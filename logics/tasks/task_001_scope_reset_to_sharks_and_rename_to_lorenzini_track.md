## task_001_scope_reset_to_sharks_and_rename_to_lorenzini_track - Scope reset to sharks and rename to Lorenzini Track
> From version: 0.1.0
> Schema version: 1.0
> Status: Done
> Understanding: 95%
> Confidence: 85%
> Progress: 100%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Owner: Nicolas Rigaudy
> Indicators reviewed: 2026-10-19 14:57:46

# AI Context
- Summary: Deliver item_000: make sharks the default view with other species behind a taxon-family filter, keep and refine taxon-family colours, rename poseidon to Lorenzini Track, and get tsc, oxlint, ruff and backend tests green on a disposable PostGIS.
- Keywords: scope, sharks first, taxon filter, colours, rename, lorenzini, track
- Use when: Working on the 0.2 sharks-first scope, the rename or the build/test baseline.
- Skip when: The work is about the simulator, pipeline, views or hosting.

# Definition of Done (DoD)
- [x] The backlog scope is implemented.
- [x] Acceptance criteria are covered.
- [x] Validation passes.
- [x] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# Backlog
- `item_000_scope_reset_to_sharks_and_rename_to_lorenzini_track`

# Acceptance criteria
- AC1: `grep -ri poseidon` outside `.git` finds no hits except references to the codename in history notes.
- AC2: `npm run build` and `oxlint` pass; `ruff check` is clean.
- AC3: Backend tests pass against a freshly migrated PostGIS started by one documented command.
- AC4: On first load the map and lists show shark species only; every other species stays reachable through a taxon-family filter, and no species content was deleted.
- AC5: Species are coloured by taxon family: each family has one base hue and its species are shades of it, and the same species keeps its colour whatever the filter.

# Plan
- [x] Use `python3 -m logics_manager flow progress task task_001_scope_reset_to_sharks_and_rename_to_lorenzini_track.md --progress <n>%` during multi-wave work.
- [x] Run `python3 -m logics_manager flow finish task task_001_scope_reset_to_sharks_and_rename_to_lorenzini_track.md` after implementation.

# Validation
- 2026-10-19: `cd frontend && npm run build` (tsc -b + vite build) passed; `oxlint` exit 0.
- 2026-10-19: `cd backend && ruff check .` clean.
- 2026-10-19: backend tests 7 passed against a fresh tmpfs PostGIS (postgis/postgis:16-3.4 on port 5433, migrated by `tests/conftest.py`). Run via `docker run --network host` because Docker bridge networking is broken on the dev machine (running kernel 7.2.8 has no installed modules, so no veth); `backend/scripts/test.sh` itself (compose `db-test`) still needs a run after a reboot.
- 2026-10-19 (after the owner decisions): `npm run build` and `oxlint` pass, `ruff check .` clean and backend tests 7 passed on a fresh host-network PostGIS before each commit (64bb180, 333234b, ed9ee5c).
- 2026-10-19: AC3, the flow of `backend/scripts/test.sh` (compose `db-test`, wait for health, pytest, remove) passed (7 tests) with one compose override file that only sets `network_mode: host` and port 5433, since bridge networking still fails on this machine (running kernel 7.2.8, modules for 7.2.9 installed). An unmodified run needs a reboot.
- 2026-10-19: AC1, `grep -ri poseidon` outside `.git` hits only history notes (decision 0007 and Logics docs) once the stale, gitignored `backend/poseidon_backend.egg-info` was removed.
- 2026-10-19: AC4/AC5 checked in a headless browser against the 0.1 dev database (19 species, 11 studies): first load shows Sharks (9 species, 5 studies, 2007-2024) with all shark pins framed; Seabirds, Turtles and All narrow or widen the gallery, pins, studies, legend and time bounds; a bull shark selection draws all 83,832 points; dark mode checked. Only failed requests: Wikipedia summary 404 for `Trichechus manatus latirostris` (no page for the subspecies, so the manatee pin has no photo; predates this task). Legend shades: sharks blue band, other families on their own hues, colours unchanged across filters.
- Finish workflow executed on 2026-10-19.
- Linked backlog/request close verification passed.

# Report
- Done: MapView type errors fixed (0aa31d9); ruff clean (7c7f45e); disposable test PostGIS + `backend/scripts/test.sh` (4063195); point caps removed (3d47916); rename in code, config, compose, design system (01d5e63); decision 0007 superseding 0002 (7fd24f4); README rewritten (6707950).
- 2026-10-19 owner decisions (decision 0008) replaced the shark-only cut: sharks lead, other species stay behind a taxon-family filter, nothing species-related is deleted, the undersea feature layer stays, points stay uncapped until 0.5. The undersea removal patch was not used.
- Done after the decisions: docs reframed (roadmap, brief, request, item_000, this task, README, decision 0008; 64bb180); taxon-family colours tightened with interleaved shades and the old-session `speciesColors.ts` / `speciesMedia.ts` edits folded in (tiger shark size diagram URL checked, 200; 333234b); taxon-family filter in the header, opening on sharks, narrowing gallery, overview pins, studies, legend and time bounds, with the overview framed on the visible family (ed9ee5c).
- 2026-10-19 owner change: sharks use a fixed 10-colour blue→cyan ramp assigned in legend order (each ≥3:1 on light and dark panels, neighbours clearly distinct); other families keep their single hue.
- Left for later items: none from item_000. Unmodified `backend/scripts/test.sh` run waits for a reboot of the dev machine.
- Finished on 2026-10-19.
- Linked backlog item(s): `item_000_scope_reset_to_sharks_and_rename_to_lorenzini_track`
- Related request(s): `req_000_lorenzini_track_1_0_public_showcase`

# AC Traceability
- request-AC1 -> This task. Proof: groundwork only; the default view now opens on sharks with every other species behind the taxon filter (checked in a headless browser, see Validation), the base the simulated-track demo builds on.
- request-AC2 -> This task. Proof: groundwork only; rename and README rewrite done, `npm run build`, `oxlint`, `ruff check` green and backend tests runnable on a disposable PostGIS via `backend/scripts/test.sh` (see Validation).
- request-AC3 -> This task. Proof: item_000 is linked to roadmap milestone 0.2 (Sharks-first scope and rename) in `road_001_lorenzini_track_to_1_0`.

# Links
- Request: `req_000_lorenzini_track_1_0_public_showcase`
- Product brief(s): (none yet)
- Architecture decision(s): (none yet)
