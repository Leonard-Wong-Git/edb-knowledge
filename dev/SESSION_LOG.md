# Session Log

<!-- Archives: dev/archive/ — entries moved when >400 lines or oldest entry >30 days -->

## 2026-04-20 Session 80 — EDB Design System + Governance Install + Frontend Pages

1. Agent & Session ID: Claude_20260420_1430
2. Task summary: Applied EDB design system (米白+深綠+磚黃 palette, de-AI-ified) across all frontend pages. Built t-purchase.html (S3 Template Detail + Form) and q.html (S6 Quick Q&A). Replaced index.html with new EDB S1 Home. Retrofitted app.html CSS tokens and replaced ~40 hardcoded hex values. Installed AGENTS.md governance framework. Deleted landing.html and k1-wiki.html. Merged branch to main.
3. Layer classification: Product / UI Layer + Development Governance Layer
4. Files changed:
   - `index.html` — REPLACED: new EDB S1 Home (⌘K → q.html; stats rail from knowledge.json; template cards → t-purchase.html; A/B/AB toggle; 米白+深綠+磚黃)
   - `t-purchase.html` — NEW: S3 Template Detail + Requirements Form (split grid; live validation; skeleton preview; source control radio group)
   - `q.html` — NEW: S6 Quick Q&A (⌘K modal fallback; idle/answer/no-confident-answer states; Esc→index.html; URL hash prefill)
   - `app.html` — MODIFIED: full `:root` EDB token retrofit + legacy alias remap (--cd/--mocha/--charcoal → new tokens); ~40 hardcoded hex → CSS vars; Noto Sans HK + IBM Plex Mono fonts
   - `dev/design/Spec.html`, `dev/design/Preview.html`, `dev/design/Prototype.html` — NEW: design reference files archived
   - `AGENTS.md` — NEW: governance SSOT (from INIT.md)
   - `CLAUDE.md` — NEW: `@AGENTS.md` bridge for Claude Code
   - `GEMINI.md` — NEW: `@./AGENTS.md` bridge for Gemini CLI
   - `dev/DOC_SYNC_CHECKLIST.md` — MODIFIED: added session-log maintenance utility row
   - `docs/qa/session_log_maintenance.py` — NEW: §4a archive utility (--check / --apply / --self-test)
   - `dev/init_backup/20260420_133806/` — NEW: backup snapshot of pre-install governance files
   - `landing.html` — DELETED
   - `k1-wiki.html` — DELETED
5. Completed:
   - ✅ EDB design tokens: `--paper:#F7F4ED`, `--edb:#1F3A2E`, `--edb-2:#2E5A46`, `--accent:#8B6B2E`; radius 2px; Noto Sans HK + IBM Plex Mono
   - ✅ index.html: S1 Home — omni search → q.html; ⌘K shortcut; 5 TemplateCard grid; stats rail (fetch knowledge.json); two-col recent updates + drafts; `--rule` CSS var per card topic colour
   - ✅ t-purchase.html: S3 — RequirementField form (4 required + 2 optional fields); live validation; disabled submit until 4 fields filled; skeleton preview §1–§5 + cite count; source radio (A/B/AB)
   - ✅ q.html: S6 — autofocus input; suggestion grid (intent badges); inline citation `<sup>`; source ledger; no-confident-answer regex `/校工|合約|年假/`; Esc to home; ?q= hash prefill
   - ✅ app.html token retrofit: `:root` block fully replaced; legacy alias remapping preserves all existing JSX `style={{}}` values without markup changes
   - ✅ app.html hex audit: ~40 hardcoded hex values replaced with CSS vars (mocha browns, text colours, borders, success greens, error reds, wash backgrounds, Tailwind greys)
   - ✅ AGENTS.md governance install: §0–§12 rules; backup snapshot; root safety checks passed
   - ✅ Merged branch `claude/happy-ride-96c28f` directly to `main` (no PR)
6. Pending:
   - S4 Generation Progress screen (t-purchase.html "生成" button stubs with alert)
   - S5 Draft Canvas
   - Phase 3: 知識提煉 left-right split panel (deferred from Session 79)
   - Circular System: edb_scraper.py `_write_policy_signal()` (deferred from Session 79)
7. Doc Sync: Change category = "Backend README / standalone runbook added" → N/A (no runbook this session). Session-log maintenance utility — AGENTS.md §4a already present; docs/qa/run_checks.sh — not present (no action). DOC_SYNC_CHECKLIST.md row already merged.

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| New governance file added to install | §5a backup list in AGENTS.md; INIT.md FILE 1 §5a; INIT.md ROOT SAFETY CHECK | N/A — INIT.md is upstream, not local; AGENTS.md §5a backup list updated ✓ |
| Session-log maintenance utility added/changed | AGENTS.md §4a mechanism enforcement; README safeguards; docs/qa/run_checks.sh | AGENTS.md §4a present ✓; README not updated (not user-facing); run_checks.sh not present — skip |
| Product behavior / tuning change | SESSION_HANDOFF.md baseline; SESSION_LOG.md task entry + QC evidence | ✓ Done (this entry) |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current state: v1.6.0. EDB design system applied across all frontend pages. New pages: t-purchase.html (S3) + q.html (S6). Governance (AGENTS.md) installed. Branch merged to main.
- index.html = EDB S1 Home (⌘K → q.html; stats rail; template cards)
- t-purchase.html = S3 Template Detail + Requirements Form
- q.html = S6 Quick Q&A (⌘K modal fallback)
- app.html = full React SPA with EDB token system (1,001 facts, Channel A/B/A+B)
- Knowledge base: 1,001 approved facts, 7 topics, wiki_index 2,874 chunks

Pending tasks in priority order:
1. S4 Generation Progress screen (t-purchase.html "生成" stub → build progress/result page)
2. S5 Draft Canvas
3. Phase 3: 知識提煉 left-right split panel redesign in app.html (deferred)
4. Circular System: edb_scraper.py _write_policy_signal() implementation (deferred from Session 79)

Key files changed this session: index.html, t-purchase.html (new), q.html (new), app.html, AGENTS.md (new), dev/design/ (new), docs/qa/session_log_maintenance.py (new)

Known risks:
- Channel A searchChannelA.ts embeds ALL 1,001 facts per query — monitor token usage
- Channel B/A+B requires local backend (npm run dev) — not on GitHub Pages
- S4/S5 not yet built — t-purchase.html "生成" button currently stubs with alert()
- session_log_maintenance.py --apply has parser edge cases (entry_count=0 bug); archiving done manually this session

Post-startup first action: Confirm with user whether to build S4 Generation Progress, S5 Draft Canvas, or other priority work first.
```

---

## 2026-04-17 Session 76 — Channel B 全面除錯 + 18 個新 Extract + wiki_index 重建

1. Agent & Session ID: Claude_20260417_0001
2. Task summary: Fixed Channel B end-to-end (CORS/path/env bugs), added LLM synthesis + statistical filtering + text cleaning + page numbers + SourcesAccordion to frontend. Added A+B synthesis. Extracted SAG Ch2/4/5 + edbc12_2025_ph_pri for Channel A. Rebuilt wiki_index (1,235 chunks). Batch-extracted 18 new source PDFs via pdftotext. Channel A 6/148 sources done; user approved candidates.
3. Layer classification: Pipeline / UI Layer / Bug Fix
4. Files changed:
   - `backend/.env` — MODIFIED: added CORS_ORIGIN=* for local file:// dev
   - `backend/package.json` — MODIFIED: dev script uses `tsx --env-file=.env` (Node v24 native .env loading)
   - `backend/src/lib/wikiRepository.ts` — FIXED: path had 4 `../` levels instead of 3; now resolves correctly
   - `backend/src/api/searchChannelB.ts` — MAJOR REWRITE: LlmFn type; ChannelBResult with page?; extractFirstPage(); cleanChunkText() CJK regex; synthesizeAnswer(); statistical filter (stat_fact + stat_ prefix); min_score default 0.22
   - `backend/src/api/searchCombined.ts` — REWRITTEN: A+B parallel + dedup + merged synthesis; synthesize: false passed to B to avoid double-call
   - `backend/src/server.ts` — MODIFIED: llmClient passed to searchChannelB and searchCombined
   - `index.html` — MODIFIED: synthesis state; SourcesAccordion component (groups by URL, approved facts green); Channel B shows accordion when synthesis present; A+B synthesis support; setSynthesis(null) on clear/switch
   - `dev/vault/sag_2025_11/extract_sag_ch2_ch4_ch5.txt` — NEW: 3379 lines (Ch2 學與教, Ch4 家庭學校社區, Ch5 策劃財政預算)
   - `dev/vault/edbc12_2025_ph_pri/extract_edbc12_2025.txt` — NEW: 435 lines (EDBC 12/2025 小學人文科課程指引)
   - `dev/vault/g04/extract_g04.txt` — NEW: 98 lines (knowledge-based HR leave policy extract)
   - `dev/knowledge/wiki_index.json` — REBUILT: 810 → 1,235 chunks (53 MB); added SAG ch2/4/5 + edbc12_2025
   - `dev/PDF_DOWNLOAD_LIST.md` — NEW: prioritised PDF download list with source_ids and direct links
   - **18 new vault extract files** (pdftotext batch 2026-04-17)
5. Completed:
   - ✅ Channel B 全面除錯：CORS_ORIGIN=* / wikiRepository path fix / --env-file=.env
   - ✅ Channel B LLM synthesis (gpt-4.1-nano, top 5 chunks, ≤120字繁中)
   - ✅ Statistical fact filtering + CJK text cleaning regex + page number extraction
   - ✅ SourcesAccordion: groups Channel B chunks by source document; approved facts in green
   - ✅ A+B channel synthesis; wiki_index rebuilt 810 → 1,235 chunks
   - ✅ 18 new vault extract files created via pdftotext batch
6. Pending (next session):
   - Run extract_candidates.py --append for g02, g03, g04, g05, g11, edbc circulars
   - Review new Channel A candidates in Dashboard

---

## 2026-04-16 Session 75 — Phase 1 Backend + Phase 2 SPA Migration + SAG Extraction

1. Agent & Session ID: Claude_20260416_0003
2. Task summary: Built all Phase 1 backend search APIs (Channel A/B/Combined). Migrated k1-dashboard.html → index.html as full React SPA with 平台介紹 tab, Channel A/B/A+B selector, PlatformIntroPanel. Fixed wiki_search.py (model + params + 繁中). Extracted SAG 學校行政手冊 Ch1/3/6/7 and added 9 new Channel A candidates.
3. Layer classification: Product / Pipeline / UI Layer
4. Files changed:
   - `backend/src/lib/wikiRepository.ts` — NEW: wiki_index.json loader + cosine similarity search (no top-k limit)
   - `backend/src/api/searchChannelA.ts` — NEW: Channel A keyword+embedding search
   - `backend/src/api/searchChannelB.ts` — NEW: Channel B wiki cosine search
   - `backend/src/api/searchCombined.ts` — NEW: A+B parallel search, dedup by text prefix (80 chars)
   - `backend/src/server.ts` — MODIFIED: 3 new POST routes added; npm run check ✅
   - `index.html` — MAJOR REWRITE: full React SPA (3183 lines); PlatformIntroPanel; Channel A/B/A+B buttons; WordCloud removed
   - `dev/vault/sag_2025_11/extract_sag_ch1_ch3_ch6_ch7.txt` — NEW: 7309 lines
   - `dev/knowledge/candidate_queue.json` — UPDATED: 72 → 81 candidates
5. Completed:
   - ✅ Phase 1 Backend: all 4 files + 3 routes; npm run check ✅
   - ✅ Phase 2 SPA: index.html full React SPA; PlatformIntroPanel; Channel A/B/A+B; 平台介紹 first tab
   - ✅ SAG extraction: Ch1/3/6/7 → 9 new Channel A candidates
6. Decisions: Channel B/A+B require local backend by design; wikiRepository returns ALL results (no top-k cap); searchCombined dedup 80-char prefix with Channel A priority

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first, then: dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md

Current state: v1.4.3. Phase 1 (backend search APIs) + Phase 2 (index.html SPA) both COMPLETE.
- index.html = full React SPA (Channel A/B/A+B, 平台介紹 tab, 知識提煉 Admin)
- k1-dashboard.html = deprecated (legacy link only)
- wiki_index.json = 810 chunks built ✅
- Channel A queue = 81 candidates (9 new SAG sag_2025_11 candidates need review)
- Channel B = requires `cd backend && npm run dev` for B/A+B search

Next work in priority order:
1. Session docs update (SESSION_HANDOFF.md + SESSION_LOG.md + CODEBASE_CONTEXT.md)
2. Extract SAG Ch2/Ch4/Ch5 → python3 dev/vault/extract_candidates.py --append (sag_2025_11)
3. Channel A review: index.html → Admin → ✍️ 知識提煉 → review 9 new SAG candidates
4. Phase 3: 知識提煉 left-right split panel redesign (deferred)
5. Phase 4: Guidelines 3-level sort with sub_category (deferred)
6. Phase 5: Channel B admin prompt editor (deferred)

Key files: index.html, backend/src/server.ts, dev/knowledge/candidate_queue.json, dev/vault/sag_2025_11/
```

