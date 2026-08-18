import { createServer } from "node:http";
import type { IncomingMessage, ServerResponse } from "node:http";

import { analyzeCircular } from "./api/analyzeCircular.js";
import {
  analyzeDocument,
  MAX_TEXT_CHARS,
  type AnalyzeDocumentRequest,
} from "./api/analyzeDocument.js";
import {
  checklistRevise,
  listChecklistDomains,
  type ChecklistReviseRequest,
} from "./api/checklistRevise.js";
import {
  annotateDocument,
  type AnnotateDocumentRequest,
} from "./api/annotateDocument.js";
import { searchChannelA, type SearchChannelARequest } from "./api/searchChannelA.js";
import { searchChannelB, type SearchChannelBRequest } from "./api/searchChannelB.js";
import { PROBE_HEADER, readUsageTotals, recordSearch } from "./lib/usageCounter.js";
import { searchCombined, type SearchCombinedRequest } from "./api/searchCombined.js";
import { handleChunks, handleManifest } from "./api/channelBSync.js";
import { getCorsOrigins, getPort } from "./config/env.js";
import { createEmbeddingClient } from "./lib/embeddingClient.js";
import { getCacheSize, initFactEmbeddingCache, isCacheWarm } from "./lib/factEmbeddingCache.js";
import { createLlmClient } from "./lib/llmClient.js";
import type { AnalyzeCircularRequest } from "./types/knowledge.js";

const PORT = getPort();
const CORS_ORIGINS = getCorsOrigins();

// Body-size cap for the search routes (S187 audit). Queries are short; this
// blocks oversized POST bodies that would otherwise buffer unbounded in memory
// (Buffer.concat) before reaching the handler. The analyze-* routes keep their
// larger MAX_TEXT_CHARS-based cap because they carry full document text.
const SEARCH_MAX_BYTES = 16_384; // 16 KB

// ── In-memory rate limiter ────────────────────────────────────────────────────
// 10 requests per minute per IP across all POST search/analysis endpoints.
// Uses a sliding window: each IP stores timestamps of recent requests.
const RATE_LIMIT = 10;          // max requests per IP
const RATE_WINDOW_MS = 60_000;  // per 60 seconds

// Global backstop ceiling across ALL clients on the OpenAI-billing POST routes.
// Defense-in-depth against denial-of-wallet (S187 audit): even if per-IP keying
// is defeated (header spoofing, botnet), total OpenAI spend per window is
// hard-capped. Sized well above realistic concurrent legitimate use
// (12 distinct IPs at the full 10/min each).
const GLOBAL_RATE_LIMIT = 120; // max total requests per window across all IPs

const ipWindows = new Map<string, number[]>();
const globalWindow: number[] = [];

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

// Global ceiling across all clients (denial-of-wallet backstop, S187).
function checkGlobalLimit(): { allowed: boolean; retryAfterSec: number } {
  const now = Date.now();
  const cutoff = now - RATE_WINDOW_MS;
  while (globalWindow.length > 0 && globalWindow[0] <= cutoff) globalWindow.shift();
  if (globalWindow.length >= GLOBAL_RATE_LIMIT) {
    const retryAfterSec = Math.ceil((globalWindow[0] + RATE_WINDOW_MS - now) / 1000);
    return { allowed: false, retryAfterSec };
  }
  globalWindow.push(now);
  return { allowed: true, retryAfterSec: 0 };
}

function getClientIp(req: import("node:http").IncomingMessage): string {
  // Render terminates the connection at its own proxy and APPENDS the real
  // client IP as the LAST entry of X-Forwarded-For. The leftmost entries are
  // client-supplied and therefore spoofable — keying the rate limiter on
  // split(",")[0] let an attacker rotate the header for a fresh bucket per fake
  // IP (denial-of-wallet, S187 audit). Use the RIGHTMOST hop (the value the
  // trusted proxy observed) instead; fall back to the socket address.
  const forwarded = req.headers["x-forwarded-for"];
  if (typeof forwarded === "string" && forwarded.trim()) {
    const hops = forwarded.split(",").map((s) => s.trim()).filter(Boolean);
    if (hops.length > 0) return hops[hops.length - 1];
  }
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

function readJsonBody<T>(
  req: import("node:http").IncomingMessage,
  maxBytes?: number
): Promise<T> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    let received = 0;

    req.on("data", (chunk) => {
      const buf = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk);
      received += buf.length;
      if (maxBytes !== undefined && received > maxBytes) {
        // Stop buffering and drain the rest so the 413 response can still be
        // written on this socket (req.destroy() here would RST before the
        // client sees any response).
        req.removeAllListeners("data");
        req.removeAllListeners("end");
        req.resume();
        reject(new Error("PAYLOAD_TOO_LARGE"));
        return;
      }
      chunks.push(buf);
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
  // ── Channel A retirement probe (S198, TEMPORARY — delete once decided) ────
  // Question: does anything outside this repo still call the two Channel A
  // routes? It cannot be read off Render's logs as they stand — per-request
  // logging is a Pro-plan feature (https://render.com/docs/logging), so on this
  // Hobby instance "nobody calls this route" and "this route never prints"
  // produce the identical empty search. Verified S198: a /health request known
  // to have been made was equally absent from a dashboard search for "health",
  // while a startup console.log from this file was found — stdout is captured,
  // request paths are not. This closes the gap for these two paths only.
  // Placed above the OPTIONS branch and the POST rate limiter on purpose, so a
  // browser preflight or a throttled caller still registers. Headers only —
  // never the body, which carries user query text. Hobby log retention is 7
  // days, so the window must be read before it expires.
  //
  // Logs the WHOLE X-Forwarded-For chain, deliberately not getClientIp(). That
  // helper takes the rightmost hop because a rate limiter must not key on a
  // spoofable value (S187), but measured here the rightmost hop is a Render
  // internal proxy address (10.x) and identifies nobody. The question this
  // probe asks is "who is calling", not "who do I throttle", and the window is
  // seven days and unrepeatable — so record the full chain and judge it when
  // read. The leftmost entry is client-supplied and must be treated as a claim,
  // not a fact. getClientIp and the rate limiter are untouched.
  if (req.url === "/api/search/channel-a" || req.url === "/api/search/combined") {
    console.log(
      `[route-probe] ${req.method} ${req.url}` +
        ` origin=${req.headers.origin ?? "-"}` +
        ` ua=${String(req.headers["user-agent"] ?? "-").slice(0, 120)}` +
        ` xff=${String(req.headers["x-forwarded-for"] ?? "-").slice(0, 200)}` +
        ` peer=${req.socket?.remoteAddress ?? "-"}`,
    );
  }

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

  // ── Cumulative usage counter (GET, no rate limit) ─────────────────────────
  // Cloudflare Web Analytics only keeps a short rolling window; this is the running total.
  if (req.method === "GET" && req.url === "/api/stats/usage") {
    setCorsHeaders(req, res);
    try {
      const totals = await readUsageTotals();
      res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify({ ok: true, ...totals }));
    } catch (error) {
      // The counter is decoration, not a contract — report the failure rather than
      // inventing a number the caller would render as fact.
      const message = error instanceof Error ? error.message : "Unknown error";
      res.writeHead(503, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify({ ok: false, error: message }));
    }
    return;
  }

  // ── 文件修訂: checklist domain list for the frontend selector (GET, no rate limit) ──
  if (req.method === "GET" && req.url === "/api/checklist-domains") {
    setCorsHeaders(req, res);
    try {
      res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify({ ok: true, domains: listChecklistDomains() }));
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      res.writeHead(500, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify({ error: message }));
    }
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
    const perIp = checkRateLimit(ip);
    const global = perIp.allowed ? checkGlobalLimit() : { allowed: true, retryAfterSec: 0 };
    if (!perIp.allowed || !global.allowed) {
      const retryAfterSec = !perIp.allowed ? perIp.retryAfterSec : global.retryAfterSec;
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

  // ── 文件分析: per-segment guideline matching for user-uploaded documents ──
  // Body cap: MAX_TEXT_CHARS chars of (possibly multi-byte) text + JSON overhead.
  // Only this endpoint passes a cap — existing endpoints keep prior behavior.
  if (req.method === "POST" && req.url === "/api/analyze-document") {
    try {
      const input = await readJsonBody<AnalyzeDocumentRequest>(req, MAX_TEXT_CHARS * 4 + 4096);
      const result = await analyzeDocument(input, { embeddingClient, llmClient });

      setCorsHeaders(req, res);
      res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify(result));
      return;
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      setCorsHeaders(req, res);
      const status = message === "PAYLOAD_TOO_LARGE" ? 413 : 400;
      res.writeHead(status, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify({
        error: status === 413 ? "上載內容過大，請分批分析。" : message,
      }));
      return;
    }
  }

  // ── 文件修訂: compare an uploaded document against a domain's compliance checklist ──
  // Same body cap + rate limiter as 文件分析; embedding-only coverage (no LLM).
  if (req.method === "POST" && req.url === "/api/checklist-revise") {
    try {
      const input = await readJsonBody<ChecklistReviseRequest>(req, MAX_TEXT_CHARS * 4 + 4096);
      const result = await checklistRevise(input, { embeddingClient });

      setCorsHeaders(req, res);
      res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify(result));
      return;
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      setCorsHeaders(req, res);
      const status = message === "PAYLOAD_TOO_LARGE" ? 413 : 400;
      res.writeHead(status, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify({
        error: status === 413 ? "上載內容過大，請分批處理。" : message,
      }));
      return;
    }
  }

  // ── 文件標註: merged guideline-match + checklist-gap, returns findings[] the
  // client uses to highlight + comment the ORIGINAL docx in place ──
  // Same body cap + rate limiter as 文件分析/文件修訂.
  if (req.method === "POST" && req.url === "/api/annotate-document") {
    try {
      const input = await readJsonBody<AnnotateDocumentRequest>(req, MAX_TEXT_CHARS * 4 + 4096);
      const result = await annotateDocument(input, { embeddingClient, llmClient });

      setCorsHeaders(req, res);
      res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify(result));
      return;
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      setCorsHeaders(req, res);
      const status = message === "PAYLOAD_TOO_LARGE" ? 413 : 400;
      res.writeHead(status, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify({
        error: status === 413 ? "上載內容過大，請分批處理。" : message,
      }));
      return;
    }
  }

  if (req.method === "POST" && req.url === "/analyze-circular") {
    try {
      const input = await readJsonBody<AnalyzeCircularRequest>(req, MAX_TEXT_CHARS * 4 + 4096);
      const result = await analyzeCircular(input, { llmClient, embeddingClient });

      setCorsHeaders(req, res);
      res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify(result));
      return;
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      setCorsHeaders(req, res);
      const status = message === "PAYLOAD_TOO_LARGE" ? 413 : 400;
      res.writeHead(status, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify({
        error: status === 413 ? "上載內容過大，請分批處理。" : message,
      }));
      return;
    }
  }

  // ── Channel A search (approved policy facts) ─────────────────────────────
  if (req.method === "POST" && req.url === "/api/search/channel-a") {
    try {
      const input = await readJsonBody<SearchChannelARequest>(req, SEARCH_MAX_BYTES);
      const result = await searchChannelA(input, embeddingClient, llmClient);

      setCorsHeaders(req, res);
      res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify(result));
      return;
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      setCorsHeaders(req, res);
      const status = message === "PAYLOAD_TOO_LARGE" ? 413 : 400;
      res.writeHead(status, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify({
        error: status === 413 ? "查詢內容過大。" : message,
      }));
      return;
    }
  }

  // ── Channel B search (LLM-wiki index, all results) ────────────────────────
  if (req.method === "POST" && req.url === "/api/search/channel-b") {
    try {
      const input = await readJsonBody<SearchChannelBRequest>(req, SEARCH_MAX_BYTES);
      const result = await searchChannelB(input, embeddingClient, llmClient);
      recordSearch(Boolean(req.headers[PROBE_HEADER]));

      setCorsHeaders(req, res);
      res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify(result));
      return;
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      setCorsHeaders(req, res);
      const status = message === "PAYLOAD_TOO_LARGE" ? 413 : 400;
      res.writeHead(status, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify({
        error: status === 413 ? "查詢內容過大。" : message,
      }));
      return;
    }
  }

  // ── Combined A+B search ───────────────────────────────────────────────────
  if (req.method === "POST" && req.url === "/api/search/combined") {
    try {
      const input = await readJsonBody<SearchCombinedRequest>(req, SEARCH_MAX_BYTES);
      const result = await searchCombined(input, embeddingClient, llmClient);

      setCorsHeaders(req, res);
      res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify(result));
      return;
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      setCorsHeaders(req, res);
      const status = message === "PAYLOAD_TOO_LARGE" ? 413 : 400;
      res.writeHead(status, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify({
        error: status === 413 ? "查詢內容過大。" : message,
      }));
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
