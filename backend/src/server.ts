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

  // ── Temporary diagnostic endpoint ────────────────────────────────────────
  if (req.method === "GET" && req.url === "/debug-b") {
    try {
      const supabaseUrl = process.env.SUPABASE_URL ?? "";
      const supabaseKey = process.env.SUPABASE_ANON_KEY ?? "";

      // 1. Direct table query (no vector)
      const tableResp = await fetch(
        `${supabaseUrl}/rest/v1/wiki_chunks?select=id,text&limit=2`,
        { headers: { apikey: supabaseKey, Authorization: `Bearer ${supabaseKey}` } }
      );
      const tableData = await tableResp.json();

      // 2. RPC with a simple unit vector [1,0,0,...,0]
      const unitVec = `[1${",0".repeat(1535)}]`;
      const rpcResp = await fetch(`${supabaseUrl}/rest/v1/rpc/match_wiki_chunks`, {
        method: "POST",
        headers: {
          apikey: supabaseKey,
          Authorization: `Bearer ${supabaseKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query_embedding: unitVec, match_threshold: 0.0, match_count: 3 }),
      });
      const rpcStatus = rpcResp.status;
      const rpcText = await rpcResp.text();

      setCorsHeaders(res);
      res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify({
        table_status: tableResp.status,
        table_rows: tableData,
        rpc_status: rpcStatus,
        rpc_preview: rpcText.slice(0, 300),
      }));
    } catch (err) {
      setCorsHeaders(res);
      res.writeHead(500, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify({ error: String(err) }));
    }
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
      const result = await searchChannelA(input, embeddingClient);

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
