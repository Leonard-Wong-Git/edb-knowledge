# Session Log

<!-- Archives: dev/archive/ — entries moved when >400 lines or oldest entry >30 days -->

## 2026-04-20 Session 83 — Phase 3 Knowledge Review Split Workspace

1. Agent & Session ID: Codex_20260420_1427
2. Task summary: Refactored `app.html` 知識提煉 Admin from single-column candidate cards into a left/right review workspace with candidate queue, evidence inspector, inline text revision, role toggles, and existing approve/reject flow.
3. Layer classification: Product / UI Layer + Release / Deploy
4. Files changed:
   - `app.html` — MODIFIED: added review split workspace CSS and replaced `CandidateReviewPanel`; removed unused old `CandidateCard` implementation
   - `dev/SESSION_HANDOFF.md` — MODIFIED: marked Phase 3 review split complete and moved next priorities forward
   - `dev/CODEBASE_CONTEXT.md` — MODIFIED: updated directory map and AI Maintenance Log for Phase 3 behavior
   - `dev/SESSION_LOG.md` — MODIFIED: added this session entry, test scenarios, doc sync, and release gate evidence
5. Completed:
   - ✅ Candidate review now uses left queue + right sticky evidence/revision inspector
   - ✅ Inline candidate text revision and role toggles are available before approval
   - ✅ Existing `handleApproveCandidate` / `handleRejectCandidate` data flow retained
   - ✅ Empty queue state preserved
   - ✅ Mobile responsive fallback added for the split workspace
6. Pending:
   - Circular System: `edb_scraper.py _write_policy_signal()` (deferred)
   - Phase 4: 指引文件庫 dual sort (`sub_category`)
7. Verification:
   - `sed -n '547,4173p' app.html | node -e "...esbuild.transformSync(...,{loader:'jsx'})"` → PASS (`esbuild jsx parse PASS`)
   - `rg -n "CandidateCard|review-workspace|review-inspector|candidate-row|知識提煉" app.html` → PASS (`CandidateCard` removed; split workspace markers present)
   - Independent review pass: self-review checked correctness, consistency with Phase 3 requirement, regression risk, doc sync, and GitHub Pages compatibility → PASS
   - `git commit -m "feat: add split candidate review workspace"` → PASS (`1fcbd66`)
   - `git push origin main` → PASS (`88f37a8..1fcbd66 main -> main`)
   - `curl -L https://raw.githubusercontent.com/Leonard-Wong-Git/edb-knowledge/main/app.html | rg -n "review-workspace|review-inspector|candidate-row|逐條核對候選事實"` → PASS
   - `curl -L "https://leonard-wong-git.github.io/edb-knowledge/app.html?v=1fcbd66" | rg -n "review-workspace|review-inspector|candidate-row|逐條核對候選事實"` → PASS
   - Note: bare `app.html` was still serving a short GitHub Pages cache immediately after push; cache-busted URL verified the live updated artifact.

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Empty queue | `candidateQueue.length === 0` | Open 知識提煉 | Shows calm empty state with no crash | Empty branch preserved as `review-empty` | PASS |
| Candidate selection | Queue has items | Click candidate row | Inspector updates to selected candidate | `selectedId` drives active row, editor, role toggles, and source evidence | PASS |
| Approve/reject | Queue has items | Use inspector buttons | Existing handlers called with selected candidate | Inspector calls `onApprove({...selected, proposed_text, suggested_roles})` and `onReject(selected.id)` | PASS |
| Responsive | Narrow viewport | Open review view | Two columns stack without overlap | CSS switches `.review-workspace` to one column below 980px | PASS |
| Release | Checks pass | Commit + push | GitHub Pages live app includes new review workspace | Cache-busted GitHub Pages URL contains split workspace markers | PASS |

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Product behavior / tuning change | SESSION_HANDOFF.md baseline, priorities, risks if affected; SESSION_LOG.md task entry + QC evidence | ✓ Done |
| Product behavior / tuning change | CODEBASE_CONTEXT.md Directory Map / AI Maintenance Log if stable product behavior changed | ✓ Done |
| Product version / release milestone change | k1-dashboard.html `_meta`; dev/knowledge/role_facts.json `_meta`; README badge; CHANGELOG; SESSION_HANDOFF.md; SESSION_LOG.md; CODEBASE_CONTEXT.md if release summary changed | N/A — no version number or public data schema changed; GitHub Pages sync only |

---

## 2026-04-20 Session 82 — S5 Draft Canvas + GitHub Sync

1. Agent & Session ID: Codex_20260420_1425
2. Task summary: Implemented S5 Draft Canvas in `t-purchase.html` and prepared the current static frontend changes for GitHub Pages sync.
3. Layer classification: Product / UI Layer + Release / Deploy
4. Files changed:
   - `t-purchase.html` — MODIFIED: added S5 draft canvas, source/citation panel, stale-source warning, section selection, revision action bar, and S4-to-S5 open-draft flow
   - `dev/SESSION_HANDOFF.md` — MODIFIED: marked S5 complete and moved next priorities to Circular System / Phase 3 admin redesign
   - `dev/CODEBASE_CONTEXT.md` — MODIFIED: updated directory map and AI Maintenance Log for S5 behavior
   - `dev/SESSION_LOG.md` — MODIFIED: added this session entry, test scenarios, doc sync, and deploy-gate evidence
5. Completed:
   - ✅ S5 Draft Canvas built inside `t-purchase.html` to avoid GitHub Pages routing issues
   - ✅ S4 completion CTA now opens the draft workspace
   - ✅ Draft sections can be selected; selected section updates the source panel and revision action bar
   - ✅ §2 stale-source warning state implemented
   - ✅ GitHub sync requested by user; local release gate prepared before commit/push
6. Pending:
   - Circular System: `edb_scraper.py _write_policy_signal()` (deferred)
   - Phase 3: 知識提煉 left-right split panel redesign in `app.html`
7. Verification:
   - `sed -n '/<script>/,/<\\/script>/p' t-purchase.html | sed '1d;$d' | node --check` → PASS
   - `rg -n "draft-stage|openDraft|sourceMap|selectSection|S5 Draft|alert\\(|開啟草稿|stale" t-purchase.html` → PASS (`alert()` absent; S5 markers present)
   - Independent review pass: self-review checked correctness, consistency with `dev/design/Spec.html`, regression risk, documentation sync, and GitHub Pages compatibility → PASS
   - `git commit -m "feat: add document generation progress and draft canvas"` → PASS (`a32132c`)
   - `git push origin main` → PASS (`dbe83c3..a32132c main -> main`)
   - `curl -I -L https://leonard-wong-git.github.io/edb-knowledge/t-purchase.html` → PASS (HTTP 200, content-length 35736, last-modified 2026-04-20 14:18:10 UTC)
   - `curl -L https://leonard-wong-git.github.io/edb-knowledge/t-purchase.html | rg -n "S5 Draft Canvas|draft-stage|開啟草稿|Generation · Step"` → PASS

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal flow | S4 completion reached | Click open draft | Draft canvas appears with document + sources | `openDraft` calls `showDraft()`, activates `draft-stage`, and scrolls to canvas | PASS |
| Section selection | Draft canvas visible | Select §2 | Selected section and matching source context update | `selectSection()` updates selected class, revision label, citation cards, and §2 stale warning | PASS |
| Mobile source panel | Narrow viewport | Use sources area after canvas | Sources panel remains accessible without overlap | CSS switches `.canvas` to one column and removes sticky positioning below 980px | PASS |
| Regression | S3/S4 flow | Fill form → generate | Validation and S4 progress still work | Previous `check()`, `startGeneration()`, and `completeGeneration()` paths retained; JS syntax check passes | PASS |
| Release gate | Local checks pass | Commit + push main | GitHub Pages receives latest commit | Live GitHub Pages returns 200 and contains S4/S5 markers | PASS |

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Product behavior / tuning change | SESSION_HANDOFF.md baseline, priorities, risks if affected; SESSION_LOG.md task entry + QC evidence | ✓ Done |
| Product behavior / tuning change | CODEBASE_CONTEXT.md Directory Map / AI Maintenance Log if stable product behavior changed | ✓ Done |
| Product version / release milestone change | k1-dashboard.html `_meta`; dev/knowledge/role_facts.json `_meta`; README badge; CHANGELOG; SESSION_HANDOFF.md; SESSION_LOG.md; CODEBASE_CONTEXT.md if release summary changed | N/A — no version number or public data schema changed; GitHub Pages sync only |

---

## 2026-04-20 Session 81 — S4 Generation Progress

1. Agent & Session ID: Codex_20260420_1413
2. Task summary: Implemented S4 Generation Progress in `t-purchase.html`, replacing the previous "生成" alert stub with an in-page step-based progress/result experience.
3. Layer classification: Product / UI Layer
4. Files changed:
   - `t-purchase.html` — MODIFIED: added S4 generation progress workspace, 5-step progress track, ETA, source-mode-specific status copy, document skeleton reveal, completion state, and return-to-edit flow
   - `dev/SESSION_HANDOFF.md` — MODIFIED: marked S4 complete and moved next priority to S5 Draft Canvas
   - `dev/CODEBASE_CONTEXT.md` — MODIFIED: updated directory map and AI Maintenance Log for S4 behavior
   - `dev/SESSION_LOG.md` — MODIFIED: added this session entry and QC evidence
5. Completed:
   - ✅ Replaced `alert()` submit stub with `startGeneration()`
   - ✅ Added S4 progress UI that follows the design spec: step count, progress bar, ETA, source extraction copy, and section skeleton reveal
   - ✅ Added source-mode variations for Channel A / B / A+B
   - ✅ Added completion state and a return-to-edit path; S5 Draft Canvas remains separate and not implemented here
6. Pending:
   - S5 Draft Canvas (`/d/:id` style document workspace)
   - Circular System: `edb_scraper.py _write_policy_signal()` (deferred)
7. Verification:
   - `sed -n '/<script>/,/<\\/script>/p' t-purchase.html | sed '1d;$d' | node --check` → PASS
   - `rg -n "alert\\(|草稿已準備|返回修改|Generation · Step|sourceCopy|ETA ~|aria-live" t-purchase.html` → PASS (`alert()` removed; S4 markers present)
   - `git diff -- t-purchase.html` reviewed → PASS

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal flow | 4 required fields complete | Click 生成 | Progress view opens, steps advance, completion state appears | JS handler now calls `startGeneration()`; 5-step timer advances to `completeGeneration()` | PASS |
| Boundary | Required fields missing | Load/click around form | Button remains disabled and missing count shows | Existing `check()` validation preserved; button disabled until missing count is 0 | PASS |
| Source mode | Channel A/B/AB selected | Start generation | Progress copy reflects selected source mode | `sourceCopy()` maps A/B/AB to distinct pills, source description, and check copy | PASS |
| Regression | Existing form preview | Edit fields | Skeleton preview and validation still behave | Existing form, skeleton preview, and validation code retained; only submit behavior changed | PASS |

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Product behavior / tuning change | SESSION_HANDOFF.md baseline, priorities, risks if affected; SESSION_LOG.md task entry + QC evidence | ✓ Done |
| Product behavior / tuning change | CODEBASE_CONTEXT.md Directory Map / AI Maintenance Log if stable product behavior changed | ✓ Done |

---

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
