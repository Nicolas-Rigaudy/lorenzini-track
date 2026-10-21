## task_005_telemetry_uncertainty_and_data_sensitivity_views - Telemetry uncertainty and data-sensitivity views
> From version: 0.1.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 30%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Owner: night
> Indicators reviewed: 2026-10-22 00:47:50

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: telemetry, uncertainty, data, sensitivity, views
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Definition of Done (DoD)
- [ ] The backlog scope is implemented.
- [ ] Acceptance criteria are covered.
- [ ] Validation passes.
- [ ] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# Backlog
- `item_003_telemetry_uncertainty_and_data_sensitivity_views`

# Acceptance criteria
- AC1: Selecting any position shows its location class or detection range, its precision level and why.
- AC2: No exported layer contains positions finer than the rule for that species allows.
- AC3: Simulated layers are labelled as simulated in the legend and in each popup.

# Plan
- [ ] Use `python3 -m logics_manager flow progress task task_005_telemetry_uncertainty_and_data_sensitivity_views.md --progress <n>%` during multi-wave work.
- [ ] Run `python3 -m logics_manager flow finish task task_005_telemetry_uncertainty_and_data_sensitivity_views.md` after implementation.

# Validation
- (no validation recorded yet)

# Report
- 2026-10-22: sensitivity rules done (`app/processing/sensitivity.py`, decision 0010 proposed): grid coarsening by IUCN status, embargo with a reference time, default CR for the simulated fleet. Backend tests pass (79).
- Left: error circles, receiver ranges, raw vs processed toggle, per-point explainer and the simulated label in popups. All are visual choices and wait for the owner. Raw fixes are not exported yet, so the toggle also needs an export decision.
- Not started.

# Links
- Request: `req_000_lorenzini_track_1_0_public_showcase`
- Product brief(s): (none yet)
- Architecture decision(s): (none yet)
