## task_003_gateway_ingestion_and_processing_pipeline_for_simulated_tags - Gateway, ingestion and processing pipeline for simulated tags
> From version: 0.1.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Owner: Nicolas Rigaudy
> Indicators reviewed: 2026-10-21 17:39:54

# AI Context
- Summary: Deliver item_002: Argos-style batch deliveries and MQTT (Mosquitto) as the two transport networks, the gateway consuming both, telemetry tables in PostGIS with a simulated flag, speed/quality filtering and track reconstruction stored as segments, and one command from seed to processed tracks.
- Keywords: gateway, ingestion, processing, pipeline, simulated, tags
- Use when: Working on the gateway, the transport networks, the telemetry schema or the processing steps.
- Skip when: The work is about the simulator itself, the sensitivity rules (item_003) or the frontend.

# Definition of Done (DoD)
- [x] The backlog scope is implemented.
- [x] Acceptance criteria are covered.
- [x] Validation passes.
- [x] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# Backlog
- `item_002_gateway_ingestion_and_processing_pipeline_for_simulated_tags`

# Acceptance criteria
- AC1: One command takes a seed to processed tracks in PostGIS.
- AC2: Duplicate messages are stored once; malformed messages are logged and skipped.
- AC3: Processed tracks keep gaps as gaps and keep the location class of each fix.
- AC4: Every stored record carries the simulated flag.

# Plan
- [x] Decision record revising "no message bus" in docs/decisions/0001 (two transport networks).
- [x] Mosquitto in docker-compose, next to PostGIS.
- [x] Alembic migration and models: deployments, satellite fixes, acoustic detections, receiver statuses, Argos deliveries, track segments and points, all with a simulated flag.
- [x] Transport: Argos batch inbox and MQTT replay publisher; gateway subscriber over MQTT.
- [x] Store gateway output idempotently; processing writes tracks with gaps kept and a hook for item_003 rules.
- [x] One command `python -m app.pipeline --seed N`, documented in the README.
- [x] Integration test against the disposable PostGIS and Mosquitto.
- [ ] Use `python3 -m logics_manager flow progress task task_003_gateway_ingestion_and_processing_pipeline_for_simulated_tags.md --progress <n>%` during multi-wave work.
- [ ] Run `python3 -m logics_manager flow finish task task_003_gateway_ingestion_and_processing_pipeline_for_simulated_tags.md` after implementation.

# Validation
- `backend/scripts/test.sh`: 69 passed against a disposable PostGIS and Mosquitto (2026-10-21); `ruff check .` clean; files touched are `ruff format` clean.
- `alembic upgrade head`, `downgrade -1`, `upgrade head` and `alembic check` (no drift) on the new revision f7a53be12002.
- `docker compose up -d db mqtt && cd backend && python -m app.pipeline --seed 42`: 8 tracks, 81 segments, 334 points; a second run stores no new rows.
- Finish workflow executed on 2026-10-21.
- Linked backlog/request close verification passed.

# Report
- Transport networks recorded in `docs/decisions/0009-two-transport-networks.md` (revises the "no message bus" line behind 0001); Mosquitto in docker-compose (`mqtt`, plus `mqtt-test` for the tests).
- Gateway (`backend/app/gateway`): reads an Argos-style inbox and the MQTT broker (`transport.py`: inbox delivery, MQTT replay with the simulated publish time as an MQTT 5 user property, listener that waits for a replay-done count).
- Telemetry schema (revision f7a53be12002): `deployment`, `argos_delivery`, `satellite_fix` (location class, `qc` outcome), `acoustic_detection`, `receiver_status`, `track_segment`, `track_point`, each with `simulated`.
- Ingest and processing (`backend/app/pipeline`): `ON CONFLICT DO NOTHING` on the dedup keys; tracks rebuilt per platform, gaps over 48 h start a new segment; `app/processing/sensitivity.py` is the hook for item_003's rules (empty list for now).
- AC1: `test_one_command_takes_a_seed_to_tracks_in_postgis`. AC2: `test_duplicates_are_stored_once_and_a_rerun_adds_nothing`, `test_malformed_deliveries_are_logged_and_skipped`, `test_malformed_broker_messages_are_logged_and_skipped`. AC3: `test_tracks_keep_gaps_as_gaps_and_the_class_of_each_fix`, plus `test_processed_points_keep_the_published_error_of_their_class` for the 0.3 exit signal. AC4: `test_every_stored_record_is_flagged_simulated`.
- Observed: with the default fleet, Argos fixes are sparse (about one per shark every nine days), so most segments hold one or two points under the 48 h gap assumption.
- Finished on 2026-10-21.
- Linked backlog item(s): `item_002_gateway_ingestion_and_processing_pipeline_for_simulated_tags`
- Related request(s): `req_000_lorenzini_track_1_0_public_showcase`

# Links
- Request: `req_000_lorenzini_track_1_0_public_showcase`
- Product brief(s): `prod_001_lorenzini_track_shark_telemetry_from_tag_to_map`
- Architecture decision(s): `adr_001_raw_tag_and_receiver_message_formats`
