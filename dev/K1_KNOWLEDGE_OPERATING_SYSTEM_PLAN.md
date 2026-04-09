# K1 Knowledge Operating System v2

Last updated: 2026-04-09
Status: agreed direction — ready for implementation
Scope: source-driven knowledge operations using LLM-wiki mental model, phased delivery

## 1. Purpose

The K1 EDB Knowledge Platform evolves from a hand-maintained knowledge base into a sustainable knowledge operating system using the **LLM-wiki** concept as its unifying mental model.

The existing 107 facts and 39 guideline links already form a wiki. Each fact is a wiki entry tagged by topic and role. What the wiki currently lacks is **source traceability** (where did each fact come from?) and **freshness tracking** (is the source still current?).

This plan adds those capabilities incrementally, without building infrastructure ahead of demand.

## 2. Non-goals

This plan does not propose:

- changing `knowledge.json`, `guidelines.json`, or `role_facts.json` public contracts
- removing the existing backend `POST /analyze-circular` endpoint
- turning the K1 repo into a request-time heavy RAG portal
- shipping a new UI structure in any current phase
- building a vault filesystem, compile pipeline, or wiki unit schema before scale demands it

`通告分析` is not the main product surface. The core product remains the knowledge base itself.

## 3. Design Principles

1. **Source first, facts second** — facts should be traceable to verified official sources.
2. **Compile-time intelligence, runtime simplicity** — token-heavy work happens during source ingestion, not on every user query.
3. **Public contracts stay stable** — internal structure can evolve without breaking downstream consumers.
4. **Manual override is a feature** — some EDB resources require login or operator access. The system supports this explicitly.
5. **Build what's useful now, defer what's not** — every new file or structure must deliver immediate value. Empty infrastructure is waste.
6. **The wiki already exists** — the current facts/guidelines ARE the wiki. Add source citations and freshness, don't rebuild from scratch.

## 4. Current State (as of 2026-04-09)

- 107 facts across 7 topics, 8+ roles — all approved
- 39 guideline document links in `guidelines.json`
- Public JSON contracts: `knowledge.json`, `guidelines.json`, `role_facts.json`
- Backend: TypeScript, local-only, OpenAI embedding + LLM
- **CRITICAL bug**: backend reads wrong `role_facts.json` (v1.3.1 merged schema instead of v2.0.0 split-role)
- Dashboard: single-file HTML, React 18 + Babel + Tailwind CDN

## 5. Key Source Spines

Two source families are system-level spines — higher priority than ordinary references.

### 5.1 School Administration Guide (SAG)

- Landing: `https://www.edb.gov.hk/tc/sch-admin/regulations/sch-admin-guide/index.html`
- PDF: `https://www.edb.gov.hk/attachment/tc/sch-admin/regulations/sch-admin-guide/SAG_C_markup.pdf`
- Role: primary operations spine; yearly update anchor; chapter-level routing for finance, student, activity, and general governance

### 5.2 Code of Aid / 資助則例

- Landing: `https://www.edb.gov.hk/tc/sch-admin/regulations/codes-of-aid/index.html`
- IMC version: `https://www.edb.gov.hk/tc/sch-admin/regulations/codes-of-aid/code-of-aid-and-related-documents-for-aided-imc-schools/index.html`
- PDF: `https://www.edb.gov.hk/attachment/sc/sch-admin/regulations/codes-of-aid/code-of-aid-and-related-documents-for-aided-imc-schools/coa_chinese_1.19.pdf`
- Role: compliance spine; high-authority source for finance, HR, appointment, governance, and school administration controls

## 6. Implementation Phases

### Phase 0 — Fix what's broken (prerequisite)

**Trigger:** immediate — must complete before any new architecture work.

**Deliverables:**

1. Fix backend data source path — update `DEFAULT_KNOWLEDGE_PATH_SETTING` in `backend/src/config/env.ts` to point to repo-root `role_facts.json` (v2.0.0 split-role). Run `npm run check`. Verify `subject_head` and `panel_chair` return distinct facts.
2. Add `similarity_scores` + `total_fact_chars` to the backend `AnalyzeCircularResponse` — already computed internally, just type change + passthrough.
3. Browser hard-refresh the 4 public K1 URLs to confirm v1.3.1 is live.

**Exit criteria:** backend compiles clean, role differentiation works, live URLs verified.

### Phase 1 — Source Registry + Fact-Source Mapping

**Trigger:** after Phase 0 is complete.

**Deliverables:**

1. **`dev/source/source_registry.json`** — a single JSON file cataloging every known EDB source.

   Per-source fields:
   ```
   source_id        — unique identifier (e.g. "sag_2025_11")
   title            — Chinese title
   title_en         — English title (optional)
   url_landing      — index/landing page URL
   url_primary      — direct document URL (PDF or specific page)
   source_type      — "pdf" | "html" | "index"
   authority        — "edb" | "other"
   spine            — true for SAG and Code of Aid
   topic_tags       — array of topic IDs this source covers
   access_mode      — "public" | "login_required" | "manual_only"
   status           — "candidate" | "verified" | "blocked" | "superseded"
   version_label    — human-readable version (e.g. "2025-11", "1.19")
   last_checked_at  — ISO date of last verification
   supersedes       — source_id of previous version, or null
   notes            — free text
   ```

2. **`_source_refs` field in `role_facts.json`** — added to each topic block, listing which `source_id` entries the facts in that block derive from. Uses `_` prefix so downstream consumers ignore it — no public contract change.

   Example:
   ```json
   "finance": {
     "_source_refs": ["sag_2025_11", "coa_1_19", "g01_procurement_guidelines"],
     "_label": "財務 / 採購 / 津貼 / 撥款",
     ...
   }
   ```

3. **Seed the registry** with SAG, Code of Aid, and the ~15 EDB documents already referenced in `guidelines.json`.

**What this phase does NOT build:** no vault directories, no wiki unit schema, no compile pipeline, no new scripts.

**Exit criteria:** every fact in every topic block can be traced to at least one source; every spine source has a registry entry with `last_checked_at`.

### Phase 2 — Source Freshness Monitoring

**Trigger:** Phase 1 is stable and the operator has used the registry for at least one manual review cycle.

**Deliverables:**

1. **`dev/source/check_freshness.py`** (or `.ts`) — a simple script that:
   - Reads `source_registry.json`
   - For each `status: "verified"` + `access_mode: "public"` entry, sends a HEAD request
   - Compares `Last-Modified` / `Content-Length` against stored values
   - Outputs a human-readable report: "these sources may have changed"
   - Updates `last_checked_at` in the registry

2. **Login-gated source convention** — for `access_mode: "login_required"` entries, the `notes` field records check interval and manual procedure. No automation — matches how the operator actually works.

3. **Optional: scheduled run** — if the operator wants, the script can run on a cron or GitHub Action schedule and open an issue when changes are detected.

**Exit criteria:** operator can run one command to know which sources need re-checking.

### Phase 3 — Extraction Assistance (scale-triggered)

**Trigger condition:** the knowledge base grows past ~250 facts or 12+ topics, AND manual curation becomes a bottleneck.

**Deliverables (build only what's needed):**

1. **LLM-assisted fact extraction** — use the existing OpenAI integration to suggest new facts from a source PDF. The LLM proposes; the human reviews and approves.
2. **Structured diff reports** — when a spine source updates (e.g. SAG 2026 vs SAG 2025), generate a section-level diff highlighting what changed.
3. **Source vault for extracted text** — at this scale, storing extracted plain text alongside the registry entry makes sense. Structure: `dev/source/vault/<source_id>/extract.txt`.
4. **Knowledge wiki units** (if needed) — structured intermediate representation between raw source text and compiled JSON. Only if the fact count and source count justify the indirection.
5. **Compile pipeline** (if needed) — automated generation of `knowledge.json`, `guidelines.json`, `role_facts.json` from wiki units. Only if manual compilation can no longer keep up.

**This phase may never be needed** for a school administration knowledge base maintained by one person. The original 4-layer architecture (source registry → source vault → knowledge wiki → compiled output) lives here as a reference design to draw from if scale demands it.

## 7. Runtime Strategy

Unchanged from current approach:

- Topic detection: lightweight embedding-based (text-embedding-3-small)
- Fact selection: deterministic role-aware selection with 600-char budget
- Prompt assembly: compact consultative framing
- LLM: small model (gpt-5-nano default)
- Public interface: precompiled JSON, no request-time retrieval

## 8. Standalone Product Shape

The system continues to work as a standalone knowledge platform across desktop, tablet, and phone:

- Knowledge base browsing (core product)
- Source-linked guideline library
- Lightweight search
- Admin review
- Export / status visibility

## 9. Migration from v1 Plan

The previous `K1_KNOWLEDGE_OPERATING_SYSTEM_PLAN.md` (v1) proposed a 4-layer architecture. After review, the agreed direction is:

- **Keep** all design principles (source-first, compile-time intelligence, interface stability, manual override)
- **Keep** the 4-layer architecture as a reference design for Phase 3+
- **Simplify** the immediate implementation to Phase 0 → 1 → 2, delivering source traceability and freshness monitoring without premature infrastructure
- **Defer** vault, wiki units, and compile pipeline until scale demands them

The LLM-wiki mental model unifies both approaches: the current facts already are the wiki; the phases add source citations (Phase 1) and freshness tracking (Phase 2) to make it a proper source-driven wiki.
