# 07 — Technical Options

Status: draft (research phase, topic 7 of 7 — last of the originally-scoped research docs)

Purpose: consolidate the architecture implied by topics 2–4 into concrete options, plus hosting,
and flag what still needs verification before implementation. Per the brief's engineering
principles: local-first, Docker-based, no AWS/Kubernetes/microservices/Terraform unless a real
need emerges.

---

## Core stack (high confidence, mostly already justified in prior topics)

- **Language**: Python throughout (backend, ingestion, data processing) — matches existing
  expertise, and every key data source (OBIS, Copernicus, GEBCO, GBIF) has mature Python tooling
  (topic 4).
- **Database**: **PostgreSQL + PostGIS**. Directly named in the brief; independently justified by
  topic 1's finding that OTN itself runs on PostgreSQL/PostGIS, and by the vector data types in
  play (occurrence points, track lines, MPA polygons) which are exactly PostGIS's strength.
- **Environmental/raster data**: **NetCDF files on disk, read via Xarray**, not loaded wholesale
  into PostGIS (topic 3's storage decision) — extract point/time values into the relational layer
  at ingestion or query time rather than treating PostGIS as a raster store. Revisit only if
  point-in-time environmental lookups become a genuine performance bottleneck.
- **API layer**: **FastAPI** — named in the brief, and a good fit because (a) Pydantic models map
  cleanly onto Darwin Core-derived and GeoJSON-shaped responses, (b) async support suits I/O-bound
  calls out to Copernicus/OBIS during ingestion jobs, (c) auto-generated OpenAPI docs are useful
  for a public-facing project others might build on.
- **Vector/geometry tooling**: GeoPandas + Shapely + GeoAlchemy2 as the bridge between
  Python-side processing and PostGIS (topic 4).
- **Containerisation**: **Docker Compose** for local dev (Postgres/PostGIS + API + any worker),
  matching the brief's "local development, Docker" preference — no orchestration layer needed at
  this scale.
- **Desktop GIS**: **QGIS** for exploration/validation, as specified — connects directly to
  PostGIS for visual QA of ingested data, and is the right tool for hands-on CRS/projection
  learning named in the brief.
- **Notebooks**: Jupyter (already scaffolded as `notebooks/`) for the learn→apply exploration
  loop — e.g. first touching each new dataset/API in a notebook before writing pipeline code.

---

## Frontend options

- **Recommendation**: A lightweight web frontend using **MapLibre GL JS** (topic 4) as the map
  renderer, consuming the FastAPI backend's GeoJSON endpoints directly. Framework choice
  (plain JS/HTM, or a light framework like Svelte/React) is a secondary decision — not
  architecturally significant, and shouldn't be over-thought before the product concept is fixed,
  per the brief's "no premature abstraction" principle.
- **Not recommended at MVP**: deck.gl (topic 4 — defer until data volume/animation complexity
  genuinely requires WebGL-scale rendering); any full SPA framework complexity beyond what's
  needed to render a map + a few panels.

---

## Ingestion pipeline shape

Following the ingest → stage → store → serve pattern from topic 3:

```
source APIs/bulk files (OBIS GeoParquet, Copernicus NetCDF, GEBCO, WDPA, IUCN)
        ↓
ingestion scripts (Python, scheduled/manual — no event bus needed at this scale)
        ↓
staging (raw/near-raw, source field names preserved, per-record licence tracked)
        ↓
PostGIS (normalised vector data) + NetCDF-on-disk (environmental cubes, queried via Xarray)
        ↓
FastAPI (GeoJSON responses)
        ↓
MapLibre-based frontend
```

For concept 6 from topic 5 (simulated telemetry), the same pipeline shape applies with a synthetic
generator standing in for the external API call — this is precisely why that concept is
low-risk/early-buildable: it exercises the ingestion→store→serve path without needing any real
external data source to be finalised first.

---

## Hosting options

- **Render** (named in the brief): confirmed to offer a genuine free tier for a web service +
  Postgres, no Dockerfile/credit card required to start. Caveats found this session, not
  previously confirmed:
  - Free Postgres is **not intended for production**, and free-tier databases are
    reported to expire/be deleted after 30–90 days depending on source (conflicting reports found —
    **needs direct confirmation on Render's current docs before relying on it**, not just this
    search summary).
  - Free web services **spin down after 15 minutes of inactivity** (30–60s cold-start on next
    request) — acceptable for a low-traffic portfolio project, worth mentioning in the README so
    visitors aren't confused by a slow first load.
  - **PostGIS extension availability on Render's Postgres was not confirmed by this search** —
    flag as a concrete thing to verify directly against Render's docs/dashboard before committing,
    since the whole architecture depends on PostGIS specifically, not just Postgres.
  - Paid tier if needed: roughly $7/mo minimum for a basic web service, ~$13/mo combined with a
    small paid Postgres instance — cheap enough to be a non-issue if the free tier's PostGIS
    support or persistence limits turn out to be a blocker.
- **Alternative to evaluate if Render's PostGIS support doesn't pan out**: Supabase (Postgres
  hosting with PostGIS commonly enabled) or Fly.io (Docker-native, supports attaching a Postgres
  volume) — not deeply researched this session, noted as fallback options rather than
  recommendations.
- **Decision**: keep hosting choice **local-first and hosting-agnostic** during MVP build — develop
  entirely via Docker Compose locally, defer the hosting decision (and its PostGIS-availability
  verification) until there's something worth deploying. This avoids sinking research time into a
  hosting decision before the product concept is even finalised.

Sources: [Platforms with a real free tier for developers in 2026 (Render)](https://render.com/articles/platforms-with-a-real-free-tier-for-developers-in-2026),
[Render Postgres 2026: Pricing, Limits & Alternatives](https://kuberns.com/blogs/render-postgres-pricing-setup-limits/),
[Render Pricing Guide](https://kuberns.com/blogs/render-pricing/)

---

## What NOT to introduce (reaffirming the brief's constraints, now grounded in the actual data/workload)

- **Kubernetes / microservices**: nothing in the ingestion or serving workload here needs
  independent scaling of separate services — a single FastAPI process + Postgres + scheduled
  ingestion scripts is proportionate to the data volumes discussed in topics 1–2 (curated telemetry
  sets, not continuous high-throughput streams).
- **Event-driven architecture / message bus**: ingestion is inherently batch/scheduled (OBIS bulk
  files, Copernicus subset downloads, a handful of curated telemetry studies) — there is no
  real-time event stream in this data to justify one, aside from the *simulated* telemetry concept,
  which can just call the ingestion API directly rather than needing Kafka/SQS-style
  infrastructure.
- **Terraform / elaborate AWS**: no infrastructure complexity has emerged from this research that
  Docker Compose + a single hosted Postgres/web-service pair can't handle; explicitly consistent
  with the brief's instruction not to demonstrate AWS skills already possessed professionally.

---

## Open technical questions to resolve before/during implementation

1. Confirm PostGIS extension availability on Render's managed Postgres (or pick an alternative
   host) before assuming it as the deployment target.
2. Confirm current OBIS API rate limits if any API polling (vs. GeoParquet bulk read) ends up
   needed for incremental updates.
3. Decide the concrete update cadence for environmental data (Copernicus) — near-real-time,
   daily, or a fixed set of historical snapshots tied to specific observation/telemetry dates —
   this has real storage/complexity implications and should be driven by the final product concept,
   not decided in the abstract here.
4. Verify `pyobis`/Movebank Python client maintenance status (flagged in topic 4) before writing
   custom HTTP clients.
