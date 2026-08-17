# 05 — Product Opportunities

Status: draft (research phase, topic 5 of N) — synthesis of topics 1–4 plus targeted gap-check.

Purpose: generate and evaluate differentiated product concepts. No concept is selected yet —
that's topic 5's recommendation, still pending your sign-off before any implementation.

One additional platform surfaced during this pass, worth folding into the topic-1 picture:

- **Animal Telemetry Network (ATN)** — a NOAA/IOOS-run access point aggregating animal telemetry
  + associated oceanographic data across species/platforms/methods (satellite, acoustic). Closer
  in spirit to what this project might want to do (integrating telemetry with environmental
  context) than OCEARCH or Movebank alone — but it's a **data discovery portal for
  researchers**, not a public storytelling/exploration product, and it doesn't appear to visualise
  uncertainty or explain tracking-technology differences to a lay audience.
  Source: [NOAA/IOOS ATN](https://ioos.noaa.gov/project/atn/), [NOAA Ocean Service ATN](https://oceanservice.noaa.gov/ocean/animal-telemetry.html)

This reinforces the topic-1 finding: **integration + transparency + public accessibility is the
gap**, not raw data availability. A targeted search this round specifically for "telemetry
uncertainty visualization education tool" turned up no existing product combining uncertainty
visualisation, telemetry-technology education, and public accessibility in one place — the closest
adjacent thing is a NOAA/IOOS *poster and lesson plan* ("Ocean Animals on the Move"), i.e.
static classroom material, not an interactive tool.

---

## Candidate concepts

### 1. Marine Wildlife & Environment Explorer
Explore species → see where they've been observed (OBIS) → see what environmental conditions
(Copernicus SST/chlorophyll/currents) were present at those observation points/times.
- **Originality**: Medium — "biodiversity + environment overlay" isn't novel in principle, but no
  consumer-facing tool does it end-to-end for marine species specifically.
- **Data feasibility**: High — OBIS (GeoParquet bulk) + Copernicus (NetCDF/Xarray) are both strong,
  well-documented sources already evaluated.
- **Learning value**: High — directly exercises taxonomy/biodiversity data, spatial queries,
  oceanography, CRS/projections.
- **Portfolio value**: Solid full-stack demonstration (PostGIS + Xarray + FastAPI + map frontend)
  but conceptually the "safest"/least distinctive of the list.

### 2. Movement + Environment Explorer (telemetry-focused)
Pick a curated set of tracked animals (Movebank public studies / OTN-via-OBIS) and let a user walk
through an individual animal's track over time, with environmental conditions animated alongside
(inspired by R's `moveVis` concept, reproduced in Python/JS).
- **Originality**: Medium-high — moveVis proves the underlying idea works, but no public web tool
  does this interactively for marine species with environmental sync.
- **Data feasibility**: Medium — telemetry access is access-gated per-study (topic 2 finding); realistic
  scope is a small curated set of tracks, not "any shark."
- **Learning value**: Very high — movement ecology, telemetry technology, oceanography, animation.
- **Portfolio value**: Visually the most impressive/demo-able concept.

### 3. Telemetry Technology & Uncertainty Explainer
An interactive tool that visualises *how different tracking technologies actually work* — satellite
(Argos/PSAT, continuous-ish but gappy), acoustic (OTN, presence/absence at fixed receivers, spatially
coarse), archival tags (light-based geolocation, very coarse) — using real datasets to show what
each technology can and cannot tell you, side by side on the same map.
- **Originality**: High — confirmed via search that nothing public combines uncertainty
  visualisation + technology comparison + public accessibility (closest thing found is a static
  NOAA/IOOS classroom poster).
- **Data feasibility**: Medium — needs at least one real example dataset per technology type; small
  curated set, not bulk ingestion.
- **Learning value**: Very high, and directly plays to your IoT/connected-devices background —
  this is the concept most naturally suited to the "telemetry bias/uncertainty as a first-class
  feature" principle from the brief.
- **Portfolio value**: Distinctive positioning ("the tool that's honest about what tracking data
  can't tell you") — a strong differentiator/narrative for a portfolio, though a narrower/less
  flashy visual surface than concept 2 unless paired with it.

### 4. Data-Quality / Sampling-Effort Explorer
Make OBIS's sampling bias visible directly — e.g., a map layer showing observation *effort*
(record density, temporal coverage, taxonomic completeness) alongside raw occurrence points, so
users learn to distinguish "no shark sightings here" from "no one ever looked here."
- **Originality**: High conceptually, but narrower audience appeal as a standalone product; works
  better as a *feature* of concept 1 than a product on its own.
- **Data feasibility**: Medium — effort/bias metrics from occurrence data alone are an active
  research topic (not just a simple density plot) — real risk of oversimplifying or misleading if
  done naively; would need care to stay scientifically honest (ties to topic 6, scientific rigour).
- **Recommendation**: Fold into concept 1/3 as a design principle rather than a standalone product.

### 5. Conservation Intelligence Layer
Combine species distribution (OBIS) + IUCN status + WDPA/MPA boundaries + (stretch) Global Fishing
Watch effort data to show conservation context per species/region.
- **Originality**: Medium — conservation-status + MPA overlays exist elsewhere (e.g. Protected
  Planet itself), but combined with species-level occurrence + telemetry it's less common.
- **Data feasibility**: High for species/IUCN/MPA; Global Fishing Watch integration would be a
  stretch goal, not MVP.
- **Learning value**: High for conservation biology specifically (IUCN categories, MPA
  effectiveness, threats).
- **Portfolio value**: Good for demonstrating "socially useful" framing but risks scope creep if
  attempted before a strong movement/biodiversity core exists.

### 6. Simulated Telemetry / Digital Twin (IoT-angle concept)
Simulate a tagged animal emitting GPS/acoustic-style telemetry with realistic imperfections (gaps,
noise, battery degradation, tag failure) through an ingestion pipeline (MQTT-ish → API → PostGIS →
visualisation), directly reusing your professional IoT/fleet-management experience, and use it
*pedagogically* to show how real telemetry-processing pipelines cope with imperfect data.
- **Originality**: High as an educational device — nobody in this space is building a "telemetry
  simulator that teaches you why real wildlife data looks the way it does."
- **Data feasibility**: N/A (synthetic data) — lowest external dependency risk of any concept,
  which is attractive for early milestones.
- **Learning value**: High for telemetry/IoT concepts specifically, moderate for marine biology
  itself (it's about the *pipeline*, not the animal).
- **Portfolio value**: This is the concept most directly demonstrating your existing professional
  strengths (IoT device management, fleet management, connected devices) applied to a new domain —
  valuable as a *secondary/companion module* (e.g. "here's what real satellite tag telemetry looks
  like, and here's a simulator showing why it looks that way") rather than the primary product.

### 7. Regional Ecosystem Snapshot Explorer
Pick a region (e.g. a specific coastline/reef system) and let users explore "what lives here,
what conditions exist here, what's protected here, what's known/unknown" as a place-first
(rather than species-first or animal-first) entry point.
- **Originality**: Medium — a genuinely different navigation paradigm (place-first) from the
  species/animal-first designs of OCEARCH/Movebank.
- **Data feasibility**: High — same data sources as concept 1, different UX framing.
- **Recommendation**: Worth keeping as an alternative *navigation mode* within concept 1 rather
  than a wholly separate product (species-first and place-first views of the same underlying data
  are cheap to support once the data layer exists).

### 8. 3D / depth-aware marine movement
Extend movement/telemetry visualisation to include depth (from archival/PSAT tag pressure sensors
and/or Argo float profiles) rather than flat lat/lon.
- **Originality**: Medium-high, technically interesting, but a genuinely harder engineering/UX
  problem (3D web rendering, depth-time-position) for uncertain differentiation payoff at MVP
  stage.
- **Recommendation**: Strong **v2/stretch feature** once a 2D version of concept 2/3 exists and
  depth data for a chosen example animal is confirmed available — not an MVP-scope concept on
  its own.

---

## Comparison matrix (rough scoring, 1–5)

| Concept | Originality | Data feasibility | Learning value | Portfolio value | Scope risk (lower=better) |
|---|---|---|---|---|---|
| 1. Wildlife+Environment Explorer | 3 | 5 | 4 | 3 | 2 |
| 2. Movement+Environment Explorer | 4 | 3 | 5 | 5 | 3 |
| 3. Telemetry Tech/Uncertainty Explainer | 5 | 3 | 5 | 4 | 3 |
| 4. Data-quality/Effort Explorer (feature, not product) | 5 | 2 | 4 | 2 | 4 |
| 5. Conservation Intelligence | 3 | 4 | 4 | 3 | 3 |
| 6. Simulated Telemetry / Digital Twin | 5 | 5 (synthetic) | 3 (marine)/5 (IoT) | 4 | 1 |
| 7. Regional Ecosystem Explorer (nav mode, not product) | 3 | 5 | 3 | 3 | 2 |
| 8. 3D depth-aware movement | 4 | 2 | 4 | 4 | 5 |

---

## Early read (not a final recommendation — that's the next step)

Concepts 1, 2, and 3 are not mutually exclusive — they're layers of one coherent product:
**species/observation data (1) as the biodiversity foundation, individual animal movement (2) as
the flagship interactive feature, and explicit telemetry-technology/uncertainty framing (3) as the
scientific-credibility differentiator that no existing platform provides.** Concept 6 (simulated
telemetry) is a low-risk, high-alignment-with-your-background companion module that could either
be built early (since it has zero external data dependency) to de-risk the ingestion pipeline
before wrestling with real API access, or added later as an explainer feature.

Concepts 4 and 7 are better treated as design principles/features within the combined 1+2+3
product than standalone products. Concept 5 (conservation) and 8 (3D) are credible v2 expansions
once the core exists.

Full recommendation, MVP scope, and evolution path will be written up in the next stage once
you've reviewed this comparison — flag now if any of these concepts should be dropped or
reprioritised before I write the recommendation.
