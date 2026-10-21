## req_001_r_d_what_comes_next_after_the_1_0_demo_build_and_what_to_cut - R&D: what comes next after the 1.0 demo build and what to cut
> From version: 1.0.0
> Schema version: 1.0
> Status: Draft
> Understanding: 90%
> Confidence: 85%
> Complexity: Medium
> Theme: General
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.

# AI Context
- Summary: Research note, written 2026-10-22 with no code: what to do after the remaining 1.0 items, what to cut or defer, and what similar tools do. Backlog items named here are proposals, not created.
- Keywords: comes, next, after, demo, build, cut
- Use when: Choosing what to build after the 0.4/0.5 work, or deciding whether an idea belongs in 1.0.
- Skip when: You need execution details for an existing backlog item.

# Needs
- Decide the order of the work left to 1.0 and what to defer, from where the repo stands today.

# Context
State on 2026-10-22: 0.2 and 0.3 are met. 0.5 is about 70% (export, static build, manual Pages workflow; PMTiles, a real Pages run and drawing tracks open). 0.4 has the sensitivity rules (decision 0010, proposed) and the licence register; the visual half is open. Item_006 (README, live URL) waits for the live URL.

What similar tools do (from general knowledge, not re-checked tonight):
- Movebank, OBIS-SEAMAP and the Ocean Tracking Network publish tracks late and coarse, with an embargo. They show no uncertainty on the map and give a citation and licence per dataset. Neither the map nor the embargo reasoning is visible to the viewer.
- Global Fishing Watch and the Sea Around Us style viewers show one story per layer, a short methods panel and a data licence link per layer. They do not draw per-position error.
- Argos-based project pages (seaturtle.org STAT, WWF tracker pages) draw lines plus a location-class legend at best, and often delay positions by days.
So the gap this project fills is the visible uncertainty and sensitivity explanation. That is the part to protect.

# Findings and proposed priorities
Proposals only. No backlog item below exists yet.
1. Show the simulated hammerheads on the map (proposal P1, highest). The export already has `tracks.geojson` and nothing draws it, so the demo today shows no simulated shark at all. A 1.0 link without the fleet fails the exit signal. This needs a visual choice (lines with error circles, or points sized by class error); render both to PNG for the owner before building. Fold it into item_003 so tracks and uncertainty are designed together.
2. Run the Pages workflow once (P2). It is the only unexecuted step on the path to a live URL, and item_006 and the exit signal depend on it. It needs the owner: set Pages to the GitHub Actions source, then run it.
3. Cut the two large studies from the demo (P3). Seabirds (154 MB) and grey seal (74 MB) work against the sharks-first story and the load budget. Keep them in the database and the API mode, leave them out of the static export. This removes the PMTiles and tippecanoe dependency from 1.0 and defers it to after 1.0. Needs the owner's yes because it removes data from the demo.
4. Confirm decision 0010 (P4). The grid and delay values are a first proposal; the owner should accept or change the table before the explainer cites them.
5. One attribution control for all layers (P5). It needs the basemap, bathymetry and feature-name licences read at the source, then one panel that lists every visible layer. It closes AC2 of item_004 and costs little.
6. Defer or cut:
   - Copernicus SST: needs an account and a download pipeline for one decorative layer. Defer to 1.1 unless the owner wants it; the story works without it.
   - OBIS/GBIF shark occurrences as context: the demo already has the real shark datasets, so a second source adds a sampling-effort caveat to write and little to see. Defer.
   - Raw vs processed toggle: it requires exporting raw fixes, which cuts against the sensitivity message. Replace with a "rejected fixes" note in the explainer, or defer.
   - Keep 1.1 (edge device) and 1.2 (real dataset) after 1.0 as planned; neither blocks the demo.
7. Add a small safety check (proposal P6): a test that fails when an exported layer holds a position finer than its species' grid. It turns AC2 of item_003 into a regression test, and the export has no filter for the real occurrence layers yet (real datasets are not covered by the rules; the 1-degree datasets already are coarse, the biologging ones are not).

Order proposed: P2 and P4 (owner), P1 with P5, P6, then P3. Everything else after 1.0.

# Risks
- The real per-fix datasets (basking shark biologging, seals, seabirds) are published at full precision. The sensitivity rules cover only the simulated tracks. For a basking shark this matches the source's own CC BY-NC publication, but the explainer must not claim all layers are coarsened.
- CC BY-NC on nine datasets limits any later commercial use of the site.

# Acceptance criteria
- AC1: The note ranks what to do next and says what to cut, with reasons.
- AC2: Every proposal says whether it needs the owner.
- AC3: No backlog item is created until the owner accepts a proposal.

# Definition of Ready (DoR)
- [ ] Problem statement is explicit and user impact is clear.
- [ ] Scope boundaries (in/out) are explicit.
- [ ] Acceptance criteria are testable.
- [ ] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): (none yet)
- Architecture decision(s): (none yet)

# References
- `logics_manager/flow.py`
- `logics_manager/assist.py`
- `tests/python/test_logics_manager_cli.py`

# Backlog
- none
