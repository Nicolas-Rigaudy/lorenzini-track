## task_003_gateway_ingestion_and_processing_pipeline_for_simulated_tags - Gateway, ingestion and processing pipeline for simulated tags
> From version: 0.1.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
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
- [ ] The backlog scope is implemented.
- [ ] Acceptance criteria are covered.
- [ ] Validation passes.
- [ ] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# Backlog
- `item_002_gateway_ingestion_and_processing_pipeline_for_simulated_tags`

# Acceptance criteria
- AC1: One command takes a seed to processed tracks in PostGIS.
- AC2: Duplicate messages are stored once; malformed messages are logged and skipped.
- AC3: Processed tracks keep gaps as gaps and keep the location class of each fix.
- AC4: Every stored record carries the simulated flag.

# Plan
- [ ] Decision record revising "no message bus" in docs/decisions/0001 (two transport networks).
- [ ] Mosquitto in docker-compose, next to PostGIS.
- [ ] Alembic migration and models: deployments, satellite fixes, acoustic detections, receiver statuses, Argos deliveries, track segments and points, all with a simulated flag.
- [ ] Transport: Argos batch inbox and MQTT replay publisher; gateway subscriber over MQTT.
- [ ] Store gateway output idempotently; processing writes tracks with gaps kept and a hook for item_003 rules.
- [ ] One command `python -m app.pipeline --seed N`, documented in the README.
- [ ] Integration test against the disposable PostGIS and Mosquitto.
- [ ] Use `python3 -m logics_manager flow progress task task_003_gateway_ingestion_and_processing_pipeline_for_simulated_tags.md --progress <n>%` during multi-wave work.
- [ ] Run `python3 -m logics_manager flow finish task task_003_gateway_ingestion_and_processing_pipeline_for_simulated_tags.md` after implementation.

# Validation
- (no validation recorded yet)

# Report
- Not started.

# Links
- Request: `req_000_lorenzini_track_1_0_public_showcase`
- Product brief(s): `prod_001_lorenzini_track_shark_telemetry_from_tag_to_map`
- Architecture decision(s): `adr_001_raw_tag_and_receiver_message_formats`
