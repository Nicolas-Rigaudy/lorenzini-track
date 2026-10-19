## item_001_simulated_shark_tag_fleet - Simulated shark tag fleet
> From version: 0.1.0
> Schema version: 1.0
> Status: In progress
> Understanding: 85%
> Confidence: 80%
> Progress: 10%
> Complexity: High
> Theme: General
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-10-19 16:29:45

# AI Context
- Summary: A seeded simulator that moves sharks with published movement models and samples them like real satellite and acoustic tags, emitting raw tag and receiver messages.
- Keywords: simulation, movement model, random walk, argos, location class, acoustic, receiver, duty cycle, battery, gaps
- Use when: Building or tuning the tag simulator or its message formats.
- Skip when: The work is about the gateway, storage or the map.

# Problem
- Real shark tracking data is mostly access-restricted (`docs/decisions/0004-no-live-tracking-data.md`), so the demo needs realistic simulated telemetry.
- Nothing in the repo simulates movement or tag behaviour yet.

# Scope
- In:
  - Movement from published shark movement models (for example behavioural-state correlated random walks), with each parameter cited.
  - Fin-mounted satellite tags: fixes only when the fin breaks the surface; Argos location classes (3, 2, 1, 0, A, B, Z) with class-dependent error.
  - Acoustic tags: detections only near receivers of a defined array, with detection probability falling with range.
  - Duty cycles, battery drain, transmission gaps, early failure.
  - Raw output as tag-like and receiver-like messages (formats fixed here, consumed by item_002); every record flagged as simulated.
  - Deterministic from a seed; unit tests for movement and sampling.
- Out:
  - Gateway, storage and processing (item_002).
  - Hardware (roadmap 1.1).

# Acceptance criteria
- AC1: The same seed produces byte-identical output.
- AC2: Error by location class and the share of each class match the ranges given in the cited sources.
- AC3: Acoustic detection rate falls with distance to the receiver as configured.
- AC4: A tag's message count stops when its battery model is exhausted.

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
- Rationale: The simulated fleet is the core of the showcase and the source of every track in the demo.

# Tasks
- `task_002_simulated_shark_tag_fleet`
