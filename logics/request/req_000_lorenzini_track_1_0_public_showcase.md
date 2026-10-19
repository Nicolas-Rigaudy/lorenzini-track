## req_000_lorenzini_track_1_0_public_showcase - Lorenzini Track 1.0 public showcase
> From version: 0.1.0
> Schema version: 1.0
> Status: Draft
> Understanding: 85%
> Confidence: 80%
> Complexity: High
> Theme: General
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.
> Indicators reviewed: 2026-10-19 16:03:21

# AI Context
- Summary: Umbrella request to take the codename "poseidon" multi-taxon marine explorer to Lorenzini Track 1.0, a shark-telemetry portfolio showcase: a clearly labelled simulated tag fleet feeding a gateway, ingestion and processing pipeline, uncertainty and data-sensitivity views, open context layers, and a static hosted demo with a case-study README.
- Keywords: lorenzini track, sharks, telemetry, simulation, argos, acoustic, pipeline, sensitivity, static demo, pmtiles, portfolio, 1.0
- Use when: Scoping or sequencing work on the path to the Lorenzini Track 1.0 public showcase.
- Skip when: You need details of a single change; read the linked backlog item instead.

# Needs
- The project is a portfolio showcase for the owner, an IoT engineer who wants to move into marine-conservation tech. It must tell one clear story: shark telemetry, from tag to map.
- Today it is a broad marine-wildlife explorer (sharks, rays, turtles, seals, manatees, seabirds) with no simulation, no uncertainty view and no hosting. Sharks have to lead: they become the default view, and the other species stay in the data and the UI behind a taxon-family filter (owner decision 2026-10-19, `docs/decisions/0008-sharks-lead-other-species-kept.md`); parts that do not fit the static demo have to be reworked.
- Real shark tracking data is mostly access-restricted, partly on purpose (location data of endangered species is sensitive, see `docs/decisions/0004-no-live-tracking-data.md`). The core therefore has to be a realistic, clearly labelled simulated tag fleet, with open occurrence and environmental data only as context.
- 1.0 is a public showcase, not an installable product: a live demo link plus a case-study README. No server should need to stay alive.

# Context
- Owner framing decided 2026-10-16 (see `prod_001_lorenzini_track_shark_telemetry_from_tag_to_map`); the GitHub repo was renamed to github.com/Nicolas-Rigaudy/lorenzini-track the same day; the local folder stays `poseidon`.
- Current state (last commit 7a1b433, 2026-10): FastAPI + SQLAlchemy/GeoAlchemy2 + Alembic backend over PostGIS with `study` and `occurrence` tables, eleven Darwin Core ingestion scripts (GBIF/STAT archives, IMOS ATF acoustic sharks, a CSV reader) feeding a shared loader; React 19 + Vite + MapLibre frontend with species/study panels, per-organism tracks, a time filter, species profiles with photos and size diagrams, dark mode, and an EMODnet bathymetry layer proxied through the backend.
- Checks on 2026-10-16: `vite build` succeeds, `oxlint` is clean, but `npm run build` fails at `tsc -b` with two errors in `frontend/src/components/MapView.tsx` (TS2352 on the colour `match` expression, TS18047 on `mapRef.current`). The seven backend tests are integration tests against a live PostGIS and could not run here (no database); `ruff check` reports 27 findings.
- Decision records stay in `docs/decisions/` (0001 to 0008); research in `docs/research/`.
- Roadmap: `road_001_lorenzini_track_to_1_0`; its Sequencing and Risks sections list the dependencies between milestones and the known risks (simulation realism, sensitive real positions, CC BY-NC inputs, static-hosting limits, scope creep).

# Acceptance criteria
- AC1: A visitor opens a public URL and, without any backend running, explores simulated shark tracks with visible Argos/acoustic uncertainty, sensitivity-aware precision, and open context layers, and every simulated element is labelled as simulated.
- AC2: The repository shows the full tag → gateway → ingestion → processing → static export path, runnable locally, with a case-study README, a licence file and a licence record for every third-party dataset.
- AC3: The work is split into backlog items linked to versioned roadmap milestones.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_001_lorenzini_track_shark_telemetry_from_tag_to_map`
- Architecture decision(s): (none yet; existing records live in `docs/decisions/`)

# References
- `README.md`
- `docs/decisions/0001-product-direction.md`
- `docs/decisions/0004-no-live-tracking-data.md`
- `docs/decisions/0005-study-exploration-and-iot-showcase-refinement.md`
- `docs/research/06-scientific-considerations.md`
- `backend/app/ingestion/loader.py`
- `backend/app/models/occurrence.py`
- `frontend/src/components/MapView.tsx`

# Backlog
- `item_000_scope_reset_to_sharks_and_rename_to_lorenzini_track`
- `item_001_simulated_shark_tag_fleet`
- `item_002_gateway_ingestion_and_processing_pipeline_for_simulated_tags`
- `item_003_telemetry_uncertainty_and_data_sensitivity_views`
- `item_004_open_context_layers_with_a_dataset_licence_register`
- `item_005_static_hosted_demo_build`
- `item_006_case_study_readme_live_url_and_licence`
