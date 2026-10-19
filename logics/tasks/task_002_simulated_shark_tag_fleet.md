## task_002_simulated_shark_tag_fleet - Simulated shark tag fleet
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
> Indicators reviewed: 2026-10-19 16:29:45

# AI Context
- Summary: Deliver item_001: a seeded, stdlib-only simulator of scalloped hammerheads off eastern Australia with fin-mounted Argos tags and acoustic tags, emitting Argos-style batch deliveries and MQTT-style receiver messages in documented raw formats for item_002.
- Keywords: simulated, shark, tag, fleet, argos, location class, acoustic, receiver, battery, duty cycle, seed, message format
- Use when: Working on the simulator, its parameters and sources, or the raw message formats.
- Skip when: The work is about the gateway, storage, processing or the map (item_002 onwards).

# Definition of Done (DoD)
- [ ] The backlog scope is implemented.
- [ ] Acceptance criteria are covered.
- [ ] Validation passes.
- [ ] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# Backlog
- `item_001_simulated_shark_tag_fleet`

# Acceptance criteria
- AC1: The same seed produces byte-identical output.
- AC2: Error by location class and the share of each class match the ranges given in the cited sources.
- AC3: Acoustic detection rate falls with distance to the receiver as configured.
- AC4: A tag's message count stops when its battery model is exhausted.

# Plan
- [ ] Use `python3 -m logics_manager flow progress task task_002_simulated_shark_tag_fleet.md --progress <n>%` during multi-wave work.
- [ ] Run `python3 -m logics_manager flow finish task task_002_simulated_shark_tag_fleet.md` after implementation.

# Validation
- (no validation recorded yet)

# Report
- Not started.

# Links
- Request: `req_000_lorenzini_track_1_0_public_showcase`
- Product brief(s): `prod_001_lorenzini_track_shark_telemetry_from_tag_to_map`
- Architecture decision(s): (none yet)
