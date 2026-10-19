## item_000_scope_reset_to_sharks_and_rename_to_lorenzini_track - Scope reset to sharks and rename to Lorenzini Track
> From version: 0.1.0
> Schema version: 1.0
> Status: In progress
> Understanding: 85%
> Confidence: 80%
> Progress: 10%
> Complexity: Medium
> Theme: General
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-10-19 14:57:46

# AI Context
- Summary: Cut the prototype to sharks only, rename poseidon to Lorenzini Track in code and docs, and get type-check, lint and backend tests green.
- Keywords: scope reset, sharks, rename, lorenzini track, cleanup, tests, tsc, ruff
- Use when: Removing non-shark code, renaming, or fixing the build and test baseline.
- Skip when: The work is about simulation, views or hosting.

# Problem
- The prototype covers five taxa (sharks, devil ray, turtles, grey seal, manatee, seabirds); most of it does not serve the shark-telemetry story.
- `poseidon` appears in the README, `backend/pyproject.toml`, `backend/app/main.py`, `backend/app/core/config.py`, `docker-compose.yml`, `frontend/index.html`, `frontend/src/App.tsx` (theme storage key), `frontend/src/components/Header.tsx` and `design-system/poseidon/`.
- `npm run build` fails at `tsc -b` (two errors in `frontend/src/components/MapView.tsx`); backend tests only run against a live PostGIS; `ruff check` has 27 findings.
- The README still says "no ingestion implemented".

# Scope
- In:
  - Remove non-shark ingestion scripts (`gbif_green_turtle`, `gbif_leatherback`, `gbif_grey_seal`, `gbif_manatee`, `gbif_seabirds_anguilla`, `gbif_devil_ray`), their entries in `app/data/species_facts.py`, colours and media.
  - Remove undersea POI markers (`underseaFeatures.ts`), taxon-family colouring and the 20k point caps.
  - Rename to Lorenzini Track across code, config, compose, design-system and docs; keep the local folder name.
  - Rewrite the README to the new framing (short; the case study comes in item_006).
  - Add a decision record in `docs/decisions/` recording the 2026-10-16 framing and superseding the interim flagship in 0002.
  - Fix the two `tsc -b` errors; make backend tests run against a disposable PostGIS; fix ruff findings.
- Out:
  - New features.
  - Reworking species profiles beyond removing non-shark entries (owner decision 2026-10-16: keep them for now).

# Acceptance criteria
- AC1: `grep -ri poseidon` outside `.git` finds no hits except references to the codename in history notes.
- AC2: `npm run build` and `oxlint` pass; `ruff check` is clean.
- AC3: Backend tests pass against a freshly migrated PostGIS started by one documented command.
- AC4: The map and lists show shark species only.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: contributes to a public demo that explores simulated shark tracks with visible uncertainty and sensitivity.
- request-AC2 -> This backlog slice. Proof: contributes to the documented tag-to-map path, licences and README.
- request-AC3 -> This backlog slice. Proof: linked to roadmap milestone 0.2 - Shark scope reset and rename.

# Decision framing
- Product framing: Covered by `prod_001_lorenzini_track_shark_telemetry_from_tag_to_map`
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_001_lorenzini_track_shark_telemetry_from_tag_to_map`
- Architecture decision(s): (none yet; see `docs/decisions/`)
- Request: `req_000_lorenzini_track_1_0_public_showcase`
- Primary task(s): (none yet)

# Priority
- Priority: High
- Rationale: Every later milestone builds on this; a broad multi-taxon base and a red type-check would leak into the demo.

# Tasks
- `task_001_scope_reset_to_sharks_and_rename_to_lorenzini_track`
