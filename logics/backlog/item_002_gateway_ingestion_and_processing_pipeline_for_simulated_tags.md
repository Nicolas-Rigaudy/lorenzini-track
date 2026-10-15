## item_002_gateway_ingestion_and_processing_pipeline_for_simulated_tags - Gateway, ingestion and processing pipeline for simulated tags
> From version: 0.1.0
> Schema version: 1.0
> Status: Ready
> Understanding: 85%
> Confidence: 80%
> Progress: 0%
> Complexity: High
> Theme: General
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.

# AI Context
- Summary: Gateway that decodes, deduplicates and timestamps raw simulated messages; ingestion into a telemetry schema in PostGIS; processing with quality filtering and track reconstruction.
- Keywords: gateway, ingestion, processing, postgis, alembic, telemetry schema, speed filter, track reconstruction
- Use when: Building the gateway, telemetry tables or processing steps.
- Skip when: The work is about the simulator itself or the frontend.

# Problem
- The current schema holds Darwin Core occurrences, not tag deployments, raw fixes and detections.
- There is no gateway or processing step between raw tag output and the map.

# Scope
- In:
  - A gateway process that reads raw messages (transport per owner decision: file/HTTP drop or MQTT), decodes, deduplicates and timestamps them.
  - Alembic migrations for deployments, raw satellite fixes (with location class) and acoustic detections, next to the existing Darwin Core tables, with a simulated flag.
  - Processing: speed and quality filter, track reconstruction, and a hook where item_003's sensitivity rules run.
  - One documented command that runs simulate → gateway → ingest → process locally.
  - Unit tests for decoding and processing; an integration test against a disposable PostGIS.
- Out:
  - Static export (item_005).
  - Real datasets (roadmap 1.2).

# Acceptance criteria
- AC1: One command takes a seed to processed tracks in PostGIS.
- AC2: Duplicate messages are stored once; malformed messages are logged and skipped.
- AC3: Processed tracks keep gaps as gaps and keep the location class of each fix.
- AC4: Every stored record carries the simulated flag.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: contributes to a public demo that explores simulated shark tracks with visible uncertainty and sensitivity.
- request-AC2 -> This backlog slice. Proof: contributes to the documented tag-to-map path, licences and README.
- request-AC3 -> This backlog slice. Proof: linked to roadmap milestone 0.3 - Simulated tag fleet and pipeline.

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
- Rationale: The tag-to-map pipeline is the engineering half of the story and feeds every later view.
