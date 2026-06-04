# Doc Sync Checklist
<!-- LOCAL PROJECT RECORD -->
<!--
  USAGE: At PERSIST phase, if any file was created or modified during CHANGE:
  1. Identify the change category in the registry below
  2. Execute all "Required Doc Updates" for matched rows
  3. Record triggered rows in SESSION_LOG under "Doc Sync"
  4. If your change type has no matching row: add the row first, then proceed
     (prevents this registry from going stale)
-->

## Change Category Registry

| Change Category | Required Doc Updates | Verification Method |
|---|---|---|
| Governance rule change (AGENTS.md) | INIT.md FILE 1 mirror; README if behavior is user-facing | grep parity check |
| Tech stack / build / dependency change | CODEBASE_CONTEXT.md Stack or Build section | manual review |
| External API / service change | CODEBASE_CONTEXT.md External Services block | block format check |
| New governance file added to install | §5a backup list in AGENTS.md; INIT.md ROOT SAFETY CHECK backup list; INIT.md FILE 1 §5a | grep check |
| Session-log maintenance utility added/changed | AGENTS.md §4a mechanism enforcement; INIT.md FILE 7 + FILE 1 §4a + §5a backup list; README*.md safeguards section; docs/qa/run_checks.sh | script self-test + grep |
| New project doc added | This file — add a row for the new doc's update triggers | row presence check |
| Governance bootstrap / INIT execution | SESSION_HANDOFF.md Last Session Record; SESSION_LOG.md task entry + handoff prompt | manual review |
| Product behavior / tuning change | SESSION_HANDOFF.md baseline, priorities, risks if affected; SESSION_LOG.md task entry + QC evidence | manual review |
| Product version / release milestone change | k1-dashboard.html `_meta`; dev/knowledge/role_facts.json `_meta`; README badge; CHANGELOG; SESSION_HANDOFF.md; SESSION_LOG.md; CODEBASE_CONTEXT.md if release summary changed | manual review |
| Backend README / standalone runbook added | CODEBASE_CONTEXT.md Build & Run or Directory Map; SESSION_HANDOFF.md priorities if operator flow changes; SESSION_LOG.md task entry + QC evidence | manual review |
| Knowledge operating architecture / planning doc | CODEBASE_CONTEXT.md Directory Map or Key Decisions if it changes long-term direction; SESSION_HANDOFF.md priorities/risks if follow-up work changes; SESSION_LOG.md task entry + QC evidence | manual review |
| _[Add project-specific rows below this line]_ | | |
| New / iterated isolated PoC (Testing/ only, no Draft code/data/contract change) | SESSION_LOG/HANDOFF record at closeout; the PoC's own Testing/ README; CODEBASE_CONTEXT N/A (Testing/ is not Draft tech-stack/dir; PoC unpromoted) | Draft `git status` shows zero PoC files outside Testing/; only governance docs changed |
| Long-term spec / locked decision / architecture invariant change | dev/PROJECT_MASTER_SPEC.md (relevant §A–§G section); CODEBASE_CONTEXT.md Key Decisions if direction shifts; SESSION_HANDOFF.md if baseline affected | manual review |
| New cross-agent handoff knowledge doc added | CODEBASE_CONTEXT.md Directory Map + AI Maintenance Log; this registry (row presence); SESSION_HANDOFF/LOG | row presence check |
| Project relocation / repo absolute-path change | AGENTS.md header line 1 + §13 examples; SESSION_HANDOFF.md User Environment + Session Close Checklist; PROJECT_MASTER_SPEC.md §A.5; any *.py/*.sh with hardcoded abs path hints; SESSION_LOG/HANDOFF entry | grep "old path" returns only archive/log history |
| Doc-drift truth-pass / accuracy correction (a doc number/architecture statement found wrong vs actual code/data) | Correct every doc carrying the stale value (PROJECT_MASTER_SPEC / CODEBASE_CONTEXT / SESSION_HANDOFF as applicable); CODEBASE_CONTEXT AI Maintenance Log entry; dev/HANDOFF_PACKAGE.md §2/§5 if a verified-state value changed; SESSION_LOG drift table | re-verify corrected value against actual code/data |
| Freshness monitoring / CI workflow change (check_freshness.py, freshness_check.yml, freshness_metadata schema) | dev/source/FRESHNESS_GUIDE.md (rhythm + commands + detection model); CODEBASE_CONTEXT.md Directory Map if a script/field is added; SESSION_HANDOFF.md priorities/risks if operator flow changes; SESSION_LOG.md task entry + QC evidence | `--self-test` PASS + dry-run smoke; YAML parse |
| guidelines.json public contract / app.html GUIDELINES_REGISTRY change (the public endpoint is a derived projection of the registry — S140) | Regenerate `guidelines.json` via `dev/build_guidelines.py --write` (NEVER hand-edit); K1_API_SPEC.md (root + dev/) count/version; README.md guideline count; PROJECT_MASTER_SPEC §B.1 釐清框 if subset/drop policy changes; CODEBASE_CONTEXT.md guidelines.json line; SESSION_LOG/HANDOFF task entry | `build_guidelines.py --self-test` PASS (incl. no-prior-public-id-lost regression guard); JSON valid; per-topic counts |
| Channel-B vault source backfill / page-carry into Supabase (new or refreshed source via repage_pdfs.py + cb3_b2_pagecarry_migrate.py — S122-S141 recurring) | source_registry.json entry (source_type=pdf + direct url_primary + freshness_metadata); backend SOURCE_SETS / TOPIC_KEYWORDS / QUERY_EXPANSIONS parity if topic-routed (S135 backfill-allowlist coupling — new Supabase source does NOT surface until allowlisted); SESSION_HANDOFF.md Current Baseline (Supabase chunk count + marker-bearing count); SESSION_LOG.md task entry + Gate1/Gate2 evidence; CODEBASE_CONTEXT.md Directory Map (new vault dir) + AI Maintenance Log | repage Gate1 markers==pages; cb3_b2 Gate2 post-count==insert (del=0 for new source); typecheck+build exit 0; live smoke surfaces source with `=== Page N ===` + curriculum-route non-regression |

## Anti-pattern: No Matching Row

If your change has no matching row above:
- Do NOT skip silently — add the missing row first, then proceed
- Record the registry addition in SESSION_LOG under `Doc Sync: registry updated`
- Reason: a stale registry is worse than no registry (false safety net)
