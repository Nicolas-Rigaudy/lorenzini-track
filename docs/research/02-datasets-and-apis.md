# 02 — Datasets and APIs

Status: draft (research phase, topic 2 of N)

Purpose: evaluate the concrete public datasets/APIs this project could realistically build on,
across biodiversity/occurrence, telemetry/movement, conservation, and oceanography. Each entry
lists what's verified vs. still to confirm — do not treat anything here as final until checked
against the live API docs at implementation time.

---

## Biodiversity / occurrence data

### OBIS (Ocean Biodiversity Information System)
- **URL**: https://obis.org/ , manual: https://manual.obis.org/access
- **What it provides**: Marine species occurrence records (Darwin Core), QC'd and taxonomically
  resolved via WoRMS.
- **Access mechanisms**: (1) OBIS Mapper (interactive, CSV export with all 225 DwC fields),
  (2) REST API, (3) full dataset as a Darwin Core Archive, (4) **full dataset as GeoParquet on
  AWS S3** (`s3://obis-open-data`) — this is the most attractive path for programmatic/bulk use
  since it avoids paginated API calls entirely.
- **Format**: Darwin Core Archive (CSV + eml.xml + meta.xml) or GeoParquet.
- **Licence**: Mixed — most underlying source datasets are CC0 or CC-BY, but the aggregated full
  OBIS dataset as distributed is **CC BY-NC**. Per-dataset licence/citation info is tracked in
  `s3://obis-open-data/licenses.tsv` — **must be respected per-record if attributing/redistributing**,
  not just at the OBIS-aggregate level.
- **Coverage**: Global, marine only, temporal range spans decades of historical + ongoing records;
  extremely uneven spatially and taxonomically (biased toward well-studied waters/species).
- **Rate limits**: not documented in what I found — needs direct confirmation from API docs before
  building around heavy API polling; the GeoParquet bulk path avoids the question.
- **Verdict**: Strong primary candidate for "observations" data. The CC BY-NC aggregate licence is
  an important constraint to note explicitly in the project's licensing doc (topic 6/decisions) —
  it likely rules out certain commercial reuse but is fine for an open personal/portfolio project.

### GBIF
- **URL**: https://www.gbif.org/
- **What it provides**: All-taxa occurrence aggregator; useful mainly as (a) a secondary
  cross-check, (b) source of citizen-science marine sightings (iNaturalist etc. flow into GBIF).
- **Access**: Public REST API + bulk Darwin Core Archive downloads, well documented, no
  authentication for basic use, DOI-backed "download" mechanism for reproducibility.
- **Licence**: CC0/CC-BY/CC-BY-NC mixed per source, tracked per record — same discipline needed as
  OBIS.
- **Verdict**: Secondary source; not core to MVP given OBIS already curates the marine subset well,
  but valuable later for citizen-science sightings layer.

### WoRMS (World Register of Marine Species) — not yet deep-dived
- Referenced as the taxonomic backbone OBIS uses. Will need this regardless of product direction
  for species name resolution/synonymy. To confirm API details in a later pass if the product
  direction needs live taxonomy lookups rather than static species lists.

---

## Animal movement / telemetry

### Movebank
- **URL**: https://www.movebank.org/ ; API doc: https://github.com/movebank/movebank-api-doc
- **What it provides**: GPS/satellite/archival tag tracks across taxa; some marine species (sharks,
  turtles, seabirds, marine mammals) among many public studies.
- **Access**: RESTful HTTP API (GET/POST/PUT/DELETE), CSV/JSON. Per-study access control set by
  data owner — public, embargoed by date, or fully private. Only public/embargoed-expired studies
  are usable without individual permission requests.
- **Format**: Custom Movebank schema (not natively Darwin Core, though an event-based DwC mapping
  exists for onward sharing to GBIF/OBIS).
- **Licence**: Per-study — varies, generally CC-style but must be checked per dataset before reuse.
- **Verdict**: Good source for a small number of well-chosen public marine studies (sharks, turtles)
  to demonstrate satellite telemetry — not a bulk global data source given the access-control
  patchwork. Realistic approach: pick 1-3 specific public studies to integrate rather than trying
  to ingest "all marine Movebank data."

### Ocean Tracking Network (OTN)
- **URL**: https://oceantrackingnetwork.org/ ; data portal https://members.oceantrack.org/
- **What it provides**: Acoustic telemetry — receiver-network detections (presence/absence,
  intermittent, spatially coarse to the receiver location, not continuous position).
- **Access**: Data Portal is closer to a private file-repository (Plone-based) than a public REST
  API; an unofficial R package (`otndata`) wraps it. Public API surface is thin.
- **Bridge**: A meaningful chunk of OTN's public detection data is aggregated into **OBIS as an
  OTN-OBIS node** — meaning the practical path to *some* OTN data may be via OBIS's API/GeoParquet
  rather than OTN directly.
- **Licence/access**: Receiver + tagging metadata public "as soon as possible"; full detection data
  is more access-controlled per project.
- **Verdict**: Treat as a secondary/illustrative source (fetch via the OTN-OBIS bridge, or use a
  small number of published/open datasets) rather than a primary bulk ingestion target — direct API
  access is not straightforward for a solo project.

### Argos / satellite tag providers — not yet deep-dived
- Underlying tag/transmission technology behind much of Movebank's satellite data (Argos system,
  Wildlife Computers, etc.). Relevant for the telemetry learning-notes angle (explaining how the
  data actually gets from tag to database) even if not a direct API integration target.

---

## Conservation status / protected areas

### IUCN Red List API
- **URL**: https://api.iucnredlist.org/ (current v4; older v3 at apiv3.iucnredlist.org is
  deprecated/archived)
- **What it provides**: Conservation status (LC/NT/VU/EN/CR/etc.), assessment details, threats,
  by species.
- **Access**: Requires an API token (free registration). Best queried by species scientific name
  rather than internal ID.
- **Licence/usage restriction**: **Commercial use is explicitly forbidden** — fine for this
  non-commercial personal/portfolio project, but a hard constraint to record if the project is
  ever monetised or relicensed.
- **Verdict**: Necessary and straightforward source for conservation-status context on any species
  shown in the app (e.g. "this shark species is Vulnerable/Endangered").

### WDPA / Protected Planet
- **URL**: https://www.protectedplanet.net/ , API docs (v3, archived): https://api.protectedplanet.net/documentation/v3
- **What it provides**: Global protected-area polygons, including Marine Protected Areas (MPAs),
  with IUCN protection-category classification. Joint UNEP-WCMC / IUCN product, updated monthly.
- **Access**: Public API + bulk shapefile/geodatabase downloads.
- **Verdict**: Strong candidate for an MPA overlay layer if the product includes a
  conservation/spatial-context dimension. Straightforward vector polygon data, PostGIS-friendly.

### Global Fishing Watch — not yet deep-dived
- Noted in topic 1 as relevant to bycatch/fishing-effort context; to be evaluated in more depth
  only if a conservation-intelligence concept is selected.

---

## Oceanographic / environmental data

### Copernicus Marine Service
- **URL**: https://marine.copernicus.eu/ , data catalogue: https://data.marine.copernicus.eu/
- **What it provides**: The most comprehensive single source found — SST, salinity, currents, sea
  level, chlorophyll-a, dissolved oxygen, nutrients, waves; both near-real-time and historical
  (back to 1993) reanalysis products; global and regional.
- **Resolution examples verified**: OSTIA global SST product at 0.05°×0.05° daily gap-free grids;
  Global Ocean Physics Analysis/Forecast at 1/12° with 50 vertical levels (0–5500m), daily/monthly
  means plus hourly surface fields.
- **Format**: NetCDF (standard oceanographic gridded format), accessed via their `copernicusmarine`
  Python toolbox (subset/download by bbox, depth, time range) — this maps directly onto the
  project's proposed Xarray/NetCDF-in-the-stack plan.
- **Access**: Requires free registration; large model outputs mean subsetting (not full-grid
  download) will be the practical approach for a solo project.
- **Licence**: Free and open (Copernicus programme = EU public data), attribution required.
- **Verdict**: This should be the primary environmental-context data source. Directly answers the
  "what were the ocean conditions where/when this animal was observed" learning objective and
  product concept. Highest-value single data source found so far for the "learn oceanography"
  goal, since it's one coherent API/toolbox covering nearly all the physical/biogeochemical
  variables listed in the brief.

### GEBCO (bathymetry)
- **URL**: https://www.gebco.net/ , download: https://download.gebco.net/
- **What it provides**: Global bathymetry (and land elevation) grid, current release on a 15
  arc-second grid (~450m at the equator).
- **Access**: Direct NetCDF/GeoTIFF global or tiled download via CEDA; also OPeNDAP/ERDDAP access
  for remote/subset queries; a newer GEBCO REST API supports point/batch/area depth queries
  without downloading the whole grid.
- **Licence**: Free to use and redistribute; explicit disclaimer that it's not authoritative for
  navigation/legal use (a science/viz-only product, not a nautical chart).
- **Verdict**: Good, low-friction source for a depth/habitat-context layer; the point-query REST
  API is attractive for on-demand "what's the seafloor depth here" lookups without hosting the
  full global grid locally, at least for MVP.

### NOAA (ERDDAP), NASA — not yet deep-dived
- ERDDAP is a widely-used standardized query protocol/server software for NetCDF oceanographic
  data (seen already serving GEBCO bathymetry via Rutgers' instance) — worth learning as a general
  access pattern since many oceanographic providers run their own ERDDAP servers. NASA satellite
  ocean-colour/chlorophyll products (e.g. MODIS/VIIRS) are a likely secondary/cross-check source to
  Copernicus's chlorophyll-a product — to confirm only if Copernicus proves insufficient.

### Argo floats — not yet deep-dived
- Autonomous profiling floats (temperature/salinity vs. depth) — relevant to the "oceanography"
  learning objective and to understanding water-column structure beyond surface-only satellite
  products. Lower priority for MVP (adds a vertical-profile dimension); to revisit if 3D/vertical
  environmental context becomes part of the chosen concept.

---

## Cross-cutting notes

- **Licensing discipline is a real constraint, not a footnote.** OBIS/GBIF are per-record mixed
  licences (CC0/CC-BY/CC-BY-NC), IUCN explicitly forbids commercial use, Copernicus/GEBCO/WDPA are
  comparatively permissive. A shared product decision is needed early: track licence/attribution
  per source at ingestion time (e.g. a `source_licence` column) rather than bolting it on later.
- **Bulk/columnar access beats per-record API polling wherever available.** OBIS's GeoParquet
  export and Copernicus's subsetting toolbox are both meaningfully better fits for a
  PostGIS/GeoPandas/Xarray stack than scraping REST endpoints record-by-record.
- **Telemetry is the least "bulk-friendly" category.** Movebank and OTN both gate most useful data
  behind per-study/per-project permissions — realistic scope is a curated handful of public
  studies/datasets, not a live global feed. This should shape MVP scope: the movement/telemetry
  dimension of any concept needs to work with a small, hand-picked set of tracks, not "all shark
  tracks everywhere."
- **Copernicus Marine is the standout single source** for this project's environmental-context and
  oceanography-learning goals — one API covering nearly every physical/biogeochemical variable
  listed in the original brief, NetCDF-native, free, well-documented Python tooling.

Still to confirm before implementation (flagged rather than assumed): OBIS API rate limits, exact
current Movebank public-study catalogue for marine taxa, GEBCO REST API current terms/limits,
whether IUCN's newer v4 API materially changed access/token requirements from what's described
here.
