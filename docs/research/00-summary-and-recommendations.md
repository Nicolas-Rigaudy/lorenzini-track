# 00 — Research Summary & Recommendations

Status: draft — end of research phase. This is the synthesis deliverable requested in the project
kickoff. **No application code has been written.** This document exists to be reviewed and
challenged before any implementation begins.

Full supporting detail lives in:
- [01 — Existing Platforms](01-existing-platforms.md)
- [02 — Datasets and APIs](02-datasets-and-apis.md)
- [03 — Data Standards](03-data-standards.md)
- [04 — Existing Open Source](04-existing-open-source.md)
- [05 — Product Opportunities](05-product-opportunities.md)
- [06 — Scientific Considerations](06-scientific-considerations.md)
- [07 — Technical Options](07-technical-options.md)

---

## 1. Summary of the existing ecosystem

Three distinct clusters of platforms exist, and none of them overlap much:

- **Storytelling/tracking platforms** (OCEARCH) — public-facing, narrow taxonomically, closed
  data, excellent UX/engagement, no environmental integration or uncertainty framing.
- **Research infrastructure** (Movebank, OTN, ATN) — deep, broad, scientifically serious data
  platforms, but access-gated per study, research-UX rather than public-explorer UX, and largely
  siloed from environmental context.
- **Biodiversity/environmental data backbones** (OBIS, GBIF, EMODnet, Copernicus Marine, GEBCO,
  WDPA, IUCN) — genuinely open, well-documented, high-quality raw data — but they are *data
  sources*, not products; none of them is trying to be an explorer.

No platform sits across all three clusters — integrating open biodiversity data, curated telemetry,
environmental context, and conservation status into one transparent, publicly explorable tool.

## 2. Comparison of existing products

See [01](01-existing-platforms.md) in full; short version: OCEARCH wins on engagement and
storytelling but is closed and narrow; Movebank/OTN win on data depth but are inaccessible to a
general audience and access-gated; OBIS/GBIF/EMODnet win on openness but offer no exploration UX.
Every platform reviewed treats telemetry/observation data as authoritative rather than making its
limitations visible.

## 3. Comparison of useful datasets

See [02](02-datasets-and-apis.md) in full. Headline picks:

| Category | Primary source | Access pattern | Licence note |
|---|---|---|---|
| Occurrences | OBIS | GeoParquet bulk (S3) | Mixed CC0/CC-BY, aggregate is CC BY-NC |
| Movement/telemetry | Movebank (curated studies) | REST API, per-study permission | Per-study, varies |
| Acoustic detections | OTN (via OBIS bridge) | Limited direct API; via OBIS easier | Metadata public, detections gated |
| Conservation status | IUCN Red List | REST API, token required | Non-commercial only |
| Protected areas | WDPA/Protected Planet | REST API + bulk download | Open |
| Ocean physics/biogeochem | Copernicus Marine | `copernicusmarine` Python toolbox, NetCDF | Free, open, EU public data |
| Bathymetry | GEBCO | Bulk download or REST point-query API | Free, non-navigational disclaimer |

## 4. Data standards overview

Darwin Core (biodiversity, adopt at ingestion boundary), GeoJSON (adopt as API/frontend
transport), GeoParquet (adopt for OBIS bulk ingestion), NetCDF/CF (adopt for environmental data via
Xarray), OGC WMS/WFS/STAC (background knowledge only, not a dependency at MVP). Full reasoning in
[03](03-data-standards.md).

## 5. Interesting open-source projects/libraries

Python geospatial stack (GeoPandas/Shapely/Rasterio/Xarray/GeoAlchemy2) is mature and directly
reusable — no gap there. The one real gap found: **Python's animal-movement/trajectory-analysis
tooling is noticeably less mature than R's** (`move`/`moveVis`/`adehabitatLT`) — expect to write
modest custom trajectory logic rather than finding a turnkey Python library. Full detail in
[04](04-existing-open-source.md).

## 6. Candidate product concepts (5–10 differentiated ideas)

Eight concepts evaluated in [05](05-product-opportunities.md): (1) Wildlife+Environment Explorer,
(2) Movement+Environment Explorer, (3) Telemetry Technology/Uncertainty Explainer, (4)
Data-Quality/Effort layer, (5) Conservation Intelligence, (6) Simulated Telemetry/Digital Twin,
(7) Regional Ecosystem Explorer, (8) 3D depth-aware movement.

## 7. Comparison matrix

Reproduced from topic 5:

| Concept | Originality | Data feasibility | Learning value | Portfolio value | Scope risk |
|---|---|---|---|---|---|
| 1. Wildlife+Environment Explorer | 3 | 5 | 4 | 3 | 2 |
| 2. Movement+Environment Explorer | 4 | 3 | 5 | 5 | 3 |
| 3. Telemetry Tech/Uncertainty Explainer | 5 | 3 | 5 | 4 | 3 |
| 4. Data-quality/Effort layer | 5 | 2 | 4 | 2 | 4 |
| 5. Conservation Intelligence | 3 | 4 | 4 | 3 | 3 |
| 6. Simulated Telemetry/Digital Twin | 5 | 5 | 3/5 | 4 | 1 |
| 7. Regional Ecosystem Explorer | 3 | 5 | 3 | 3 | 2 |
| 8. 3D depth-aware movement | 4 | 2 | 4 | 4 | 5 |

## 8. Recommendation — best 2–3 concepts

**Recommended: build concepts 1 + 2 + 3 as one layered product, not three separate ones.**

- **Foundation layer (concept 1)**: species/place explorer over OBIS occurrence data +
  Copernicus environmental context. This is the "safe," high-data-feasibility backbone that makes
  everything else navigable (species pages, place pages, environmental overlays).
- **Flagship feature (concept 2)**: individual-animal movement view for a small, curated set of
  public Movebank/OTN-bridged studies, with environmental conditions shown alongside the track —
  this is the most visually compelling, demo-able part of the product.
- **Differentiator (concept 3)**: telemetry uncertainty made visible and explained wherever
  tracks/detections are shown — Argos error classes/ellipses, acoustic presence-vs-position
  distinction, sampling-effort context for occurrence maps. This is what no other platform
  reviewed does, and it's now backed by concrete sourced mechanisms (topic 6), not just intent.

**Companion/de-risking module: concept 6 (simulated telemetry).** Recommend building this
*early*, even before real external data integration is finalised, because it exercises the full
ingestion→store→serve pipeline with zero external API dependency, directly reuses your IoT/fleet
background, and de-risks the architecture before wrestling with OBIS/Copernicus/Movebank access
specifics.

**Deferred**: concept 4 and 7 become features/navigation modes within concept 1, not separate
builds. Concepts 5 (conservation) and 8 (3D) are credible v2 additions once the core exists —
building them now would be scope creep ahead of validating the core loop.

## 9. Proposed MVP

A single web app with:
1. A species/place browser backed by OBIS occurrence data (concept 1 core).
2. One or two Copernicus-derived environmental overlays (SST is the simplest starting point —
   single well-documented gridded product).
3. A small number (start with **one**) of real, curated Movebank public tracking studies for a
   shark or other charismatic marine species, rendered as a track with visible Argos error
   information (concepts 2+3 combined, deliberately narrow scope).
4. A basic simulated-telemetry demo (concept 6) showing a synthetic tagged animal going through
   the same ingestion pipeline, explicitly labelled as synthetic, used to explain real telemetry
   imperfections (gaps, noise, low-accuracy fixes) side-by-side with the real track from (3).
5. IUCN conservation status shown on species pages (cheap, high value, already scoped in topic 2).

Deliberately excluded from MVP: acoustic telemetry integration, MPA/WDPA overlay, multi-species
comparison, 3D/depth view, any form of habitat-suitability modelling, hosting/deployment beyond
local Docker Compose.

## 10. Proposed 3–6 month evolution path

- **Month 1**: Environment setup (Docker Compose, Postgres/PostGIS), first OBIS ingestion
  (species + occurrence for a small taxonomic/geographic slice), first Copernicus SST ingestion,
  QGIS-based validation, first learning notes (GIS/CRS, Darwin Core, occupancy/effort concept).
- **Month 2**: FastAPI read API over the ingested data (GeoJSON endpoints), MapLibre frontend
  showing species/occurrence + SST overlay — concept 1 MVP working end-to-end.
- **Month 3**: Simulated telemetry pipeline (concept 6) — synthetic tag generator, ingestion,
  visualisation — validates the full pipeline shape before tackling real telemetry access.
- **Month 4**: Integrate one real Movebank public study; build the track view with Argos
  error-class visualisation (concepts 2+3) — the flagship feature.
- **Month 5**: IUCN status integration, polish, second Copernicus variable (e.g. chlorophyll),
  write up scientific-limitations documentation directly into the product UI (not just docs).
- **Month 6**: Buffer/evaluation month — assess whether to pursue conservation-layer (concept 5),
  a second species/track, hosting/deployment, or a different expansion based on what was actually
  learned building the MVP. Do not pre-commit this month's scope now.

## 11. Learning roadmap

Structured as learn → apply pairs, tied to the MVP plan above:

- **GIS**: CRS/projections (building the first map), vector vs. raster data (occurrence points vs.
  SST grids), spatial queries (species-in-region).
- **Marine biology / sharks**: species biology for whichever species is chosen for the flagship
  track (life history, habitat use) — informs what's interesting to show on its page.
- **Ecology**: sampling bias, observation effort, occupancy-modelling concepts (topic 6) — applied
  directly when designing how occurrence density is displayed.
- **Conservation**: IUCN Red List categories/criteria — applied when displaying species status.
- **Oceanography**: SST/chlorophyll/currents fundamentals — applied via Copernicus ingestion and
  the environmental-context overlay.
- **Telemetry**: Argos accuracy classes, satellite vs. acoustic tracking differences (topic 6) —
  applied directly in the uncertainty-visualisation feature.
- **Data science**: time-series handling (tag transmission gaps), basic spatial-statistics
  concepts if a density/effort layer is attempted.

## 12. Proposed technical architecture

Python + PostgreSQL/PostGIS + FastAPI + Docker Compose + MapLibre GL JS frontend + Xarray for
NetCDF environmental data, ingest→stage→store→serve pipeline, QGIS for validation, Jupyter
notebooks for exploration. No Kubernetes/microservices/event bus/Terraform/elaborate AWS. Full
detail and reasoning in [07](07-technical-options.md).

## 13. Major risks and unknowns

- **Telemetry access is the biggest external-dependency risk** — Movebank/OTN access is
  per-study/permission-gated; the MVP's flagship feature depends on finding a genuinely public,
  usable study for a suitable species. This should be validated (find and confirm one specific
  usable dataset) *before* committing further design around it.
- **Render's PostGIS support is unconfirmed** (topic 7) — a hosting-path risk, but low urgency
  since MVP is local-first.
- **Naive occurrence-density visualisation risk** — easy to accidentally build something that
  looks like a "shark map" but is really a "where researchers went" map (topic 6) — needs explicit
  design attention, not just documentation.
- **Scope creep risk** — the product concept naturally invites adding "just one more layer"
  (MPAs, fishing effort, 3D, more species) — the phased plan above exists specifically to guard
  against this.

## 14. Data licensing/accessibility concerns

- OBIS aggregate distribution is **CC BY-NC** — fine for this non-commercial personal project, but
  worth stating explicitly in the README/licence section; per-record licences should still be
  tracked (topic 2) since some underlying datasets are more permissive.
- **IUCN Red List API forbids commercial use outright** — same conclusion, document it, don't
  monetise this project without renegotiating that access.
- Movebank/OTN data is per-study — whichever studies are chosen for the flagship feature must have
  their specific licence/citation terms checked and displayed in-app (attribution is a core
  scientific-integrity requirement, not just a legal one).

## 15. Scientific limitations

Documented in depth in [06](06-scientific-considerations.md): sampling bias, effort vs. presence
confounding, Argos spatial error classes (and the surprising dominance of low-accuracy fixes in
real datasets), acoustic presence-vs-position distinction, tag failure/transmission-gap semantics,
species ID uncertainty, geographic sampling bias. These are treated as first-class product design
constraints, not disclaimers.

## 16. Questions to resolve before implementation

1. Which specific species and which specific public Movebank (or OTN-bridged) study will anchor
   the flagship movement feature? (Needs a concrete dataset check, not a category-level answer.)
2. What SST/environmental temporal resolution is actually needed for the MVP — matching
   observation/track dates exactly, or a coarser (e.g. monthly climatology) approach for a first
   pass?
3. Confirm PostGIS availability on whichever host is eventually chosen (Render or an alternative)
   — deferred but not forgotten.
4. Confirm `pyobis` and any Movebank Python client maintenance status before writing ingestion
   code against them.
5. How much of the "effort vs. presence" distinction (topic 6) is worth attempting to visualise at
   MVP vs. deferring as a documented known-limitation for v1?

## 17. Suggested first practical exercise

**Pull one real OBIS occurrence dataset for a single species in a single region (e.g. great white
shark occurrences off South Africa or California) via the GeoParquet bulk path, load it into a
local PostGIS instance via GeoPandas, and open it in QGIS.** This is deliberately the smallest
possible slice that:
- exercises the real ingestion mechanism chosen for MVP (GeoParquet, not a toy CSV),
- forces hands-on Darwin Core field familiarity,
- forces a first real CRS/projection decision (QGIS will make lat/lon vs. projected CRS choices
  concrete rather than abstract),
- immediately surfaces the sampling-bias question from topic 6 in real data (the exercise should
  end with looking at *where* the points cluster and asking "is this where sharks are, or where
  people are").

This is learning + building in one step, not a theoretical detour, and is the natural entry point
into Month 1 of the evolution path above.

---

## Status and next step

This concludes the research phase as scoped in the original brief. **Nothing has been implemented.**
The recommendation above (concepts 1+2+3 layered, concept 6 as an early companion) is a
recommendation, not a locked decision — flag any disagreement before I record it in
`docs/decisions/` and begin Month 1 work.
