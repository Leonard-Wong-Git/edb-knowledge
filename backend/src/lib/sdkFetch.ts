import nodeFetch from "node-fetch";
import type { ClientOptions } from "openai";

/**
 * Shared HTTP fetch for the OpenAI SDK clients.
 *
 * S173 production incident: on Render, Node's bundled native fetch (undici)
 * began failing EVERY OpenAI call with `Invalid response body while trying to
 * fetch https://api.openai.com/v1/embeddings: Premature close` — undici reused a
 * keep-alive connection that OpenAI's edge had already closed, and the failure
 * persisted across service restarts (the startup Channel-A cache warmed 0/455).
 * The same API key + same code embedded fine from other egress (verified live,
 * HTTP 200), isolating the fault to undici keep-alive on Render's network — not
 * the key, billing, OpenAI, or app code.
 *
 * node-fetch (already a dependency) does not pool keep-alive connections by
 * default — it opens a fresh connection per request — so it sidesteps the stale
 * keep-alive "Premature close". Injected into BOTH OpenAI clients (embeddings +
 * LLM) so every OpenAI call uses the resilient path. node-fetch v3 is API-compatible
 * with the WHATWG fetch the SDK expects; bridge the Request/Response types through
 * the SDK's own ClientOptions["fetch"] shape.
 */
export const sdkFetch = nodeFetch as unknown as ClientOptions["fetch"];
