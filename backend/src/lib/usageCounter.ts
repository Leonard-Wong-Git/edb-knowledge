/**
 * usageCounter.ts — cumulative search counter (S204)
 * ═══════════════════════════════════════════════════
 * Cloudflare Web Analytics (on index/q/app since S154) answers "who visited this week",
 * but its free tier keeps only a short rolling window, so there is no way to say how much
 * the platform has been used in total. This counts searches server-side instead: no cookie,
 * no fingerprint, nothing about who — one integer per day.
 *
 * Storage is `public.usage_daily(day date primary key, searches bigint)`. Increments go
 * through the `bump_usage()` SECURITY DEFINER function rather than a table write, so the
 * backend's key needs EXECUTE on one counter function and no write grant on any table.
 *
 * Two rules this module exists to enforce:
 *
 * 1. Counting must never be able to break a search. Every call here is fire-and-forget and
 *    swallows its own errors; a counter outage degrades to a stale number, never to a failed
 *    query.
 * 2. Our own traffic must not inflate the number. `dev/source/eval_retrieval.py` hits the
 *    live endpoint 34 times per run and the judge harness more, so a request carrying the
 *    PROBE_HEADER is served normally but not counted. Without this the total measures our
 *    test runs as much as it measures real use.
 */

import { getSupabaseAnonKey, getSupabaseUrl } from "../config/env.js";

/** Requests carrying this header are served but not counted (our own probes and evals). */
export const PROBE_HEADER = "x-probe";

const RPC_TIMEOUT_MS = 4000;

export interface UsageTotals {
  /** Searches counted since the counter was created. */
  total: number;
  /** Searches counted today (UTC, matching Postgres current_date). */
  today: number;
  /** First day with a recorded search, or null before the first one. */
  since: string | null;
}

function rpcHeaders(): Record<string, string> {
  const key = getSupabaseAnonKey();
  return {
    "Content-Type": "application/json",
    apikey: key,
    Authorization: `Bearer ${key}`,
  };
}

async function callRpc(name: string): Promise<unknown> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), RPC_TIMEOUT_MS);
  try {
    const res = await fetch(`${getSupabaseUrl()}/rest/v1/rpc/${name}`, {
      method: "POST",
      headers: rpcHeaders(),
      body: "{}",
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

/**
 * Record one search. Never throws and is never awaited by the request path — a counter
 * failure must not turn a working search into an error.
 */
export function recordSearch(isProbe: boolean): void {
  if (isProbe) return;
  void callRpc("bump_usage").catch((err) => {
    console.warn("[usage] bump_usage failed (search unaffected):", String(err));
  });
}

/** Read the totals for display. Throws on failure so the route can answer honestly. */
export async function readUsageTotals(): Promise<UsageTotals> {
  const rows = (await callRpc("get_usage_total")) as
    | { total: number | string; today: number | string; since: string | null }[]
    | null;
  const row = Array.isArray(rows) ? rows[0] : null;
  return {
    total: Number(row?.total ?? 0),
    today: Number(row?.today ?? 0),
    since: row?.since ?? null,
  };
}
