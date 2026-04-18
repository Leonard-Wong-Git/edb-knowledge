# Session Log

<!-- Archives: dev/archive/ — entries moved when >800 lines or oldest entry >30 days -->

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
   - **18 new vault extract files** (pdftotext batch 2026-04-17):
     - `dev/vault/g05/extract_g05.txt` — 教師專業操守指引 (30 pages, 1010 lines)
     - `dev/vault/g11/extract_g11.txt` — 擬定校曆表（3 calendar docs combined, 282 lines）
     - `dev/vault/edbc13_2025_pri_science/extract_edbc13_2025_pri_science.txt` (5 pages)
     - `dev/vault/edbc18_2023_pri_science/extract_edbc18_2023_pri_science.txt` (16 pages)
     - `dev/vault/edbc9_2024_ph_pri/extract_edbc9_2024_ph_pri.txt` (8 pages)
     - `dev/vault/edbc20_2023_ph_pri/extract_edbc20_2023_ph_pri.txt` (16 pages)
     - `dev/vault/pri_curr_guide_2024/extract_pri_curr_guide_2024.txt` (80/343 pages)
     - `dev/vault/ph_pri_guide_2025/extract_ph_pri_guide_2025.txt` (80/263 pages)
     - `dev/vault/pri_science_guide_2025/extract_pri_science_guide_2025.txt` (80/138 pages)
     - `dev/vault/chi_pri_guide_2023/extract_chi_pri_guide_2023.txt` (67 pages)
     - `dev/vault/eng_pri_guide_2025/extract_eng_pri_guide_2025.txt` (80/290 pages)
     - `dev/vault/gs_pri_guide_2017/extract_gs_pri_guide_2017.txt` (80/188 pages)
     - `dev/vault/ma_kla_guide_2017/extract_ma_kla_guide_2017.txt` (80/246 pages)
     - `dev/vault/chi_hist_jss_2019/extract_chi_hist_jss_2019.txt` (79 pages)
     - `dev/vault/chi_jss_guide_2023/extract_chi_jss_guide_2023.txt` (66 pages)
     - `dev/vault/music_p1_s6_2024/extract_music_p1_s6_2024.txt` (65 pages)
     - `dev/vault/va_p1_s6_2024/extract_va_p1_s6_2024.txt` (53 pages)
     - `dev/vault/pe_kla_2017/extract_pe_kla_2017.txt` (80/146 pages)
5. Completed:
   - ✅ Channel B 全面除錯：CORS_ORIGIN=* / wikiRepository path fix / --env-file=.env
   - ✅ Channel B LLM synthesis (gpt-4.1-nano, top 5 chunks, ≤120字繁中)
   - ✅ Statistical fact filtering (content_type="stat_fact" OR source_id starts with "stat_")
   - ✅ CJK text cleaning regex (removes spaces between CJK chars from pdftotext output)
   - ✅ Page number extraction from === Page N === markers
   - ✅ SourcesAccordion: groups Channel B chunks by source document; approved facts in green
   - ✅ A+B channel synthesis (same prompt, merged top 5)
   - ✅ wiki_index rebuilt: 810 → 1,235 chunks (SAG ch2/4/5 + edbc12_2025 added)
   - ✅ 18 new vault extract files created via pdftotext batch
   - ✅ Channel A: user approved candidates in Dashboard
   - ✅ Channel A progress: 6/148 sources extracted (g01, coa_imc_1_19, circ_edbc24017, sag_2025_11, edbc12_2025_ph_pri, g04)
   - `dev/vault/g02/extract_g02.txt` — NEW: 設有法團校董會的資助學校財務管理指引 (17 pages, 726 lines)
   - `dev/vault/g03/extract_g03.txt` — NEW: 全方位學習津貼運用指引（2024年9月）(5 pages, 286 lines)
   - `dev/knowledge/policy_signals.json` — NEW: empty template for Circular System → K1 bridge signals
   - `dev/PDF_DOWNLOAD_LIST.md` — NEW: prioritised download list with source_ids and direct links
6. Pending (next session):
   - Run `python3 dev/vault/extract_candidates.py --append` for: g02, g03, g04, g05, g11, edbc20/9/18/13 circulars
   - ✅ `python3 dev/vault/build_wiki_index.py` — **完成**：810 → 2,840 chunks (124 MB); 45 vault sources; 2,705 vault_extract + 109 approved_fact + 26 stat_fact
   - Run `python3 dev/vault/extract_candidates.py --append` for 9 pending sources (g02, g03, g04, g05, g11, edbc20/9/18/13)
   - Review new Channel A candidates in Dashboard after extraction
   - Discuss [TODO-1] Policy Signals integration with K1 Dashboard

---

## 2026-04-16 Session 75 — Phase 1 Backend + Phase 2 SPA Migration + SAG Extraction

1. Agent & Session ID: Claude_20260416_0003
2. Task summary: Built all Phase 1 backend search APIs (Channel A/B/Combined). Migrated k1-dashboard.html → index.html as full React SPA with 平台介紹 tab, Channel A/B/A+B selector, PlatformIntroPanel. Fixed wiki_search.py (model + params + 繁中). Extracted SAG 學校行政手冊 Ch1/3/6/7 and added 9 new Channel A candidates.
3. Layer classification: Product / Pipeline / UI Layer
4. Files changed:
   - `backend/.env` — NEW: OPENAI_API_KEY for local dev
   - `backend/src/lib/wikiRepository.ts` — NEW: wiki_index.json loader + cosine similarity search (no top-k limit)
   - `backend/src/api/searchChannelA.ts` — NEW: Channel A keyword+embedding search (offline, per-request embed)
   - `backend/src/api/searchChannelB.ts` — NEW: Channel B wiki cosine search (all results above minScore)
   - `backend/src/api/searchCombined.ts` — NEW: A+B parallel search, dedup by text prefix (80 chars), Channel A priority
   - `backend/src/server.ts` — MODIFIED: 3 new POST routes added; npm run check ✅
   - `dev/vault/wiki_search.py` — MODIFIED: gpt-5-nano→gpt-4.1-nano; max_completion_tokens→max_tokens; 繁體中文 prompt fix; finish_reason diagnostics
   - `index.html` — MAJOR REWRITE: full React SPA (3183 lines); PlatformIntroPanel; Channel A/B/A+B buttons; WordCloud removed; k1-dashboard.html deprecated
   - `dev/vault/sag_2025_11/extract_sag_ch1_ch3_ch6_ch7.txt` — NEW: 7309 lines (Ch1 校本管理, Ch3 學生事務, Ch6 學校財務, Ch7 人事管理)
   - `dev/knowledge/candidate_queue.json` — UPDATED: 72 → 81 candidates (9 new from sag_2025_11)
   - `dev/SESSION_HANDOFF.md` — Phase 0/1/2 marked complete; new session record
5. Completed:
   - ✅ **wiki_index.json**: 810 chunks built by user running build_wiki_index.py (~$0.002); text-embedding-3-small; 35 MB
   - ✅ **wiki_search.py tested**: Query "小學採購門檻是多少" → correct 4-tier procurement answer in Traditional Chinese
   - ✅ **Phase 1 Backend**: All 4 files + 3 routes. wikiRepository cosine implemented in TypeScript without external math libs. searchCombined deduplicates by 80-char text prefix with Channel A priority. npm run check ✅
   - ✅ **Phase 2 SPA**: index.html rewritten as full React SPA. PlatformIntroPanel (hero dynamic stats, 6-card bento, 3-step how-it-works, sources strip). QAPanel rewritten: Channel A/B/A+B toggle buttons, offline A search, backend B/A+B with graceful error. 平台介紹 first tab. WordCloud deleted. k1-dashboard.html deprecated (v1 legacy link at opacity 0.4).
   - ✅ **SAG extraction**: sag_2025_11 PDF (270 pages) → pdftotext → 10484 lines → selected Ch1/3/6/7 (7309 lines) → extract_candidates.py --append → 9 new policy candidates covering 校本管理/學生事務/學校財務/人事管理
   - ✅ **UI confirmed**: User screenshot showed index.html with working Channel A/B/A+B buttons and backend error handling
6. Decisions / non-obvious choices:
   - Channel B/A+B require local backend (OpenAI embedding on query); Channel A is fully offline — by design, no GitHub Pages backend
   - wikiRepository returns ALL results above minScore (no top-k cap) — frontend paginates
   - searchCombined deduplication: 80-char text prefix comparison, Channel A takes priority on tie
   - SAG Ch2 學與教 / Ch4 家校伙伴 / Ch5 策劃預算 deferred to next extraction batch
   - P0.3 role_facts.json prefix fix deferred (lower priority)

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

---

## 2026-04-16 Session 74 — Platform Architecture Decisions + UI Redesign (index.html / dashboard)

1. Agent & Session ID: Claude_20260416_0002
2. Task summary: Completed UI redesign of index.html (K1知識平台 branding) and k1-dashboard.html (Cloud Dancer design system). Conducted full architectural planning for the platform. Confirmed final architecture: index.html → single React SPA entry point; k1-dashboard.html → deprecated. Defined Channel A/B/A+B search backend API design, Channel B admin prompt editor, guidelines dual-sort, and full phased work order.
3. Layer classification: Product / Architecture / UI Layer
4. Files changed:
   - `index.html` — NEW: K1知識平台 homepage (rebranded from k1-wiki.html, branding updated)
   - `k1-dashboard.html` — Visual redesign: new CSS design system (Cloud Dancer + Mocha Mousse tokens), new header/nav, sidebar cards, tab system, footer — all React logic preserved
   - `dev/SESSION_HANDOFF.md` — Architecture decisions + revised open priorities
   - `dev/SESSION_LOG.md` — this entry
5. Completed:
   - ✅ **index.html created**: K1知識平台 branding (was k1-wiki.html). Title, logo, hero label, footer all updated. Secondary CTA → "進入知識平台". Mobile bottom nav updated.
   - ✅ **k1-dashboard.html redesign**: 320-line CSS design system replacing old Tailwind overrides. New header with K1知識平台 logo + sub-label + ← 首頁 link. `k1-tab-bar`, `k1-card`, `k1-sidebar`, `k1-btn`, `k1-footer` components. All React logic unchanged.
   - ✅ **Architecture confirmed** (full discussion):
     - index.html =唯一入口 React SPA (tabs: 智能搜尋/指引/通告分析/平台介紹/知識提煉/知識管理)
     - k1-dashboard.html = deprecated after migration
     - Platform stats: dynamic A+B combined (not hardcoded)
     - Channel B search: backend API (not frontend JSON load) — no top-4 limit, return all results
     - Channel B admin: prompt editor UI (SYSTEM_PROMPT_B + SYNTHESIS_PROMPT editable)
     - Guidelines: 3-level sort (category → sub_category → time desc)
     - 知識提煉: left-right layout + inline edit restored
     - WordCloud animation: deleted
6. Decisions / non-obvious choices:
   - Channel B search returns ALL results (no top-k cap) — backend handles filtering/ranking
   - Platform stats reflect BOTH channels (same source vault), updated dynamically
   - Channel B candidates stay independent from Channel A queue; admin tunes quality via prompt editor
   - Backend: extend existing Node.js TypeScript server (has embeddingClient.ts already) for /api/search/* endpoints

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first, then: dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md

Current state: v1.4.3 + architecture locked. index.html = new K1知識平台 homepage. k1-dashboard.html = redesigned but will be deprecated when index.html becomes full SPA. Full platform architecture confirmed (see SESSION_HANDOFF.md §Architecture Decisions).

Next work in priority order:
PHASE 0 (immediate, no architecture needed):
  1. Run: python3 dev/vault/build_wiki_index.py  (needs OPENAI_API_KEY, ~$0.002)
  2. Test: python3 dev/vault/wiki_search.py "小學採購門檻是多少"
  3. Dashboard: delete "課程統籌主任規劃" prefix → export role_facts.json
  4. Admin Review: reject 2 duplicate circ_edbc24017 candidates; approve remaining 19

PHASE 1 (backend):
  - backend/src/api/searchChannelA.ts
  - backend/src/api/searchChannelB.ts  (no top-k limit, return all)
  - backend/src/api/searchCombined.ts
  - backend/src/lib/wikiRepository.ts  (load wiki_index.json, cosine search)

PHASE 2 (frontend, index.html SPA migration):
  - Merge k1-dashboard.html React app into index.html
  - Add 平台介紹 tab (current static content)
  - Channel A/B/A+B search buttons
  - Dynamic stats from actual data

PHASE 3+: 知識提煉 left-right layout, guidelines dual-sort, Channel B prompt editor
```

---

## 2026-04-16 Session 73 — k1-wiki.html: Public-Facing LLM-Wiki Landing Page

1. Agent & Session ID: Claude_20260416_0001
2. Task summary: Designed and built k1-wiki.html — a full public-facing landing page for the K1 EDB LLM-Wiki system. Used ui-ux-responsive skill, Pantone 2026 Cloud Dancer + Mocha Mousse palette, mobile-first design with 10+ sections.
3. Layer classification: Product / UI Layer
4. Files changed:
   - `k1-wiki.html` — NEW: full landing page (hero, search demo, bento grid, how-it-works, sources, channel A/B, roles, CTA, footer)
   - `dev/SESSION_HANDOFF.md` — open priorities + last session record updated
   - `dev/SESSION_LOG.md` — this entry
5. Completed:
   - ✅ **k1-wiki.html**: Public landing page for LLM-wiki. Fixed nav + mobile bottom nav. Hero with fluid typography (clamp), stats bar (109+ facts, 39 guidelines, 7 topics, 810 chunks). Scrolling EDB topic ticker. Interactive search demo (5 preset Q&A datasets: procurement, CPD, overseas, stats, anti-bullying). Bento feature grid (7 cards). 3-step How-It-Works. Trusted sources strip (4 EDB docs). Channel A/B comparison cards. 6 role cards (Principal/VP/Panel Chair/Subject Head/Teacher/EO). CTA + footer.
   - ✅ **Design system**: CSS custom properties, fluid type scale (clamp), Cloud Dancer (#F0EEE9) base + Mocha Mousse (#A47764) accent, IntersectionObserver scroll reveals, nav scroll shadow.
6. Decisions / non-obvious choices:
   - Landing page is purely informational/demo — no backend connection; search demo uses pre-baked answer datasets
   - Mobile bottom nav added for app-like UX on phones
   - Stats reflect current knowledge base state: 109 role facts, 39 guidelines, 7 topics, 810 chunks (wiki_index.json pending build)

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists)

Current state: v1.4.3. k1-wiki.html (public landing page) just created. Channel B pipeline built but wiki_index.json not yet built (needs API key + ~$0.002). 72 candidates in Channel A queue (19 pending review). EO→行政主任 improvements pending export.

Pending tasks in priority order:
1. Dashboard fix: Admin → Knowledge tab → find "課程統籌主任規劃，科主任須帶領..." → delete prefix → export 發布版 role_facts.json → replace repo file
2. Build wiki index: python3 dev/vault/build_wiki_index.py (cost ~$0.002, needs API key)
3. Test wiki search: python3 dev/vault/wiki_search.py "小學採購門檻是多少"
4. Admin Review: Reject 2 circ_edbc24017 duplicate candidates; approve remaining 19
5. SQLite db.ts type contract in backend/src/lib/
6. Review / refine k1-wiki.html as needed

Key files: k1-wiki.html, dev/vault/build_wiki_index.py, dev/vault/wiki_search.py, dev/knowledge/wiki_index.json (not yet built)

Known risks: wiki_index.json not yet built; guidelines not indexed (embedded in dashboard HTML); Channel B Circular System integration paused; EDB HTML embed blocked permanently.
```

---

## 2026-04-15 Session 72 — Channel B: ai_extract.py · build_wiki_index.py · wiki_search.py

1. Agent & Session ID: Claude_20260415_0003
2. Task summary: Clarified Channel B architecture. Built three Channel B components: ai_extract.py (batch AI fact extraction), build_wiki_index.py (vector index builder, 810 chunks, ~$0.002 embedding cost), wiki_search.py (semantic retrieval + LLM synthesis engine). Channel B paused from Circular System pending testing.
3. Layer classification: Product / Pipeline / Architecture Layer
4. Files changed:
   - `dev/vault/ai_extract.py` — Channel B batch extractor (updated prompt, broader analysis)
   - `dev/vault/build_wiki_index.py` — NEW: offline index builder (chunking + embeddings + hash dedup)
   - `dev/vault/wiki_search.py` — NEW: online query engine (cosine retrieval + LLM synthesis)
   - `dev/SESSION_HANDOFF.md` — open priorities updated
   - `dev/SESSION_LOG.md` — this entry
   - `dev/CODEBASE_CONTEXT.md` — AI Maintenance Log updated
5. Completed:
   - ✅ **Architecture clarification**: Channel B has same functions as Channel A (policy fact extraction, can feed Circular System) PLUS LLM-wiki search. Circular System integration PAUSED pending testing.
   - ✅ **ai_extract.py**: Batch AI extraction, broader prompt (requirement/guidance/deadline/procedure/risk_flag), outputs ai_candidate_queue.json. NOT connected to Circular System yet.
   - ✅ **build_wiki_index.py**: Indexes vault extracts (21 files) + role_facts.json (109 facts) + stat_facts.json (26 facts) + guidelines. 810 chunks at ≤600 chars each. Hash-based dedup (skip re-embedding unchanged chunks). Estimated cost: ~$0.002 total.
   - ✅ **wiki_search.py**: Cosine similarity retrieval (no numpy), top-k=4 chunks (≤2400 chars context), LLM synthesis (≤200 char answer + source URLs). Supports --retrieve-only and --json flags.
   - ✅ **Token efficiency**: Pre-computed embeddings (one-time), only top-4 chunks per query, 200-char answer cap.
6. Decisions / non-obvious choices:
   - Channel B does NOT auto-write to role_facts.json — output stays in ai_candidate_queue.json until testing confirms quality
   - Cosine similarity implemented without numpy (pure Python) for portability
   - Chunk overlap=60 chars to preserve sentence context across chunk boundaries
   - guidelines.json not found at repo root (guidelines embedded in dashboard HTML) — 0 guidelines indexed; can add later

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current state: v1.4.3. Channel B pipeline fully built: ai_extract.py + build_wiki_index.py + wiki_search.py. Channel B paused from Circular System pending testing. 72 candidates in Channel A queue. EO→行政主任 improvements in admin snapshot pending export to role_facts.json.

Pending tasks in priority order:
1. Dashboard fix: Admin → Knowledge tab → find "課程統籌主任規劃，科主任須帶領..." → delete prefix → export 發布版 role_facts.json → replace repo file
2. Build wiki index: python3 dev/vault/build_wiki_index.py (cost ~$0.002, needs API key)
3. Test wiki search: python3 dev/vault/wiki_search.py "小學採購門檻是多少"
4. Admin Review: Reject 2 circ_edbc24017 duplicate candidates; approve remaining 19
5. SQLite db.ts type contract in backend/src/lib/

Key files: dev/vault/ai_extract.py, dev/vault/build_wiki_index.py, dev/vault/wiki_search.py, dev/knowledge/wiki_index.json (not yet built), dev/knowledge/ai_candidate_queue.json

Known risks: wiki_index.json not yet built (need to run build_wiki_index.py); guidelines not indexed (embedded in dashboard HTML, not in guidelines.json); Channel B Circular System integration explicitly paused; EDB HTML embed blocked permanently.

Post-startup first action: Ask user if they want to run build_wiki_index.py to create the wiki index (needs API key, ~$0.002), or proceed with other pending tasks first.
```

## 2026-04-15 Session 71 — dedup_check.py · Snapshot Analysis · EO→行政主任 Improvements

1. Agent & Session ID: Claude_20260415_0002
2. Task summary: Built dedup_check.py (no-LLM fact deduplication tool). Ran dedup check on admin snapshot vs role_facts.json. Identified EO→行政主任 improvements made in Dashboard. Clarified two-channel architecture isolation from Circular System. Confirmed Channel A pipeline status.
3. Layer classification: Product / Pipeline / Quality Layer
4. Files changed:
   - `dev/vault/dedup_check.py` — NEW: fact dedup tool (character n-gram + CJK word similarity, no API key)
   - `dev/SESSION_HANDOFF.md` — open priorities updated
   - `dev/SESSION_LOG.md` — this entry
5. Completed:
   - ✅ **Architecture clarification**: Channel A/B do NOT affect live Circular System until explicit export of role_facts.json. Circular System reads only repo-root role_facts.json.
   - ✅ **Channel A status confirmed**: 72 candidates pending approval; 97/112 sources unextracted.
   - ✅ **dedup_check.py built**: Character bigram + trigram + CJK word Jaccard similarity. Detects exact duplicates (100%), near-duplicates (🔴 85%+), similar (🟡 60%+), related (🔵 50%+). Supports `--against` for cross-file comparison. No API key required.
   - ✅ **Snapshot analysis (2026-04-03 snapshot vs role_facts.json)**:
     - 101 exact 100% pairs → expected (snapshot mirrors role_facts.json, not a problem)
     - 5–6 pairs at 85-89% → user improved "EO" → "行政主任" in Dashboard (keep new version)
     - 1 pair at 80% → fact has unwanted prefix "課程統籌主任規劃，" → fix in Dashboard before export
     - 1 pair at 59% → new version more specific (ER/MR vs 設施) → keep new version
   - ✅ **Action plan**: Fix 1 fact in Dashboard → export 發布版 role_facts.json → replace repo file to capture EO→行政主任 improvements.
6. Decisions / non-obvious choices:
   - dedup tool uses max(bigram, trigram, CJK-word) similarity to improve Chinese recall vs trigram-only
   - 100% matches in cross-file check are expected when snapshot predates new candidate approvals — not a bug

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current state: v1.4.3. dedup_check.py built and tested. Snapshot analysis complete: admin snapshot (2026-04-03) has EO→行政主任 improvements worth saving. One fact has unwanted prefix to fix. 72 candidates pending approval in queue.

Pending tasks in priority order:
1. Dashboard fix: Admin → Knowledge tab → find fact starting "課程統籌主任規劃，科主任須帶領..." → delete prefix → then export 發布版 role_facts.json → replace repo role_facts.json (captures EO→行政主任 improvements)
2. Continue Admin Review: Reject 2 circ_edbc24017 duplicate candidates (工作坊230場 + 100小時 appear twice); approve remaining 19
3. Channel B: design ai_extract.py schema (vault extract text → GPT → ai_candidate_queue.json)
4. SQLite db.ts type contract in backend/src/lib/

Key files: dev/vault/dedup_check.py, dev/knowledge/candidate_queue.json, dev/knowledge/candidate_queue.js, role_facts.json

Known risks: Snapshot is from 2026-04-03 — does not include recently approved candidates; export role_facts.json AFTER completing all pending approvals for a clean single export. EDB HTML embed blocked permanently. Online semantic re-verify needs live OPENAI_API_KEY.

Post-startup first action: Remind user to fix the one fact with unwanted prefix in Dashboard Knowledge tab, then export 發布版 role_facts.json to capture EO→行政主任 improvements before approving new candidates.
```

## 2026-04-15 Session 70 — Vault Audit · circ_edbc24017 Extraction · stat_facts Build

1. Agent & Session ID: Claude_20260415_0001
2. Task summary: Vault extract.txt audit. Ran Channel A extraction for circ_edbc24017 (21 new policy candidates). Synced candidate_queue.js to 72 total. Built stat_facts.json (26 auto-approved statistical facts from 5 sources) without LLM via new build_stat_facts.py.
3. Layer classification: Product / Pipeline Layer
4. Files changed:
   - `dev/knowledge/candidate_queue.json` — 21 new candidates appended from circ_edbc24017 (total 72)
   - `dev/knowledge/candidate_queue.js` — synced to 72 candidates
   - `dev/knowledge/stat_facts.json` — NEW: 26 auto-approved statistical facts
   - `dev/vault/build_stat_facts.py` — NEW: stat fact builder script (no LLM)
   - `dev/SESSION_HANDOFF.md` — open priorities updated
   - `dev/SESSION_LOG.md` — archived 1334 lines to dev/archive/SESSION_LOG_2026_Q2.md; this entry
5. Completed:
   - ✅ **Vault Audit**: 3 sources have policy extract.txt (circ_edbc24017 NEW; g01/coa_imc_1_19 already in queue). 6 stat sources with extract files. 12 dirs catalogue-only (need PDF download). High-priority g06/g08/g13 not yet in vault.
   - ✅ **circ_edbc24017 Channel A Extraction**: `python3 dev/vault/extract_candidates.py --append` → 21 new curriculum/hr policy candidates. 2 duplicates flagged (candidates #6≈#20 re: 230場工作坊; #7=#21 re: 100小時培訓). Admin should Reject duplicates during review.
   - ✅ **candidate_queue.js Sync**: Updated from 51 → 72 candidates via Python rebuild.
   - ✅ **stat_facts.json**: 26 auto-approved facts across stat_kg(5), stat_pri(6), stat_sec(6), stat_special(4), stat_integrated_edu(5). Latest year 2024/25 (integrated: 2025/26). No LLM required — programmatic parse.
   - ✅ **§4a Archive**: SESSION_LOG.md was 1412 lines. Archived Sessions 67 and older to dev/archive/SESSION_LOG_2026_Q2.md. Retained Sessions 68 + 69 in active log.
6. Decisions / non-obvious choices:
   - stat_facts.json is separate from candidate_queue.json — statistical facts are auto-approved and feed LLM-wiki search only, not role_facts.json injection
   - build_stat_facts.py is hardcoded from parsed extract data (not LLM) — faster, cheaper, no API key needed, deterministic
   - candidate_queue.js rebuilt from JSON (not appended) to ensure clean sync

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current state: v1.4.3. Channel A: 72 candidates in queue (circ_edbc24017 added — 2 duplicates to reject in Admin Review). stat_facts.json built (26 auto-approved statistical facts, no LLM). Two-channel architecture confirmed.

Pending tasks in priority order:
1. Admin Review: open dashboard → Candidate Review tab → Reject 2 circ_edbc24017 duplicates (工作坊230場 + 100小時 appear twice); approve remaining
2. Channel B: design ai_extract.py schema (input: vault extract text → GPT auto-propose → output: ai_candidate_queue.json separate from human queue)
3. SQLite db.ts type contract (sources / facts / guidelines tables) in backend/src/lib/
4. High-priority source extraction: g06/g08/g13 need PDF download → vault extract → Channel A

Key files: dev/knowledge/candidate_queue.json, dev/knowledge/candidate_queue.js, dev/knowledge/stat_facts.json, dev/vault/build_stat_facts.py, dev/vault/extract_candidates.py

Known risks / blockers: 97/112 sources not yet extracted; g06/g08/g13 not yet in vault (need PDF download); online semantic re-verify needs live OPENAI_API_KEY; EDB HTML embed blocked permanently.

Post-startup first action: Remind user to open dashboard Admin → Candidate Review and Reject the 2 circ_edbc24017 duplicate candidates before approving the rest.
```

## 2026-04-13 Session 69 — Phase 0 Fix · Pie Chart Full · Candidate Edit · Two-Channel Architecture

1. Agent & Session ID: Claude_20260413_0002
2. Task summary: Completed Phase 0 backend fix (topic contamination). Fixed pie chart to show all 16 categories. Added inline edit capability to Candidate Review flow. Confirmed two-channel pipeline architecture and policy document export backlog feature.
3. Layer classification: Product / System / Architecture Layer
4. Files changed:
   - `backend/src/services/topicDetector.ts` — `MAX_TOPICS=2` + `SCORE_GAP=0.05` filter applied
   - `k1-dashboard.html` — Pie chart full (removed `.slice(0,4)`); CandidateCard inline edit before approve
   - `dev/SESSION_HANDOFF.md` — v1.4.3 baseline; two architecture decisions recorded; open priorities updated
   - `dev/SESSION_LOG.md` — this entry
5. Completed:
   - ✅ **Backend Phase 0**: `topicDetector.ts` — `MAX_TOPICS=2` hard cap + `SCORE_GAP=0.05` secondary-topic filter. Tested with 5 scenarios via Node.js inline simulation. Verified online: EDBC 12/2025 returned `total_fact_chars: 581`.
   - ✅ **Pie Chart Full**: Removed `.slice(0,4)` in conic-gradient builder and legend. All 16 WORDCLOUD_DATA items now show as distinct coloured slices. Legend switched to `grid grid-cols-2`, swatch size `w-3 h-3`, `text-xs`. No more `#F5EFE8` off-white remainder.
   - ✅ **CandidateCard Inline Edit**: Added `editableText` + `isEditing` state. Hover on proposed_text → ✏️ icon appears. Click → textarea (pre-populated). Buttons: 「完成修改」/ 「還原原文」. Edited badge + button label change to「確認修改並通過」. `onApprove` receives `proposed_text: editableText`.
   - ✅ **Source Audit**: 112 sources in registry; 97 not yet extracted into candidate pipeline. 15 already extracted (g01–g05, g16–g20, g24, g28, coa_imc_1_19, sag_2025_11, edbc_12_2025).
   - ✅ **Architecture — Two-Channel Pipeline confirmed**:
     - Channel A (Human Review): existing pipeline → `candidate_queue.js` → Admin Approve with edit → `role_facts.json`
     - Channel B (Full AI): same sources → `ai_extract.py` → `ai_candidate_queue.json` (separate, not yet built)
     - UI unchanged for now; future: comparison view
   - ✅ **Architecture — Policy Document Export (Backlog)**: Users export knowledge by topic/role as PDF or WhatsApp text. Deferred; not yet implemented.
6. Decisions / non-obvious choices:
   - Channel B queue uses separate file (`ai_candidate_queue.json`) to keep human and AI pipelines independent and comparable
   - Inline edit passes `proposed_text: editableText` at approve time (not a separate save step) to keep the flow lightweight
   - Policy export uses client-side PDF generation (jsPDF or print CSS) to avoid backend dependency

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md → dev/PROJECT_MASTER_SPEC.md

Current state: v1.4.3. Phase 0 backend fix done. Pie chart full (16 slices). CandidateCard inline edit before approve implemented.

Architecture confirmed: Two-channel pipeline (Channel A human review existing; Channel B full-AI pending). Policy document export in backlog.

Next priorities:
1. Vault extract.txt audit → list which sources have extract.txt ready → run Channel A extraction immediately
2. Design ai_extract.py schema for Channel B
3. SQLite db.ts type contract (sources/facts/guidelines tables)

Key files: k1-dashboard.html, backend/src/services/topicDetector.ts, dev/source/source_registry.json, dev/knowledge/candidate_queue.json, dev/vault/

Known risks: 97/112 sources not yet extracted; online semantic re-verify needs live OPENAI_API_KEY; EDB HTML embed blocked permanently.
```

## 2026-04-13 Session 68 — UX Recovery & Security Fallback Hardening

1. Agent & Session ID: Antigravity_20260413_0820
2. Task summary: Fixed a critical UX bug where an invisible overlay blocked all interaction. Hardened the Document Library drawer with a smart fallback panel for EDB HTML pages that cannot be embedded. Fully aligned the UI with the Pantone 2026 warm palette.
3. Layer classification: Product / System Layer
4. Files changed:
   - `k1-dashboard.html` — Conditional rendering for drawer backdrop; smart domain detector in drawer; style cleanup.
   - `dev/SESSION_HANDOFF.md`
   - `dev/SESSION_LOG.md`
5. Completed:
   - ✅ **Ghost Overlay Fix**: Rewrote the Slide-in Drawer backdrop logic to only render when `previewDoc` is active, restoring all page interactions.
   - ✅ **EDB Security Fallback**: Added a domain detection switch that replaces broken iframes with a high-fidelity "Blocked Preview" panel (Pantone themed) and a prominent "Open in New Tab" button for EDB HTML links.
   - ✅ **Palette Completion**: Ensured all buttons (Reset, Search, Nav) and chart bars correctly use the Pantone 2026 hex values.
   - ✅ **Code Hygiene**: Removed orphaned JSX fragments and redundant titles.

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)
Current objective and progress state: v1.4.2 Hardened. Visuals fully Pantone 2026 aligned. UX interaction issues resolved. EDB security headers handled via smart fallback.
Pending tasks in priority order:
1. Admin Approval E2E flow validation (Candidate -> Review -> Dashboard Fact Count).
2. Knowledge Pipeline: Extract from `coa_imc_1_19`.
3. Monitor for Guidelines feedback.
Key files changed in this session: k1-dashboard.html, dev/SESSION_HANDOFF.md, dev/SESSION_LOG.md
Known risks / blockers / cautions: EDB HTML pages strictly block iframes; the new fallback panel is the permanent solution for these links.
Post-startup first action: Verify the Admin Review dashboard correctly approves a candidate and updates the "Confirmed Facts" metric on the main page.
```


