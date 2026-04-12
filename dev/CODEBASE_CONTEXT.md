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
- `K1_KNOWLEDGE_INTERFACE_SPEC.md` — external data contract and validation expectations for `role_facts.json`; now v2.0.0 with `subject_head` + `panel_chair`
- `K1_API_SPEC.md` — public integration spec for EDB Circular System; v1.3.1 schema with `subject_head` + `panel_chair`
- `dev/K1_KNOWLEDGE_OPERATING_SYSTEM_PLAN.md` — agreed architecture plan (v2): LLM-wiki approach with phased delivery — source registry, fact-source traceability, freshness monitoring, and trust-gate design; full vault/wiki-unit/compile layers deferred until scale or clear utility demands them
- `dev/source/source_registry.json` — Phase 1 registry seeded with `SAG`, `Code of Aid`, existing `guidelines.json` sources, and additional statistical / curriculum source entries; also stores the current trust-gate policy
- `dev/source/FRESHNESS_GUIDE.md` — Phase 2 freshness monitoring operating rhythm and rhythm for maintenance
- `dev/vault/` — extracted-source working area for pilot LLM-wiki materials (catalogues, circular extracts, and statistical extracts); currently a bounded evidence workspace, not a full compile pipeline
- `knowledge.json` — public API endpoint: v1.3.1 approved facts, 7 topics, `subject_head` + `panel_chair` role schema (GitHub Pages)
- `guidelines.json` — public API endpoint: 39 EDB guideline document reference links, 7 topics (GitHub Pages)
- `bump_version.py` — version bumper: patch/minor/major/set modes; syncs 6 files + CHANGELOG + README date
- `backend/` — TypeScript Knowledge Platform backend scaffold
- `backend/src/types/knowledge.ts` — backend topic/role/schema types; now accepts both legacy `department_head` and split `subject_head` + `panel_chair`
- `backend/src/services/topicDetector.ts` — keyword topic routing logic
- `backend/src/services/knowledgeSelector.ts` — role-aware approved-knowledge selection with 600-char budget; bridges legacy `department_head` and split-role schema
- `backend/src/services/promptBuilder.ts` — builds the consultative prompt with approved knowledge injection
- `backend/src/lib/embeddingClient.ts` — OpenAI `text-embedding-3-small` wrapper; exports `EmbedFn` type
- `backend/src/lib/knowledgeRepository.ts` — loads repo-root `role_facts.json` for backend use; `dev/knowledge/role_facts.json` remains a legacy backup/export artifact
- `backend/src/lib/llmClient.ts` — OpenAI Responses API wrapper with low-cost default model
- `backend/src/api/analyzeCircular.ts` — orchestrates detect → select → prompt → LLM flow
- `backend/src/server.ts` — minimal Node HTTP entrypoint exposing `POST /analyze-circular`
- `backend/README.md` — standalone backend runbook, env vars, API examples, and health check usage
- `dev/knowledge/role_facts.json` — JSON backup / export artifact for the dashboard knowledge dataset; synchronized with repo-root `role_facts.json` to support systems expecting the legacy path.
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
  - `npm run regression:semantic`
  - `npm run build`
  - `OPENAI_API_KEY=... npm run dev`
  - `curl http://localhost:8787/health`
  - default backend knowledge source is repo-root `role_facts.json`; override with `KNOWLEDGE_PATH` only when intentionally testing another dataset
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
- The agreed architecture direction is LLM-wiki with phased delivery: the current facts/guidelines already form the wiki; Phase 0 fixes the backend bug, Phase 1 adds source registry + fact-source traceability, Phase 2 adds freshness monitoring, Phase 3 (scale-triggered) adds extraction assistance and optional vault/wiki-unit/compile layers. Trust is enforced by source/freshness/approval gates rather than by letting the LLM act autonomously. See `dev/K1_KNOWLEDGE_OPERATING_SYSTEM_PLAN.md` v2 for full details
- Knowledge base scope is intentionally broadened beyond the Circular analysis system. Two distinct fact types are now recognised: (1) `statistical` facts (objective numbers from verified EDB sources — auto-approvable, stored in vault, served via RAG or search-to-source) and (2) `policy` facts (interpretive role-specific guidance — human approval required, injected into Circular system prompts). The vault serves both: statistical facts feed LLM-wiki search and point users to source URLs; policy facts continue to feed `role_facts.json`
- LLM-wiki search use case: user queries → relevant vault content retrieved → user directed to original EDB source URL. No fact approval step needed for this path. `role_facts.json` injection is specific to the Circular analysis system only

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
- `2026-04-09 (Codex_20260409_0905)` Updated context after promoting `K1_KNOWLEDGE_INTERFACE_SPEC.md` to v2.0.0 and aligning it with the split-role contract (`subject_head` + `panel_chair`).
- `2026-04-09 (Codex_20260409_1135)` Added `dev/K1_KNOWLEDGE_OPERATING_SYSTEM_PLAN.md` to capture the agreed source-driven architecture direction: preserve current public interfaces, add source registry/vault, monitor `SAG` + `Code of Aid`, and support scheduled/manual ingestion.
- `2026-04-09 (Claude_20260409_0000)` Rewrote `dev/K1_KNOWLEDGE_OPERATING_SYSTEM_PLAN.md` to v2: replaced 4-layer architecture with phased LLM-wiki approach (Phase 0 fix backend → Phase 1 source registry + traceability → Phase 2 freshness monitoring → Phase 3 extraction if scale demands). Updated Key Decisions to reflect agreed direction.
- `2026-04-09 (Codex_20260409_0001)` Updated backend context after Phase 0 fix: default knowledge path now points to repo-root `role_facts.json` (split-role v2.0.0), and analyze responses now expose `similarity_scores` plus `total_fact_chars`.
- `2026-04-10 (Codex_20260410_0002)` Refined the LLM-wiki plan to clarify trust gates: source admission, freshness, fact proposal, approval, and public compilation. The intended evolution is evidence-first semi-automation, not autonomous LLM publishing.
- `2026-04-10 (Codex_20260410_0004)` Added `dev/source/source_registry.json` as the first Phase 1 artifact. Seeded `2` spine sources plus `39` existing guideline sources and recorded the first lightweight trust-gate policy in the registry itself.
- `2026-04-10 (Codex_20260410_0005)` Added backward-compatible `_source_refs` metadata to each topic block in repo-root `role_facts.json` and aligned `K1_KNOWLEDGE_INTERFACE_SPEC.md` so fact-source traceability is now documented as part of the external contract extension.
- `2026-04-10 (Claude_20260410_0006)` Registered 7 new stat sources (stat_edb_figures, stat_kg, stat_pri, stat_sec, stat_special, stat_integrated_edu, stat_enrolment_report) and built vault extracts for 5 xlsx files. Formalised two-tier fact model: statistical facts (auto-approve) vs policy facts (human-gated). Widened knowledge base scope to include LLM-wiki search path pointing users to EDB source URLs, separate from Circular system prompt injection.
- `2026-04-10 (Codex_20260410_0008)` Added Science Education curriculum-document entries under `sci_curr_docs` and created `dev/vault/science_edu_curr_docs/catalogue.json` from user-provided page content. This extends the registry/vault evidence workspace without changing any current public JSON endpoint.
- `2026-04-10 (Codex_20260410_0009)` Added Technology Education curriculum-document entries under `tech_curr_docs` and created `dev/vault/technology_edu_curr_docs/catalogue.json` from user-provided page content. This extends the registry/vault evidence workspace without changing any current public JSON endpoint.
- `2026-04-10 (Codex_20260410_0010)` Added PSHE curriculum-document entries under `pshe_curr_docs` and created `dev/vault/pshe_curr_docs/catalogue.json` from user-provided page content. This extends the registry/vault evidence workspace without changing any current public JSON endpoint.
- `2026-04-10 (Codex_20260410_0011)` Added Arts Education curriculum-document entries under `arts_curr_docs` and created `dev/vault/arts_edu_curr_docs/catalogue.json` from user-provided page content. Recorded the direct PDF URL for the 2017 Arts Education KLA guide and kept other music / visual arts files in the same registry/vault pattern.
- `2026-04-10 (Codex_20260410_0012)` Backfilled direct PDF URLs and local-file evidence for `music_p1_s6_2024`, `va_p1_s6_2024`, and `va_sss_2015` in the Arts Education registry/catalogue, reducing the number of arts entries still waiting for direct-link capture.
- `2026-04-10 (Codex_20260410_0013)` Added Physical Education curriculum-document entries under `pe_curr_docs` and created `dev/vault/pe_curr_docs/catalogue.json` from user-provided page content. Kept learning-scope / overview materials as catalogue-only while upgrading the core guide/CAG files into registry sources.
- `2026-04-10 (Codex_20260410_0015)` Backfilled the EdCity direct PDF URL and local evidence for `ict_sss_2021`, then added General Studies (`gs_pri_curr`) and Primary Humanities (`ph_pri_curr`) curriculum entries plus dedicated vault catalogues. This further extends the registry/vault evidence workspace without changing any current public JSON endpoint.
- `2026-04-10 (Codex_20260410_0017)` Expanded the Primary Science (`pri_science`) family with the official 2025 curriculum-guide PDF link, six circular / memorandum child entries, and two teacher-development documents. Synced the same structure into `dev/vault/science_edu_curr_docs/catalogue.json` and recorded local-file evidence for `PSCG(2025).pdf`.
- `2026-04-10 (Codex_20260410_0018)` Expanded `moral_civic_curr` with five core child entries for values education / moral and civic education documents and created `dev/vault/moral_civic_curr/catalogue.json`, preserving the same registry/vault pattern without changing any public JSON endpoint.
- `2026-04-10 (Codex_20260410_0020)` Added `backend/scripts/semanticRegression.ts` plus `npm run regression:semantic` to provide a reusable backend semantic regression harness. Offline regression now checks topic routing, role buckets, schema consistency, and real circular retrieval; online regression remains blocked until `OPENAI_API_KEY` is available.
- `2026-04-11 (Codex_20260411_0001)` Realigned `K1_API_SPEC.md` with the live public schema metadata (`knowledge.json` / `guidelines.json` both at `v1.3.1`) so schema-consistency regression no longer fails on stale local spec markers. Live GitHub Pages copy still requires a future push to catch up.
- `2026-04-11 (Claude_20260411_0007)` Integrated Phase 2: Created `dev/source/FRESHNESS_GUIDE.md` to document the monitoring rhythm. Backfilled 7 direct PDF URLs for Primary Science circulars in the registry. Synced root `role_facts.json` to `dev/knowledge/role_facts.json` to ensure the EDB Circular System scraper (Project-V3) sees the latest v2.0.0 facts. Ran offline semantic regression: circular samples PASS, but query routing awaits online re-verification.
- `2026-04-12 (Antigravity_20260412_1524)` Completed Phase 1 registry backfill: updated approx 23 core curriculum documents with verified direct PDF URLs for KLAs (Econ, Ethics, Geog, Art, PE, etc.). Registry is now 99% complete for core curriculum files.
