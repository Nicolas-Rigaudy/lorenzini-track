# 03 — Data Standards

Status: draft (research phase, topic 3 of N)

Purpose: understand the standards that matter for this project, and decide — per standard —
whether to adopt it directly, map to/from it at ingestion boundaries, or just understand it as
background knowledge for reading source data.

---

## Darwin Core (DwC)

- **What it is**: A TDWG (Biodiversity Information Standards) vocabulary for sharing biodiversity
  data — the standard OBIS and GBIF both publish in. Organised around two central entities:
  **Event** (the "how, when, where" of a sampling/observation event) and **Occurrence** (what
  organism was recorded during that event).
- **Distribution format**: Darwin Core Archive (DwC-A) — a zip of CSV data tables plus `eml.xml`
  (dataset metadata) and `meta.xml` (schema mapping).
- **Currency**: A Darwin Core public review completed 30 March 2026, ratified 26 May 2026, plus a
  newer **Darwin Core Data Package (DwC-DP)** format extending the Frictionless Data "Data
  Package" spec as a more modern container. Worth checking which version OBIS/GBIF downloads use
  at implementation time since this is actively evolving.
- **Decision for this project**: **Map to it at the ingestion boundary, don't invent a competing
  schema.** When pulling OBIS/GBIF occurrence data, keep core DwC field names (`scientificName`,
  `eventDate`, `decimalLatitude`/`decimalLongitude`, `basisOfRecord`, etc.) in the raw/staging
  layer even if the application's internal model is simplified — this preserves traceability back
  to source records and avoids costly re-mapping later if more DwC data sources are added.

Sources: [Darwin Core Quick Reference (TDWG)](https://dwc.tdwg.org/terms/), [Darwin Core Data
Package guide](https://gbif.github.io/dwc-dp/dp/), [OBIS manual — Darwin
Core](https://manual.obis.org/darwin_core.html)

---

## GeoJSON

- **What it is**: An IETF standard (RFC 7946) for encoding vector geographic features
  (points/lines/polygons + properties) as JSON. The de facto format for web maps (Leaflet,
  Mapbox GL, MapLibre all consume it natively).
- **Decision for this project**: **Adopt directly as the API-to-frontend transport format.**
  PostGIS can emit GeoJSON directly (`ST_AsGeoJSON`), FastAPI can serve it, and every mapping
  library expects it. This is the natural "last mile" format regardless of what's used internally
  for storage — no real alternative makes sense at the API layer for point/line/polygon features
  (animal locations, MPA boundaries, tracks).
- **Limitation to keep in mind**: Not efficient for very large vector datasets (verbose, no native
  compression/columnar filtering) — fine for map-viewport-sized responses, not for bulk transfer.

---

## GeoParquet

- **What it is**: An emerging (OGC-adjacent, developed by the geospatial open-source community)
  columnar format — Apache Parquet with a standardised geometry column encoding. Growing fast for
  large vector datasets, cloud-native access (range-read from S3), and analytics workloads
  (filtering/selecting columns without parsing whole rows).
- **Relevance**: OBIS already distributes its **entire global dataset as GeoParquet on S3** — this
  is the most efficient bulk-ingestion path for occurrence data (see topic 2), far better than
  paginating a REST API for millions of records.
- **Decision for this project**: **Use directly wherever a source offers it (OBIS) for bulk
  ingestion**, read via GeoPandas/DuckDB into PostGIS. Not needed as an application-internal
  storage format at MVP scale — PostGIS is more appropriate once data is loaded and needs
  relational/spatial querying, not just columnar scanning.

Sources: [Benefits of Cloud Native Geospatial File Formats](https://rtei.net/the-benefits-of-cloud-native-geospatial-file-formats/)

---

## NetCDF + CF (Climate and Forecast) Conventions

- **What it is**: NetCDF is a self-describing binary array format long used by
  atmospheric/oceanographic science; CF Conventions constrain it further — standardised variable
  names, units, coordinate reference systems, cell/aggregation methods — so that, e.g., a
  "sea_surface_temperature" variable means the same thing whether it comes from NOAA, NASA, ESA,
  or Copernicus.
- **Why it dominates oceanography specifically**: it's built for regular space-time
  "data cubes" (gridded time series across lat/lon/depth/time) — exactly the shape of SST,
  chlorophyll, current, and salinity model/satellite outputs. This is why Copernicus Marine,
  GEBCO, and NOAA/NASA products are all NetCDF-native rather than vector formats.
- **Decision for this project**: **Adopt directly for environmental data ingestion.** Read with
  Xarray (the Python-standard NetCDF/CF-aware array library), subset by bounding box/time/depth
  at the source where possible (Copernicus's own subsetting toolbox) rather than downloading full
  global cubes, then extract the specific point/time values needed to pair with an
  observation/track point. This is also a core piece of the oceanography learning objective —
  understanding data cubes, dimensions, and CF variable naming is foundational to working with
  this entire category of data.

Sources: [CF Conventions](https://cfconventions.org/Data/cf-conventions/cf-conventions-1.7/cf-conventions.html),
[OGC NetCDF standard](https://www.ogc.org/standards/netcdf/), [Working with spatio-temporal data
in Python](https://annefou.github.io/metos_python/02-formats/)

---

## OGC standards (WMS/WFS/STAC) — background knowledge, not deep dependency at MVP

- **WMS (Web Map Service)** / **WFS (Web Feature Service)**: Long-standing OGC standards for
  serving map images (WMS) or raw vector features (WFS) over HTTP. EMODnet and many national
  agencies expose data this way. Useful to *understand* since some environmental/bathymetry
  sources may only offer WMS/WFS endpoints rather than clean REST+JSON APIs, but not something to
  build custom infrastructure around at MVP — consume via GDAL/GeoPandas readers, which handle
  WMS/WFS natively, rather than hand-rolling clients.
- **STAC (SpatioTemporal Asset Catalog)**: A newer, lighter-weight JSON-based catalog standard for
  discovering geospatial assets (especially raster/satellite imagery) by space/time/collection.
  Increasingly used for cloud-native raster discovery. Not required for MVP given the specific
  sources chosen (Copernicus, GEBCO, OBIS) mostly have their own APIs/toolboxes, but worth knowing
  if the project later ingests satellite imagery catalogs directly.
- **Decision**: Understand these; do not build a generic OGC client layer until/unless a specific
  needed data source requires it.

---

## Cross-cutting decision: internal storage model

Given the above, the practical pattern for this project's stack is:

1. **Ingest** — read each source in its native/best format (DwC-A or GeoParquet for OBIS/GBIF,
   NetCDF via Xarray for Copernicus/GEBCO, GeoJSON/shapefile for WDPA).
2. **Stage** — keep source field names/identifiers (DwC terms, CF variable names) recognisable in
   a staging layer for traceability and licence/attribution tracking (per-record licence tracking
   flagged in topic 2).
3. **Store** — normalise into PostgreSQL/PostGIS for anything vector/relational (occurrences,
   tracks, MPA polygons); keep large environmental cubes as NetCDF/Zarr on disk queried via
   Xarray rather than fully loading into PostGIS, extracting only the specific point/time values
   needed at query time (a raster-in-database approach would be premature complexity at this
   scale).
4. **Serve** — GeoJSON over a FastAPI REST layer to the frontend, since every mapping library and
   the browser JSON pipeline already expects it.

This mapping means the project touches Darwin Core, GeoParquet, NetCDF/CF, and GeoJSON all as
genuinely necessary parts of the pipeline (not standards adopted for their own sake) — each maps
to a real learning objective (biodiversity data / cloud-native geospatial / oceanographic data
cubes / web GIS) called out in the original brief.
