## task_001_scope_reset_to_sharks_and_rename_to_lorenzini_track - Scope reset to sharks and rename to Lorenzini Track
> From version: 0.1.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 80%
> Progress: 60%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Owner: Nicolas Rigaudy
> Indicators reviewed: 2026-10-19 14:57:46

# AI Context
- Summary: Deliver item_000: cut the prototype to sharks, rename poseidon to Lorenzini Track, and get tsc, oxlint, ruff and backend tests green on a disposable PostGIS.
- Keywords: scope, reset, sharks, rename, lorenzini, track
- Use when: Working on the 0.2 shark scope reset, the rename or the build/test baseline.
- Skip when: The work is about the simulator, pipeline, views or hosting.

# Definition of Done (DoD)
- [ ] The backlog scope is implemented.
- [ ] Acceptance criteria are covered.
- [ ] Validation passes.
- [ ] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# Backlog
- `item_000_scope_reset_to_sharks_and_rename_to_lorenzini_track`

# Acceptance criteria
- AC1: `grep -ri poseidon` outside `.git` finds no hits except references to the codename in history notes.
- AC2: `npm run build` and `oxlint` pass; `ruff check` is clean.
- AC3: Backend tests pass against a freshly migrated PostGIS started by one documented command.
- AC4: The map and lists show shark species only.

# Plan
- [ ] Use `python3 -m logics_manager flow progress task task_001_scope_reset_to_sharks_and_rename_to_lorenzini_track.md --progress <n>%` during multi-wave work.
- [ ] Run `python3 -m logics_manager flow finish task task_001_scope_reset_to_sharks_and_rename_to_lorenzini_track.md` after implementation.

# Validation
- 2026-10-19: `cd frontend && npm run build` (tsc -b + vite build) passed; `oxlint` exit 0.
- 2026-10-19: `cd backend && ruff check .` clean.
- 2026-10-19: backend tests 7 passed against a fresh tmpfs PostGIS (postgis/postgis:16-3.4 on port 5433, migrated by `tests/conftest.py`). Run via `docker run --network host` because Docker bridge networking is broken on the dev machine (running kernel 7.2.8 has no installed modules, so no veth); `backend/scripts/test.sh` itself (compose `db-test`) still needs a run after a reboot.

# Report
- Done: MapView type errors fixed (0aa31d9); ruff clean (7c7f45e); disposable test PostGIS + `backend/scripts/test.sh` (4063195); point caps removed (3d47916); rename in code, config, compose, design system (01d5e63); decision 0007 superseding 0002 (7fd24f4); README rewritten (6707950).
- Blocked, owner decision needed: deleting non-shark content (the six non-shark ingestion scripts, non-shark `species_facts.py` entries, `underseaFeatures.ts` and its layer). The undersea edit is ready as a patch but needs the file deletion to build.
- Blocked, owner file: taxon-family colouring lives in `frontend/src/speciesColors.ts`, which has uncommitted owner edits; `speciesMedia.ts` already holds shark entries only.
- Not yet: AC4 check on a fresh database loaded with the shark scripts only, and a visual check of the UI.

# Links
- Request: `req_000_lorenzini_track_1_0_public_showcase`
- Product brief(s): (none yet)
- Architecture decision(s): (none yet)
