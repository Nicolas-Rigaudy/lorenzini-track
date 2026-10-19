## item_000_scope_reset_to_sharks_and_rename_to_lorenzini_track - Scope reset to sharks and rename to Lorenzini Track
> From version: 0.1.0
> Schema version: 1.0
> Status: Done
> Understanding: 95%
> Confidence: 85%
> Progress: 100%
> Complexity: Medium
> Theme: General
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-10-19 14:57:46

# AI Context
- Summary: Make sharks the default view while keeping every other species behind a taxon-family filter, rename poseidon to Lorenzini Track in code and docs, and get type-check, lint and backend tests green.
- Keywords: scope reset, sharks first, taxon filter, taxon-family colours, rename, lorenzini track, tests, tsc, ruff
- Use when: Working on the default shark view, the taxon filter or colours, the rename, or the build and test baseline.
- Skip when: The work is about simulation, views or hosting.

# Problem
- The prototype covers six taxon families (sharks, a ray, turtles, a seal, a manatee, seabirds) with no hierarchy: a first-time visitor sees all of them at once, so the shark-telemetry story does not lead.
- `poseidon` appears in the README, `backend/pyproject.toml`, `backend/app/main.py`, `backend/app/core/config.py`, `docker-compose.yml`, `frontend/index.html`, `frontend/src/App.tsx` (theme storage key), `frontend/src/components/Header.tsx` and `design-system/poseidon/`.
- `npm run build` fails at `tsc -b` (two errors in `frontend/src/components/MapView.tsx`); backend tests only run against a live PostGIS; `ruff check` has 27 findings.
- The README still says "no ingestion implemented".

# Scope
- In:
  - Sharks as the default map and list view: a taxon-family filter, set to sharks on load, narrows the species gallery, the overview map pins, the studies list, the legend and the time-filter bounds; the other families and "all" stay one click away.
  - Keep and refine taxon-family colouring (one base hue per family, species as shades of it), folding in the leftover edits to `speciesColors.ts` and `speciesMedia.ts`.
  - Remove the 20k point caps (uncapped until tiles arrive in 0.5, owner 2026-10-19).
  - Rename to Lorenzini Track across code, config, compose, design-system and docs; keep the local folder name.
  - Rewrite the README to the new framing (short; the case study comes in item_006).
  - Decision records in `docs/decisions/`: 0007 records the 2026-10-16 framing and supersedes the interim flagship in 0002; 0008 records the 2026-10-19 scope (sharks lead, other species stay) and supersedes 0007's shark-only line.
  - Fix the two `tsc -b` errors; make backend tests run against a disposable PostGIS; fix ruff findings.
- Out:
  - Deleting species content: non-shark ingestion scripts, `species_facts.py` entries, colours and media all stay (owner decision 2026-10-19, replacing the shark-only cut of 2026-10-16).
  - Removing the undersea feature-name layer (`underseaFeatures.ts`): it is sea map detail, not species content. Land detail stays as is; the owner will judge it later.
  - Reworking species profiles (owner decision 2026-10-16: keep them for now).
  - Other new features.

# Acceptance criteria
- AC1: `grep -ri poseidon` outside `.git` finds no hits except references to the codename in history notes.
- AC2: `npm run build` and `oxlint` pass; `ruff check` is clean.
- AC3: Backend tests pass against a freshly migrated PostGIS started by one documented command.
- AC4: On first load the map and lists show shark species only; every other species stays reachable through a taxon-family filter, and no species content was deleted.
- AC5: Species are coloured by taxon family: each family has one base hue and its species are shades of it, and the same species keeps its colour whatever the filter.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: contributes to a public demo that explores simulated shark tracks with visible uncertainty and sensitivity.
- request-AC2 -> This backlog slice. Proof: contributes to the documented tag-to-map path, licences and README.
- request-AC3 -> This backlog slice. Proof: linked to roadmap milestone 0.2 - Sharks-first scope and rename.

# Decision framing
- Product framing: Covered by `prod_001_lorenzini_track_shark_telemetry_from_tag_to_map`
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_001_lorenzini_track_shark_telemetry_from_tag_to_map`
- Architecture decision(s): (none yet; see `docs/decisions/0007-lorenzini-track-framing.md` and `docs/decisions/0008-sharks-lead-other-species-kept.md`)
- Request: `req_000_lorenzini_track_1_0_public_showcase`
- Primary task(s): (none yet)

# Priority
- Priority: High
- Rationale: Every later milestone builds on this; a demo where sharks do not lead and a red type-check would leak into everything after.

# Tasks
- `task_001_scope_reset_to_sharks_and_rename_to_lorenzini_track`

# Notes
- Task `task_001_scope_reset_to_sharks_and_rename_to_lorenzini_track` was finished via `logics-manager flow finish task` on 2026-10-19.
