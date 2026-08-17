# 04 — Existing Open-Source Projects & Libraries

Status: draft (research phase, topic 4 of N)

Purpose: catalogue the open-source libraries/tools this project should build on rather than
reinvent, across geospatial processing, movement analysis, and visualisation. This is about
*building blocks*, distinct from topic 1's finished *platforms*.

---

## Python geospatial stack (core, high confidence)

- **GeoPandas** — pandas + geometry column; the workhorse for tabular vector data (occurrences,
  MPA polygons, receiver stations). Built on Shapely for geometry ops.
- **Shapely** — planar geometry manipulation/analysis (point-in-polygon, buffering, distance),
  backed by GEOS. Used under the hood by GeoPandas; direct use for custom spatial logic.
- **Fiona** — vector I/O (reading/writing shapefiles, GeoJSON, GeoPackage), the layer GeoPandas
  uses for file access.
- **Rasterio** — raster I/O and processing (GDAL-based) — relevant for GEBCO bathymetry grids,
  satellite-derived raster products.
- **Xarray (+ rioxarray)** — labelled multi-dimensional arrays; the standard tool for NetCDF/CF
  data (Copernicus Marine outputs, GEBCO). `rioxarray` bridges Xarray with Rasterio/GDAL
  georeferencing for raster-style array data.
- **GeoAlchemy2** — SQLAlchemy extension for PostGIS — the natural ORM-layer bridge if a FastAPI
  backend is used with PostGIS.
- **Verdict**: This stack (GeoPandas/Shapely/Fiona/Rasterio/Xarray/GeoAlchemy2) essentially
  *is* the "Python geospatial stack" already named in the original brief, and is independently
  confirmed here as the standard, well-maintained toolset for exactly this kind of project — no
  reason to look further afield for core geospatial plumbing.

Sources: [GeoPandas ecosystem docs](https://geopandas.org/en/latest/community/ecosystem.html),
[Python Geospatial Processing Libraries comparison](https://www.pistack.xyz/posts/2026-07-01-python-geospatial-libraries-geopandas-shapely-fiona-rasterio-folium/)

---

## Animal movement / trajectory analysis

- **MovingPandas** (not returned directly in search but well-established; verify current status
  before depending on it) — GeoPandas-based trajectory objects, common for movement-ecology work
  in Python. Flag as **to verify** rather than confirmed, since it wasn't directly surfaced in
  these searches — check `movingpandas` PyPI/GitHub status before committing to it.
- **Traja** — Python toolbox specifically for animal trajectory analysis (path metrics,
  turning angles, etc.).
- **ORTEGA** — Python package for time-geographic, pairwise animal-interaction analysis (are two
  tracked animals in space-time proximity). Interesting if the product ever explores
  multi-animal/predator-prey-style interaction questions — likely beyond MVP.
- **R ecosystem is more mature here than Python's**: `move`/`move2` (the R packages behind
  Movebank itself), `moveVis` (GPS-track + environmental-data video animations — directly relevant
  to the "movement + environment" visualisation concept), `adehabitatLT` (trajectory statistics),
  `abmR` (agent-based movement modelling), `stmove` (exploratory movement report building).
- **Decision**: Given the project's Python-first stack preference, treat R packages as
  *reference/inspiration* for what movement-analysis features look like (e.g. moveVis's
  environment-synced animation idea is worth reproducing in Python/JS rather than adopting R) —
  not as dependencies to actually run. For Python, expect to write custom (fairly simple)
  trajectory logic on top of GeoPandas/Shapely rather than finding one mature all-purpose Python
  movement-ecology library equivalent to R's `move` ecosystem — this is itself a useful finding:
  **Python's movement-ecology tooling is noticeably less mature than R's**, which is a real gap
  the project could quietly help close for others working in Python, even if that's not the
  primary goal.

Sources: [moveVis (GitHub)](https://github.com/16EAGLE/moveVis), [ORTEGA package
(PMC)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10925014/), [movement-analysis-tools
(GitHub, anitagraser)](https://github.com/anitagraser/movement-analysis-tools), [animal-movement
GitHub topic](https://github.com/topics/animal-movement)

---

## Visualisation / frontend mapping

Not deeply searched this round (lower risk, well-known ecosystem) but noting the realistic
candidates given "simple frontend" is a project constraint:

- **Leaflet / MapLibre GL JS** — open-source web map rendering; MapLibre (a maintained fork of
  Mapbox GL after its licence change) is the more future-proof pick for vector-tile-heavy,
  animated map rendering (needed for tracks/movement).
- **deck.gl** — WebGL-based large-scale geospatial visualisation (good fit if trajectory/point
  volumes grow large; more complex to adopt than Leaflet/MapLibre, so not needed until scale
  demands it).
- **Folium** — Python wrapper generating Leaflet maps from a notebook — useful for the
  exploration/analysis/notebooks phase of the work (`notebooks/`), not the production frontend.
- **QGIS** — already specified in the brief for desktop GIS exploration; this remains the right
  tool for early data exploration, understanding CRS/projections hands-on, and validating layers
  before building the web frontend.
- **Decision**: Folium + QGIS for the exploration/learning phase; MapLibre GL JS as the production
  frontend map renderer once a concept is chosen, deferring deck.gl unless/until data volume or
  animation complexity genuinely requires it.

---

## Biodiversity/telemetry API client libraries

- **pyobis** (OBIS's own Python client) — worth checking current maintenance status; if healthy,
  preferable to hand-rolling REST calls against the OBIS API.
- **pygbif** — GBIF's official Python client, well-established.
- **movebank-api-doc-derived clients** — no single official Python client confirmed from this
  round of research; Movebank access is more commonly done via direct REST calls or the R `move2`
  package. Flag: **check for an official/community Python client before hand-rolling a Movebank
  integration.**
- **copernicusmarine** (Copernicus's own Python toolbox, referenced in topic 2) — official,
  actively maintained, handles auth + subsetting; adopt directly.
- **Decision**: Prefer each provider's official client library where one exists and is maintained
  (pygbif, copernicusmarine) over hand-rolled HTTP calls; fall back to `requests`/direct API calls
  only where no good client exists (likely OTN, possibly Movebank).

---

## Cross-cutting takeaway

The core geospatial stack (GeoPandas/Shapely/Rasterio/Xarray) is mature, standard, and directly
reusable — no real build-vs-adopt decision needed there. The one genuine gap is **Python-native
animal movement/trajectory analysis**, which is less mature than the R ecosystem's `move`/`moveVis`
tooling. This means the project will likely need to write some of its own (modest) trajectory
utilities on top of GeoPandas rather than finding a turnkey library — worth flagging early as
scope, not a blocker, and consistent with keeping the project's own code lightweight per the
"no premature abstraction" engineering principle.
