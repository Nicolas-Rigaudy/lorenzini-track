# 01 — Existing Platforms

Status: draft (research phase, topic 1 of N — going one topic at a time to conserve tokens)

Purpose: understand what already exists in the marine wildlife / biodiversity / animal-movement
data-and-visualisation space before deciding on a product direction. This is not exhaustive yet —
each platform will be revisited/deepened if it becomes relevant to a chosen concept.

---

## OCEARCH

- **URL**: https://www.ocearch.org/tracker/
- **Organisation**: OCEARCH (non-profit)
- **Purpose**: Public-facing global shark (and other large marine animal) tracker, built on their
  own satellite/PSAT tagging expeditions.
- **Core features**: Interactive global tracker map, per-animal bio pages with full ping history,
  routes shown against environmental context (SST, currents). Mobile apps (iOS/Android).
- **Data**: As of early 2026, ~400 tracked sharks (great whites, tigers, makos, hammerheads, bulls,
  and other pelagics), plus some turtles/dolphins.
- **Data access**: Has an API, used for research/education partnerships; data also released
  periodically for research collaborators/universities. Terms are more restrictive than a fully
  open scientific database — not a general-purpose open API like Movebank.
- **Open source**: Not open source itself, but community projects exist that scrape/wrap its
  public tracker data (e.g. `dine-j/shark-tracker`, `botwranglers/ocearch` on GitHub) — unofficial,
  fragile, and not something to depend on architecturally.
- **Strengths**: Strong brand, compelling storytelling/UX, tight species focus (large predators),
  successfully popularises shark research to the public.
- **Weaknesses / gaps**: Single-species-group focus (large sharks + a few other megafauna), no
  general biodiversity or multi-species ecosystem view, closed/curated dataset (their own tagging
  program only), no visible uncertainty/data-quality framing, no environmental-driver analysis
  beyond simple overlays, no open API for arbitrary secondary use.
- **Opportunity signal**: A tool that is genuinely open (public APIs, transparent methodology),
  multi-species/ecosystem-scale, and explicit about telemetry uncertainty would differentiate
  clearly from OCEARCH's closed, single-org, single-taxon-group model.

Sources: [OCEARCH Shark Tracker](https://www.ocearch.org/tracker/), [Unlocking a Treasure Trove of
Shark Data](https://www.ocearch.org/blog/unlocking-a-treasure-trove-of-shark-data/), [New web
application for the biggest shark tracking system](https://www.mapotic.com/blog/new-version-shark-tracking-platform/)

---

## Movebank

- **URL**: https://www.movebank.org/
- **Organisation**: Max Planck Institute of Animal Behavior
- **Purpose**: Free, general-purpose research database/platform for animal tracking and other
  on-animal sensor data, across essentially all taxa (not marine-specific).
- **Scale**: >3,500 data owners, >4 billion location records, 1,252+ taxa, 7,500+ user-managed
  studies (figures from the cited API/platform paper — treat as a snapshot, likely larger now).
- **API**: Public RESTful API (HTTP GET/POST/PUT/DELETE) with a documented data model; separate
  Movebank Data Repository for permanently archived, citable datasets tied to publications.
  API doc repo: https://github.com/movebank/movebank-api-doc
- **Access control**: Per-study, owner-controlled — public, embargoed, or fully private. This
  matters: a lot of Movebank data is *not* openly downloadable without permission.
- **Related tooling**: MoveApps — a no-code, serverless workflow platform for analysing Movebank
  tracking data (open-source modules, community-contributed).
- **Interop**: Documented pipeline to share Movebank data onward to GBIF and OBIS (Darwin Core
  event-based mapping) — relevant if this project wants a single ingestion path for
  observation + movement data.
- **Strengths**: Massive taxonomic and data-type breadth, strong data model, genuinely open API
  for public studies, active standards/interop work with the biodiversity-data world.
- **Weaknesses / gaps**: Research-database UX, not a consumer-facing "explorer"; not marine-specific
  (mixed with all terrestrial/avian tracking); much of the best data is access-restricted; no
  built-in environmental context layer (temperature, currents, chlorophyll) in the base platform.
- **Opportunity signal**: Movebank is a *data source*, not a competitor to a marine-focused
  explorer — a project could legitimately pull public marine studies from Movebank via its API
  as one telemetry input, rather than reinventing storage.

Sources: [Movebank API doc (GitHub)](https://github.com/movebank/movebank-api-doc), [Mobilizing
Animal Movement Data: API use and the Movebank platform](https://biss.pensoft.net/article/74312/),
[MoveApps paper (PMC)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9290230/), [Animals in motion:
enabling data sharing from Movebank (GBIF)](https://www.gbif.org/news/2djCgxEiwLOLUF4E4KViPP/animals-in-motion-enabling-data-sharing-from-movebank)

---

## Ocean Tracking Network (OTN)

- **URL**: https://oceantrackingnetwork.org/ , data portal https://members.oceantrack.org/
- **Organisation**: Dalhousie University, Canada (global partnership network)
- **Purpose**: Global *acoustic* telemetry network/data-management platform for aquatic animals
  (fish, sharks, marine mammals) — receiver-network based, not satellite.
- **Infrastructure**: Backend is PostgreSQL/PostGIS, hosted at Dalhousie — directly relevant
  precedent for this project's proposed stack.
- **Access**: Data Portal (members.oceantrack.org) functions more like a project file-repository
  (Dropbox-like) for partner projects rather than a fully public REST API. An unofficial R
  wrapper (`otndata`, wrapping the Plone CMS) exists for programmatic access. Public API surface
  is thinner than Movebank's.
- **Data policy**: Receiver metadata and tagging metadata are made public "as soon as possible" —
  but full detection data is more access-controlled, project-by-project.
- **Interop**: OTN data flows to OBIS (OTN-OBIS node) — meaning a chunk of OTN's public detections
  are actually more easily consumable *through OBIS* than through OTN directly.
- **Strengths**: Deep domain expertise in acoustic telemetry specifically (a technology with very
  different bias/uncertainty characteristics than satellite tracking — coarse spatial resolution,
  receiver-array-dependent, presence/absence rather than continuous position).
  This is valuable for the project's telemetry-literacy angle.
- **Weaknesses / gaps**: Not a general public-facing map/explorer product; access friction for
  raw detection data; Canada/Atlantic-centric historically (though the network has expanded
  globally via OTN-affiliated arrays).
- **Opportunity signal**: A project explaining/visualising *how acoustic telemetry differs from
  satellite telemetry* (detection vs. continuous position, receiver-array coverage gaps) is a
  genuine and underserved educational niche — OTN doesn't do this for the public, and OCEARCH is
  satellite-only.

Sources: [OTN Data Centre](https://oceantrackingnetwork.org/about-data-centre/), [OTN Data
Policies](https://members.oceantrack.org/data/policies), [OTN-OBIS node](https://obis.org/node/68f83ea7-69a7-44fd-be77-3c3afd6f3cf8),
[Ocean Tracking Network — Wikipedia](https://en.wikipedia.org/wiki/Ocean_Tracking_Network)

---

## OBIS (Ocean Biodiversity Information System)

- **URL**: https://obis.org/
- **Organisation**: IODE programme, IOC-UNESCO
- **Purpose**: Global open-access marine species occurrence database (observations, not tracks).
  Founded 2000 (Census of Marine Life origin).
- **Relationship to GBIF**: Formal joint strategy/action plan between OBIS and GBIF (2020
  cooperation agreement) — marine occurrence data flows between them, aiming to avoid duplicated
  effort. OTN's public detection data is aggregated into OBIS as an occurrence-style dataset.
- **Strengths**: Marine-specific, Darwin Core-native, huge aggregated occurrence dataset spanning
  plankton to megafauna, genuinely open API and downloads.
- **Weaknesses / gaps (to verify further in dataset-focused research)**: occurrence records
  inherit strong sampling-effort bias (goes wherever research cruises/observers go), taxonomic
  and temporal coverage very uneven.
- **Opportunity signal**: OBIS is a strong candidate as the primary "observations" data source; not
  itself a movement/telemetry or environmental-context tool — an explorer built on top of it,
  environmental overlays, would be additive not duplicative. (Deeper dataset-level treatment
  deferred to the next research topic — datasets & APIs.)

Sources: [OBIS impact](https://obis.org/whatwedo/impact/), [OBIS-GBIF Joint
Strategy](https://docs.gbif.org/obis-gbif-joint-strategy/en/), [OBIS and GBIF cooperation
agreement](https://obis.org/2020/09/07/obis-gbif/)

---

## GBIF (Global Biodiversity Information Facility)

- **URL**: https://www.gbif.org/
- **Organisation**: Intergovernmental network, established 2001
- **Purpose**: Global, all-taxa (not marine-specific) open biodiversity occurrence aggregator —
  the largest such aggregator in existence, built on Darwin Core.
- **Relationship to this project**: Useful as a secondary/cross-check source (e.g. citizen-science
  observations like iNaturalist records flow into GBIF), but OBIS is the more precise
  marine-specific source and already curates the marine subset with better QC for that domain.
- **Opportunity signal**: Treat GBIF as a broader occurrence source (especially coastal/citizen
  science sightings) layered alongside OBIS rather than the primary marine source.

Source: [GBIF background — OBIS/GBIF comparison search results](https://www.gbif.org/news/7w0xoodpNZRwnt1SjWfML0/obis-and-gbif-endorse-joint-strategy-and-action-plan-for-marine-biodiversity-data)

---

## EMODnet (European Marine Observation and Data Network)

- **URL**: https://emodnet.ec.europa.eu/
- **Organisation**: European Commission (DG MARE)
- **Purpose**: Aggregates multiple European marine data themes (biology, bathymetry, chemistry,
  physics, geology, human activities, seabed habitats) into thematic portals.
- **Relationship to OBIS**: EMODnet Biology's data pipeline runs through EurOBIS, which in turn
  feeds into global OBIS — so EMODnet Biology data is largely a European-regional lens on data
  that also surfaces globally via OBIS.
- **Strengths**: Very strong for European-water bathymetry/physical/chemical layers; thematically
  broader than OBIS (adds physical oceanography, seabed habitat, human-activity layers like
  shipping/fishing in one place).
- **Weaknesses / scope**: European-waters-focused — not a global solution on its own; this project
  is intended to be global, so EMODnet is a strong *regional* data source (esp. for a
  European-waters case study or as one bathymetry/physical layer provider) rather than the backbone.
- **Opportunity signal**: Good candidate for bathymetry/physical layers when building/demoing a
  European-region example, complementing global sources like GEBCO/Copernicus Marine (to be
  evaluated in the datasets & APIs research).

Source: [EMODnet — strengthening global marine biodiversity data collaboration](https://emodnet.ec.europa.eu/en/strengthening-global-marine-biodiversity-data-collaboration)

---

## Other platforms noted for later investigation (not yet researched in depth)

- **Copernicus Marine Service** — physical/biogeochemical ocean model + satellite reanalysis data
  (SST, currents, chlorophyll, salinity). Central candidate for the environmental-context layer;
  deferred to the datasets/APIs research topic.
- **Global Fishing Watch** — vessel tracking / fishing effort, relevant to bycatch/threat context
  for conservation angle.
- **iNaturalist / GBIF citizen science** — opportunistic sightings, useful but effort-biased.
- **Argo floats network** — ocean profiling floats (temperature/salinity profiles), relevant to
  oceanography learning objective.
- **WoRMS (World Register of Marine Species)** — authoritative marine taxonomy backbone, likely
  needed regardless of final product direction for species-name resolution.
- **MPAtlas / Protected Planet (WDPA)** — marine protected area boundaries, relevant to
  conservation-context concepts.

These will be covered properly under topic 2 (datasets & APIs) rather than duplicated here.

---

## Early synthesis (platforms)

No existing platform combines: (a) multi-species/ecosystem-scale marine biodiversity, (b) animal
movement/telemetry from more than one technology type, (c) environmental context layering, and
(d) explicit visualisation of data quality/uncertainty — in one open, global, public-facing tool.
- OCEARCH: narrow taxonomically, closed data, great storytelling.
- Movebank/OTN: strong data infrastructure, weak/no public "explorer" UX, access-restricted in
  large part.
- OBIS/GBIF/EMODnet: strong open observation data, no movement or environmental-context product
  layer, no consumer-facing exploration UX.

This gap — an *integrative, transparent explorer* rather than a new raw data source — is the
strongest early signal for product direction, to be tested against dataset feasibility (topic 2)
and scientific-rigour framing (later topic) before committing.
