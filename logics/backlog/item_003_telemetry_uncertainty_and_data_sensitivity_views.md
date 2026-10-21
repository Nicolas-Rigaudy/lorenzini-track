## item_003_telemetry_uncertainty_and_data_sensitivity_views - Telemetry uncertainty and data-sensitivity views
> From version: 0.1.0
> Schema version: 1.0
> Status: In progress
> Understanding: 85%
> Confidence: 80%
> Progress: 30%
> Complexity: Medium
> Theme: General
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-10-22 00:47:50

# AI Context
- Summary: Map views for Argos-class error, acoustic receiver ranges and gaps, plus sensitivity rules (precision levels, publication delay, coarsening by conservation status) applied in processing, with an in-product explainer.
- Keywords: uncertainty, argos error, acoustic range, gaps, sensitivity, precision, embargo, coarsening, iucn
- Use when: Building the uncertainty layers, the sensitivity rules or the explainer.
- Skip when: The work is about context datasets or hosting.

# Problem
- Tracks are drawn as exact lines; nothing shows how uncertain a position is.
- Shark positions are sensitive (`docs/decisions/0004-no-live-tracking-data.md`), and the project has no rule for what precision may be published.

# Scope
- In:
  - Error radius or ellipse per Argos class; acoustic detections drawn as receiver ranges; gaps drawn as gaps; raw vs processed toggle.
  - Sensitivity rules in processing: precision levels, publication delay, coarsening driven by IUCN status, applied to every animal-position layer including real ones.
  - An explainer in the UI on why positions are coarsened or delayed, citing the sources in decision 0004.
  - A persistent "simulated" label on simulated layers.
- Out:
  - Context layers (item_004).

# Acceptance criteria
- AC1: Selecting any position shows its location class or detection range, its precision level and why.
- AC2: No exported layer contains positions finer than the rule for that species allows.
- AC3: Simulated layers are labelled as simulated in the legend and in each popup.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: contributes to a public demo that explores simulated shark tracks with visible uncertainty and sensitivity.
- request-AC2 -> This backlog slice. Proof: contributes to the documented tag-to-map path, licences and README.
- request-AC3 -> This backlog slice. Proof: linked to roadmap milestone 0.4 - Uncertainty, sensitivity and context.

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
- Rationale: Visible uncertainty and sensitivity handling are what set the project apart from a plain track map.

# Tasks
- `task_005_telemetry_uncertainty_and_data_sensitivity_views`
