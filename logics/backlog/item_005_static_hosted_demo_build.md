## item_005_static_hosted_demo_build - Static hosted demo build
> From version: 0.1.0
> Schema version: 1.0
> Status: In progress
> Understanding: 85%
> Confidence: 80%
> Progress: 70%
> Complexity: Medium
> Theme: General
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-10-21 21:22:11

# AI Context
- Summary: Export processed, sensitivity-filtered data to GeoJSON and PMTiles, switch the frontend to static files, replace the bathymetry proxy, and deploy from CI to GitHub Pages or Cloudflare Pages.
- Keywords: static, export, geojson, pmtiles, github pages, cloudflare pages, ci, deploy
- Use when: Building the export, the static data mode or the deploy pipeline.
- Skip when: The work is about data processing or views.

# Problem
- The frontend fetches everything from the FastAPI backend, including bathymetry tiles through a proxy (`backend/app/api/routes/tiles.py`).
- There is no hosting or deploy pipeline.

# Scope
- In:
  - An export command from PostGIS to GeoJSON and PMTiles, after sensitivity rules.
  - A data-source switch in the frontend (static files for the demo, API for local work).
  - A static-compatible bathymetry layer or its removal.
  - CI that builds and deploys; a size and load-time budget; HTTP range support for PMTiles checked on the chosen host.
- Out:
  - A hosted API or database.

# Acceptance criteria
- AC1: The deployed site works with the backend stopped.
- AC2: First load stays under five seconds on a normal connection.
- AC3: A push to master rebuilds and redeploys the site.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: contributes to a public demo that explores simulated shark tracks with visible uncertainty and sensitivity.
- request-AC2 -> This backlog slice. Proof: contributes to the documented tag-to-map path, licences and README.
- request-AC3 -> This backlog slice. Proof: linked to roadmap milestone 0.5 - Static hosted demo.

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
- Rationale: 1.0 needs a demo that stays online without a server.

# Tasks
- `task_004_static_hosted_demo_build`
