# Codebase Context

## Stack
- Single-file frontend application served as static HTML
- Runtime libraries loaded from CDN: React 18.2, ReactDOM 18.2, Babel Standalone 7.23.9, Tailwind CSS 2.2.19
- Primary languages: HTML, inline JSX, CSS, embedded JSON-like data
- Hosting: GitHub Pages via `main` branch

## Directory Map
- `k1-dashboard.html` — primary application UI and embedded knowledge data
- `index.html` — redirect entry point to `k1-dashboard.html`
- `README.md` — project overview, feature summary, live demo link
- `CHANGELOG.md` — release history through `v1.3.1`
- `K1_KNOWLEDGE_INTERFACE_SPEC.md` — external data contract and validation expectations for the knowledge JSON structure
- `K1_API_SPEC.md` — public integration spec for EDB Circular System; v1.3 schema with `subject_head` + `panel_chair`
- `knowledge.json` — public API endpoint: v1.3.1 approved facts, 7 topics, `subject_head` + `panel_chair` role schema (GitHub Pages)
- `guidelines.json` — public API endpoint: 39 EDB guideline document reference links, 7 topics (GitHub Pages)
- `bump_version.py` — version bumper: patch/minor/major/set modes; syncs 6 files + CHANGELOG + README date
- `backend/` — TypeScript Knowledge Platform backend scaffold
- `backend/src/types/knowledge.ts` — backend topic/role/schema types; now accepts both legacy `department_head` and split `subject_head` + `panel_chair`
- `backend/src/services/topicDetector.ts` — keyword topic routing logic
- `backend/src/services/knowledgeSelector.ts` — role-aware approved-knowledge selection with 600-char budget; bridges legacy `department_head` and split-role schema
- `backend/src/services/promptBuilder.ts` — builds the consultative prompt with approved knowledge injection
- `backend/src/lib/embeddingClient.ts` — OpenAI `text-embedding-3-small` wrapper; exports `EmbedFn` type
- `backend/src/lib/knowledgeRepository.ts` — loads `dev/knowledge/role_facts.json` for backend use
- `backend/src/lib/llmClient.ts` — OpenAI Responses API wrapper with low-cost default model
- `backend/src/api/analyzeCircular.ts` — orchestrates detect → select → prompt → LLM flow
- `backend/src/server.ts` — minimal Node HTTP entrypoint exposing `POST /analyze-circular`
- `backend/README.md` — standalone backend runbook, env vars, API examples, and health check usage
- `dev/knowledge/role_facts.json` — JSON backup / export artifact for the dashboard knowledge dataset; currently still uses older merged `department_head` wording/schema
- `dev/SESSION_HANDOFF.md` — current operating state and next priorities
- `dev/SESSION_LOG.md` — session-by-session history and verification evidence

## Key Entry Points
- Browser entry: `index.html`
- App root: `k1-dashboard.html`
- DOM mount: `#root`
- Main dataset constant: `INITIAL_DATA`
- Review state bootstrap: `buildInitialReview(...)`

## Build & Run
- No local build step or package manager is currently required
- Local usage: open `k1-dashboard.html` directly in a browser
- Deployed usage: GitHub Pages serves `index.html`, which redirects to `k1-dashboard.html`
- Admin review persistence:
  - same-browser edits / approvals are auto-saved in `localStorage`
  - permanent cross-device persistence requires downloading the admin snapshot export and writing it back to repo
- Backend scaffold:
  - backend now accepts both legacy merged `department_head` and split `subject_head` + `panel_chair`
  - `cd backend`
  - `npm install`
  - `npm run check`
  - `npm run build`
  - `OPENAI_API_KEY=... npm run dev`
  - `curl http://localhost:8787/health`
- Baseline verification used by the project:
  - validate fact schema and counts in `dev/knowledge/role_facts.json`
  - verify JSX/bracket balance in `k1-dashboard.html`
  - keep `role_facts.json` synchronized with dashboard data after product changes
  - when public `knowledge.json` schema changes, re-check backend `types/knowledge.ts` and `knowledgeSelector.ts` for compatibility before claiming backend-ready
  - current compatibility check status: `npm run check` ✅, `npm run build` ✅ after adding split-role support

## External Services
### Hong Kong Education Bureau (EDB)
- Purpose: authoritative source for policy facts and guideline documents
- Access pattern: official EDB PDFs and web pages
- Constraints:
  - WebFetch is blocked for `www.edb.gov.hk`
  - browser-based verification is required for new source discovery
- Notes:
  - direct PDF URLs are preferred where available
  - some older EDB URLs may 404 or move during site restructuring

### GitHub / GitHub Pages
- Purpose: source control, release tags, and static site hosting
- Repo: `Leonard-Wong-Git/edb-knowledge`
- Live site: `https://leonard-wong-git.github.io/edb-knowledge/k1-dashboard.html`
- Deployment model: push to `main`, serve static assets via GitHub Pages
- Public artifacts:
  - `knowledge.json`
  - `guidelines.json`
  - `K1_API_SPEC.md`

### OpenAI API
- Purpose: (1) embedding-based semantic topic detection; (2) circular analysis generation
- Backend usage: `backend/src/lib/embeddingClient.ts` (embeddings), `backend/src/lib/llmClient.ts` (LLM)
- Embedding model: `text-embedding-3-small` (fixed in embeddingClient.ts)
- LLM default model: `gpt-5-nano` (configurable via `OPENAI_MODEL` env var)
- Notes:
  - LLM implementation targets the Responses API (`client.responses.create`)
  - Embedding implementation uses standard Embeddings API (`client.embeddings.create`)
  - Anchor embeddings (6 topics) are cached in-process after first request — no re-embedding per query

## Key Decisions
- Keep the product as a single-file dashboard to avoid introducing a build pipeline
- Store the knowledge base directly in the HTML app while maintaining a JSON sync copy for validation and handoff
- Keep review workflow in the UI so fact approval can happen without backend infrastructure
- Treat governance files as internal session state and exclude them from git
- Build the Knowledge Platform as a separate backend project under `backend/` so the GitHub Pages frontend remains untouched
- Public `knowledge.json` is now the external schema SSOT; backend compatibility must be checked whenever its role buckets change
- Backend compatibility is implemented as a bridge layer: old clients can still request `department_head`, while new split-role callers may request `subject_head` or `panel_chair`
- Dashboard UI may use split role labels and role buckets that differ from older backup/export artifacts; do not assume `dev/knowledge/role_facts.json` matches the live public schema without verification

## AI Maintenance Log
- `2026-03-17 (Codex_20260317_1941)` Generated initial `CODEBASE_CONTEXT.md` from: `README.md`, `CHANGELOG.md`, `K1_KNOWLEDGE_INTERFACE_SPEC.md`, `k1-dashboard.html`, `index.html`, `.gitignore`, `dev/knowledge/role_facts.json`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
- `2026-03-17 (Codex_20260317_1955)` Updated context after adding `backend/` scaffold with TypeScript config plus `knowledge.ts`, `topicDetector.ts`, and `knowledgeSelector.ts`
- `2026-03-17 (Codex_20260317_2001)` Updated context after adding `promptBuilder.ts`, `knowledgeRepository.ts`, `llmClient.ts`, `analyzeCircular.ts`, `server.ts`, and backend env/config files
- `2026-03-23 (Claude_20260323_1032)` Added `embeddingClient.ts`; upgraded `topicDetector.ts` to async embedding-based semantic search; added CORS to `server.ts`; added Dashboard `CircularAnalysisPanel` (4th view mode). Updated OpenAI API entry and directory map.
- `2026-04-03 (Codex_20260403_1011)` Updated context after platform version bump to `v1.0.0`; release-history summary now reflects the new milestone.
- `2026-04-04 (Codex_20260404_0834)` Updated context after aligning backend role schema to `department_head`, adding `backend/README.md`, adding `/health`, and re-running successful backend `check` + `build`
- `2026-04-08 (Codex_20260408_0905)` Updated directory map after `K1_API_SPEC.md` returned to repo root and `knowledge.json` moved to v1.3.0 split-role schema; noted that backend still expects `department_head` and needs compatibility verification.
- `2026-04-08 (Codex_20260408_0925)` Updated backend notes after adding a compatibility bridge for `department_head` plus split `subject_head` / `panel_chair`, with successful `npm run check` and `npm run build`.
- `2026-04-08 (Codex_20260408_1115)` Refreshed release-state context after `v1.3.1` push; clarified that public `knowledge.json` is split-role while local `dev/knowledge/role_facts.json` remains a merged backup/export artifact.
