/**
 * _s250_localServer.ts — run the backend locally for a before/after retrieval eval.
 * backend/.env holds no anon key, so the service key stands in for it (same convention
 * as routeFirstProbe.ts). NOTE the measurement caveat that comes with it: service_role
 * has an 8 s statement_timeout where production's anon has 3 s, so timeouts are
 * under-reported here — compare result SETS from this server, not error rates.
 *
 *   cd backend && npx tsx --env-file=.env scripts/_s250_localServer.ts
 */
process.env.SUPABASE_ANON_KEY ||= process.env.SUPABASE_SERVICE_KEY;
process.env.SUPABASE_URL ||= "https://youkcekbrbywuqjxgibe.supabase.co";
process.env.FEATURE_ROUTE_FIRST_SEARCH = "1";
process.env.FEATURE_CIRCULAR_NUMBER_LOOKUP = "1";
await import("../src/server.js");
