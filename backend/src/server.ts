import { createServer } from "node:http";
import type { IncomingMessage, ServerResponse } from "node:http";

import { analyzeCircular } from "./api/analyzeCircular.js";
import { searchChannelA, type SearchChannelARequest } from "./api/searchChannelA.js";
import { searchChannelB, type SearchChannelBRequest } from "./api/searchChannelB.js";
import { searchCombined, type SearchCombinedRequest } from "./api/searchCombined.js";
import { handleChunks, handleManifest } from "./api/channelBSync.js";
import { getCorsOrigins, getPort } from "./config/env.js";
import { createEmbeddingClient } from "./lib/embeddingClient.js";
import { getCacheSize, initFactEmbeddingCache, isCacheWarm } from "./lib/factEmbeddingCache.js";
import { createLlmClient } from "./lib/llmClient.js";
import type { AnalyzeCircularRequest } from "./types/knowledge.js";

const PORT = getPort();
const CORS_ORIGINS = getCorsOrigins();

// ── In-memory rate limiter ────────────────────────────────────────────────────
// 10 requests per minute per IP across all POST search/analysis endpoints.
// Uses a sliding window: each IP stores timestamps of recent requests.
const RATE_LIMIT = 10;          // max requests
const RATE_WINDOW_MS = 60_000;  // per 60 seconds

const ipWindows = new Map<string, number[]>();

// Purge stale IPs every 5 minutes to prevent unbounded memory growth
setInterval(() => {
  const cutoff = Date.now() - RATE_WINDOW_MS;
  for (const [ip, timestamps] of ipWindows) {
    const fresh = timestamps.filter(t => t > cutoff);
    if (fresh.length === 0) ipWindows.delete(ip);
    else ipWindows.set(ip, fresh);
  }
}, 5 * 60_000);

function checkRateLimit(ip: string): { allowed: boolean; retryAfterSec: number } {
  const now = Date.now();
  const cutoff = now - RATE_WINDOW_MS;
  const timestamps = (ipWindows.get(ip) ?? []).filter(t => t > cutoff);
  if (timestamps.length >= RATE_LIMIT) {
    const oldest = Math.min(...timestamps);
    const retryAfterSec = Math.ceil((oldest + RATE_WINDOW_MS - now) / 1000);
    return { allowed: false, retryAfterSec };
  }
  timestamps.push(now);
  ipWindows.set(ip, timestamps);
  return { allowed: true, retryAfterSec: 0 };
}

function getClientIp(req: import("node:http").IncomingMessage): string {
  // Respect Render's forwarded IP header; fall back to socket address
  const forwarded = req.headers["x-forwarded-for"];
  if (typeof forwarded === "string") return forwarded.split(",")[0].trim();
  return req.socket?.remoteAddress ?? "unknown";
}

function setCorsHeaders(req: IncomingMessage, res: ServerResponse): void {
  const requestOrigin = req.headers.origin;
  const allowed =
    typeof requestOrigin === "string" && CORS_ORIGINS.includes(requestOrigin)
      ? requestOrigin
      : CORS_ORIGINS[0];
  res.setHeader("Access-Control-Allow-Origin", allowed);
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  res.setHeader("Vary", "Origin");
}

function readJsonBody<T>(req: import("node:http").IncomingMessage): Promise<T> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];

    req.on("data", (chunk) => {
      chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
    });

    req.on("end", () => {
      try {
        const raw = Buffer.concat(chunks).toString("utf-8");
        resolve(JSON.parse(raw) as T);
      } catch (error) {
        reject(error);
      }
    });

    req.on("error", reject);
  });
}

// Instantiate clients once at startup (not per-request) so that the
// embedding client's module-level anchor cache is shared across requests.
const llmClient = createLlmClient();
const embeddingClient = createEmbeddingClient();

// Warm up the Channel A fact embedding cache in the background.
// Non-blocking: the first search request will fall back to batch-embed if the
// cache is not yet ready, then subsequent requests use the cache.
initFactEmbeddingCache(embeddingClient).catch((err) => {
  console.error("[startup] Channel A cache init error:", err);
});

const server = createServer(async (req, res) => {
  // Handle CORS preflight requests from the browser
  if (req.method === "OPTIONS") {
    setCorsHeaders(req, res);
    res.writeHead(204);
    res.end();
    return;
  }

  if (req.method === "GET" && req.url === "/health") {
    setCorsHeaders(req, res);
    res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" });
    res.end(JSON.stringify({
      ok: true,
      service: "edb-knowledge-platform-backend",
      cache_a: { warm: isCacheWarm(), size: getCacheSize() },
    }));
    return;
  }

  // ── Channel B incremental-sync read endpoints (Q4 Phase 2; CHANNEL_B_SYNC_SPEC.md) ──
  // X-Sync-Key gated, NO CORS (server-to-server), own rate-limit + daily budget.
  // MUST sit before the public POST 10/min limiter so sync traffic isn't choked.
  if (req.method === "GET" && req.url?.startsWith("/api/channel-b/manifest")) {
    await handleManifest(req, res);
    return;
  }
  if (req.method === "POST" && req.url === "/api/channel-b/chunks") {
    await handleChunks(req, res);
    return;
  }

  // ── Rate limiting (all POST endpoints) ───────────────────────────────────
  if (req.method === "POST") {
    const ip = getClientIp(req);
    const { allowed, retryAfterSec } = checkRateLimit(ip);
    if (!allowed) {
      setCorsHeaders(req, res);
      res.setHeader("Retry-After", String(retryAfterSec));
      res.writeHead(429, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify({
        error: "請求過於頻繁，請稍後再試。",
        retry_after_sec: retryAfterSec,
      }));
      return;
    }
  }

  if (req.method === "POST" && req.url === "/analyze-circular") {
    try {
      const input = await readJsonBody<AnalyzeCircularRequest>(req);
      const result = await analyzeCircular(input, { llmClient, embeddingClient });

      setCorsHeaders(req, res);
      res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify(result));
      return;
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      setCorsHeaders(req, res);
      res.writeHead(400, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify({ error: message }));
      return;
    }
  }

  // ── Channel A search (approved policy facts) ─────────────────────────────
  if (req.method === "POST" && req.url === "/api/search/channel-a") {
    try {
      const input = await readJsonBody<SearchChannelARequest>(req);
      const result = await searchChannelA(input, embeddingClient, llmClient);

      setCorsHeaders(req, res);
      res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify(result));
      return;
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      setCorsHeaders(req, res);
      res.writeHead(400, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify({ error: message }));
      return;
    }
  }

  // ── Channel B search (LLM-wiki index, all results) ────────────────────────
  if (req.method === "POST" && req.url === "/api/search/channel-b") {
    try {
      const input = await readJsonBody<SearchChannelBRequest>(req);
      const result = await searchChannelB(input, embeddingClient, llmClient);

      setCorsHeaders(req, res);
      res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify(result));
      return;
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      setCorsHeaders(req, res);
      res.writeHead(400, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify({ error: message }));
      return;
    }
  }

  // ── Combined A+B search ───────────────────────────────────────────────────
  if (req.method === "POST" && req.url === "/api/search/combined") {
    try {
      const input = await readJsonBody<SearchCombinedRequest>(req);
      const result = await searchCombined(input, embeddingClient, llmClient);

      setCorsHeaders(req, res);
      res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify(result));
      return;
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      setCorsHeaders(req, res);
      res.writeHead(400, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify({ error: message }));
      return;
    }
  }

  setCorsHeaders(req, res);
  res.writeHead(404, { "Content-Type": "application/json; charset=utf-8" });
  res.end(JSON.stringify({ error: "Not found" }));
});

server.listen(PORT, () => {
  console.log(`學校管理知識中心 backend listening on http://localhost:${PORT}`);
  console.log(`CORS origins: ${CORS_ORIGINS.join(", ")}`);
});
