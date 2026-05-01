import { createServer } from "node:http";
import type { ServerResponse } from "node:http";

import { analyzeCircular } from "./api/analyzeCircular.js";
import { searchChannelA, type SearchChannelARequest } from "./api/searchChannelA.js";
import { searchChannelB, type SearchChannelBRequest } from "./api/searchChannelB.js";
import { searchCombined, type SearchCombinedRequest } from "./api/searchCombined.js";
import { getCorsOrigin, getPort } from "./config/env.js";
import { createEmbeddingClient } from "./lib/embeddingClient.js";
import { createLlmClient } from "./lib/llmClient.js";
import type { AnalyzeCircularRequest } from "./types/knowledge.js";

const PORT = getPort();
const CORS_ORIGIN = getCorsOrigin();

function setCorsHeaders(res: ServerResponse): void {
  res.setHeader("Access-Control-Allow-Origin", CORS_ORIGIN);
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

const server = createServer(async (req, res) => {
  // Handle CORS preflight requests from the browser
  if (req.method === "OPTIONS") {
    setCorsHeaders(res);
    res.writeHead(204);
    res.end();
    return;
  }

  if (req.method === "GET" && req.url === "/health") {
    setCorsHeaders(res);
    res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" });
    res.end(JSON.stringify({ ok: true, service: "edb-knowledge-platform-backend" }));
    return;
  }

  if (req.method === "POST" && req.url === "/analyze-circular") {
    try {
      const input = await readJsonBody<AnalyzeCircularRequest>(req);
      const result = await analyzeCircular(input, { llmClient, embeddingClient });

      setCorsHeaders(res);
      res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify(result));
      return;
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      setCorsHeaders(res);
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

      setCorsHeaders(res);
      res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify(result));
      return;
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      setCorsHeaders(res);
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

      setCorsHeaders(res);
      res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify(result));
      return;
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      setCorsHeaders(res);
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

      setCorsHeaders(res);
      res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify(result));
      return;
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      setCorsHeaders(res);
      res.writeHead(400, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify({ error: message }));
      return;
    }
  }

  setCorsHeaders(res);
  res.writeHead(404, { "Content-Type": "application/json; charset=utf-8" });
  res.end(JSON.stringify({ error: "Not found" }));
});

server.listen(PORT, () => {
  console.log(`學校管理知識中心 backend listening on http://localhost:${PORT}`);
  console.log(`CORS origin: ${CORS_ORIGIN}`);
});
