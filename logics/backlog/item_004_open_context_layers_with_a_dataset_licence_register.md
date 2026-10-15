## item_004_open_context_layers_with_a_dataset_licence_register - Open context layers with a dataset licence register
> From version: 0.1.0
> Schema version: 1.0
> Status: Ready
> Understanding: 85%
> Confidence: 80%
> Progress: 0%
> Complexity: Medium
> Theme: General
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-10-16 01:16:31

# AI Context
- Summary: OBIS/GBIF shark occurrences and one Copernicus Marine variable as context, with a licence register for every dataset, photo and basemap and on-map attribution.
- Keywords: obis, gbif, copernicus marine, sst, context, licence, attribution, register
- Use when: Adding a context layer or checking a dataset licence.
- Skip when: The work is about simulated telemetry.

# Problem
- Licences are recorded only partly, in decision records and ingestion code; the IMOS licence has not been checked against the source.
- No environmental layer exists yet.

# Scope
- In:
  - A licence register (one file in the repo) listing each dataset, photo and basemap: source URL, licence, attribution text, date checked.
  - OBIS/GBIF shark occurrences for the featured species and region, with per-record licences kept and a sampling-effort caveat in the UI.
  - One Copernicus Marine variable (sea surface temperature) for the fleet's region and period.
  - IMOS acoustic detections are dropped from 1.0 (owner decision 2026-10-16; real data comes with 1.2). Decide keep or drop for the whale shark 1° aggregated data as context; if kept, the sensitivity rules apply.
  - On-map attribution for every visible layer.
- Out:
  - More than one environmental variable in 1.0.

# Acceptance criteria
- AC1: Every dataset used by the demo has a register entry with a licence checked against the source.
- AC2: Every visible layer shows its attribution.
- AC3: The SST layer covers the simulated fleet's region and period.

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
- Priority: Medium
- Rationale: Context makes the tracks meaningful, and nothing can be published before its licence is known.
