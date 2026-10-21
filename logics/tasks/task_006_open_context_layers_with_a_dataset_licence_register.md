## task_006_open_context_layers_with_a_dataset_licence_register - Open context layers with a dataset licence register
> From version: 0.1.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 25%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Owner: night
> Indicators reviewed: 2026-10-22 00:49:17

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: open, context, layers, dataset, licence, register
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Definition of Done (DoD)
- [ ] The backlog scope is implemented.
- [ ] Acceptance criteria are covered.
- [ ] Validation passes.
- [ ] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# Backlog
- `item_004_open_context_layers_with_a_dataset_licence_register`

# Acceptance criteria
- AC1: Every dataset used by the demo has a register entry with a licence checked against the source.
- AC2: Every visible layer shows its attribution.
- AC3: The SST layer covers the simulated fleet's region and period.

# Plan
- [ ] Use `python3 -m logics_manager flow progress task task_006_open_context_layers_with_a_dataset_licence_register.md --progress <n>%` during multi-wave work.
- [ ] Run `python3 -m logics_manager flow finish task task_006_open_context_layers_with_a_dataset_licence_register.md` after implementation.

# Validation
- (no validation recorded yet)

# Report
- 2026-10-22: `docs/licence-register.md` written: eleven real datasets read from the IPT EML or GBIF record, five curated Wikimedia files read from the Commons API. AC1 holds for datasets and curated photos, not yet for basemap, bathymetry, feature names and Wikipedia content (marked "to check").
- Left: on-map attribution for every layer (visual), OBIS/GBIF shark context layer, Copernicus SST (needs a Copernicus Marine account, owner), keep or drop the whale shark aggregated data as context (product decision).
- Not started.

# Links
- Request: `req_000_lorenzini_track_1_0_public_showcase`
- Product brief(s): (none yet)
- Architecture decision(s): (none yet)
