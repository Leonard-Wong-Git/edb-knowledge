/**
 * searchLog.ts — per-search log + answer feedback (S233)
 * ══════════════════════════════════════════════════════
 * The usage counter (S204) answers "how much"; nothing answered "what do users actually ask".
 * Every retrieval measurement so far ran on a hand-written gold set. This keeps each real
 * Channel B search — query, route, answer, the result window — for 180 days, and lets the
 * user rate the answer. Design and decisions: dev/SEARCH_LOG_DESIGN.md.
 *
 * Storage is `public.search_log`, written only through two SECURITY DEFINER functions
 * (`log_search`, `record_search_feedback`; DDL in backend/supabase/s233_search_log.sql),
 * exactly like `bump_usage`: the backend's anon key has EXECUTE and no table grant.
 *
 * Same two rules as usageCounter.ts:
 *
 * 1. Logging must never be able to break a search. `logSearch` is fire-and-forget and
 *    swallows its own errors.
 * 2. Our own probe traffic (PROBE_HEADER) is not logged — the caller decides, and returns
 *    no `log_id` for it, so there is nothing to rate.
 *
 * Nothing about who: no IP, cookie or user agent is passed here.
 */

import { randomUUID } from "node:crypto";
import { getSupabaseAnonKey, getSupabaseUrl } from "../config/env.js";
import type { SearchChannelBResponse } from "../api/searchChannelB.js";

const RPC_TIMEOUT_MS = 4000;

export type SearchClient = "desktop" | "mobile";

/** Accepts only the two known client labels; anything else is stored as null. */
export function parseClient(raw: unknown): SearchClient | null {
  return raw === "desktop" || raw === "mobile" ? raw : null;
}

export function newLogId(): string {
  return randomUUID();
}

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export function isLogId(raw: unknown): raw is string {
  return typeof raw === "string" && UUID_RE.test(raw);
}

export interface SearchLogEntry {
  id: string;
  query: string;
  client: SearchClient | null;
  route: string | null;
  declined: boolean;
  latencyMs: number;
  response: SearchChannelBResponse;
}

/** Build the RPC body. Exported so the shape can be checked without a network call. */
export function toLogSearchParams(entry: SearchLogEntry): Record<string, unknown> {
  const { response } = entry;
  return {
    p_id: entry.id,
    p_query: entry.query,
    p_client: entry.client,
    p_route: entry.route,
    p_declined: entry.declined,
    p_degraded: Boolean(response.degraded),
    p_synthesis: response.synthesis ?? null,
    // Chunk text is kept, not just ids: re-ingests delete and rewrite chunks (S223 dropped
    // 792 SAG rows), so an id alone would stop resolving to what the user was shown.
    p_results: (response.results ?? []).map((r) => ({
      id: r.id,
      source_id: r.source_id,
      title: r.title,
      page: r.page ?? null,
      score: r.score,
      content_type: r.content_type,
      text: r.text,
    })),
    p_total: response.total,
    p_latency_ms: Math.round(entry.latencyMs),
  };
}

async function callRpc(name: string, body: Record<string, unknown>): Promise<unknown> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), RPC_TIMEOUT_MS);
  try {
    const key = getSupabaseAnonKey();
    const res = await fetch(`${getSupabaseUrl()}/rest/v1/rpc/${name}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        apikey: key,
        Authorization: `Bearer ${key}`,
      },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    if (!res.ok) {
      throw new Error(`${name} → HTTP ${res.status} ${await res.text()}`);
    }
    const text = await res.text();
    return text ? JSON.parse(text) : null;
  } finally {
    clearTimeout(timer);
  }
}

/** Write one search. Never throws and is never awaited by the request path. */
export function logSearch(entry: SearchLogEntry): void {
  void callRpc("log_search", toLogSearchParams(entry)).catch((err) => {
    console.warn("[search-log] log_search failed (search unaffected):", String(err));
  });
}

/** Record 👍 (1) / 👎 (-1). Resolves to whether a row (≤24h old) was updated. */
export async function recordFeedback(id: string, rating: 1 | -1): Promise<boolean> {
  const result = await callRpc("record_search_feedback", { p_id: id, p_rating: rating });
  return result === true;
}
