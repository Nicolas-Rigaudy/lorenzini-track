## item_006_case_study_readme_live_url_and_licence - Case-study README, live URL and licence
> From version: 0.1.0
> Schema version: 1.0
> Status: Ready
> Understanding: 85%
> Confidence: 80%
> Progress: 0%
> Complexity: Low
> Theme: General
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-10-16 01:16:31

# AI Context
- Summary: Case-study README opening with the agreed line and the Lorenzini note, live URL, LICENSE, third-party licences and repo metadata.
- Keywords: readme, case study, live url, license, mit, cc by, portfolio
- Use when: Writing the public README or choosing the licence.
- Skip when: The work is about code.

# Problem
- The README describes the codename project and an old status.
- There is no LICENSE file.

# Scope
- In:
  - README opening: "Lorenzini Track: an open research project on shark telemetry, from tag to map", then one line on Stefano Lorenzini, who in 1678 described the ampullae of Lorenzini, the organs sharks use to sense faint electric fields.
  - Case study: problem, why simulated, tag-to-map architecture, uncertainty and sensitivity, limits, what is next; screenshots or a short capture.
  - LICENSE: MIT for code and CC BY 4.0 for docs and simulated data (owner confirmed 2026-10-16); README states the demo is non-commercial because of CC BY-NC inputs.
  - Third-party data licences and the non-commercial note, linking the register from item_004.
  - Live URL in the README and the GitHub About field; repo description and topics.
- Out:
  - Marketing copy or a separate website.

# Acceptance criteria
- AC1: The README opens with the agreed line and the Lorenzini note, with no gimmicky copy.
- AC2: A LICENSE file exists with the owner-confirmed licence.
- AC3: The live URL works from the README and the About field.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: contributes to a public demo that explores simulated shark tracks with visible uncertainty and sensitivity.
- request-AC2 -> This backlog slice. Proof: contributes to the documented tag-to-map path, licences and README.
- request-AC3 -> This backlog slice. Proof: linked to roadmap milestone 1.0 - Public showcase.

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
- Rationale: The README and live link are the 1.0 deliverable a reader actually sees.
