## task_004_static_hosted_demo_build - Static hosted demo build
> From version: 0.1.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 70%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Owner: Nicolas Rigaudy
> Indicators reviewed: 2026-10-21 21:22:11

# AI Context
- Summary: Deliver item_005: export the database to static files, add a static build mode to the frontend, load bathymetry without the proxy, and a manual GitHub Pages workflow under /lorenzini-track/.
- Keywords: static, hosted, demo, build
- Use when: Working on the export command, the static build mode or the Pages workflow.
- Skip when: The work is about data processing, sensitivity rules or map views.

# Definition of Done (DoD)
- [ ] The backlog scope is implemented.
- [ ] Acceptance criteria are covered.
- [ ] Validation passes.
- [ ] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# Backlog
- `item_005_static_hosted_demo_build`

# Acceptance criteria
- AC1: The deployed site works with the backend stopped.
- AC2: First load stays under five seconds on a normal connection.
- AC3: A push to master rebuilds and redeploys the site.

# Plan
- [x] `python -m app.export`: studies, species, per-study occurrences and processed tracks as JSON/GeoJSON, with a manifest and a gzip budget for the first-load files.
- [x] Frontend static mode (`VITE_STATIC=1`, `VITE_BASE`): one data-source module for API or files; bathymetry straight from EMODnet (it sends CORS headers).
- [x] `.github/workflows/pages.yml`, `workflow_dispatch` only (owner decision 2026-10-21: nothing publishes on push).
- [x] Local static preview checked in a browser with the backend stopped.
- [ ] PMTiles for the two large occurrence files (a 154 MB and a 74 MB GeoJSON, 7 MB and 3 MB gzipped): needs tippecanoe, not installed here.
- [ ] Run the workflow once on GitHub, check HTTP range support on Pages, measure first load there.
- [ ] Render the exported tracks on the map (a visual change; waits for item_003's views).

# Validation
- `backend/scripts/test.sh`: 72 passed (3 new export tests); `ruff check` and `ruff format --check` clean on the new files.
- `tsc -b`, `oxlint`, `npm run build` and `VITE_STATIC=1 VITE_BASE=/lorenzini-track/ npm run build` pass.
- Static preview (`vite preview`, base /lorenzini-track/): first load 3.1 s with the backend stopped, no failed requests, no call to the API; study and species selection load their files.

# Report
- AC1 met locally. AC2 met locally (3.1 s, first-load data 6 KB gzipped, script 345 KB gzipped); to re-measure on Pages. AC3 not met on purpose: the owner decided on a manual workflow only.
- The sensitivity rules list is still empty (item_003), so the export applies no rule beyond reading `track_segment` and `track_point`; it never exports raw fixes.
- Large non-shark studies (seabirds, grey seal) stay heavy on selection; PMTiles is the open follow-up.

# Links
- Request: `req_000_lorenzini_track_1_0_public_showcase`
- Product brief(s): (none yet)
- Architecture decision(s): (none yet)
