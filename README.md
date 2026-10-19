# Lorenzini Track

An open research project on shark telemetry, from tag to map. Named after Stefano Lorenzini, who
described in 1678 the ampullae of Lorenzini, the organs sharks use to sense faint electric fields.

Lorenzini Track will simulate a fleet of shark tags the way real tags behave, carry their data
through a gateway, ingestion and processing pipeline, and publish the result as a map that shows
where positions are uncertain and why some are deliberately coarsened. Real shark tracking data
is mostly access-restricted, partly on purpose (see decision
[0004](docs/decisions/0004-no-live-tracking-data.md)), so the tracks are simulated and labelled
as simulated; open occurrence and environmental data give the real-world context.

Sharks lead: they are the headline story, the default map view and the simulated fleet. The
other marine species already in the data (a devil ray, turtles, a seal, a manatee, seabirds)
stay, one taxon filter away.

The framing is recorded in decisions [0007](docs/decisions/0007-lorenzini-track-framing.md) and
[0008](docs/decisions/0008-sharks-lead-other-species-kept.md); the
plan to 1.0 is in [`logics/roadmap/road_001_lorenzini_track_to_1_0.md`](logics/roadmap/road_001_lorenzini_track_to_1_0.md).

## Status

Milestone 0.2 (sharks-first scope and rename) is in progress. What runs today is a PostGIS-backed
map explorer over real, open datasets (OBIS-SEAMAP/GBIF Darwin Core archives and the IMOS
acoustic tracking archive). The simulated fleet, uncertainty views and the hosted demo come in
later milestones.

## Repository layout

```
backend/        FastAPI + SQLAlchemy/GeoAlchemy2 + Alembic API and ingestion scripts (Python)
frontend/       React + Vite + MapLibre GL JS map (TypeScript)
docs/
  decisions/    Architecture and product decision log
  research/     Research-phase findings
design-system/  UI design notes
logics/         Product brief, roadmap, backlog and tasks
```

## Running locally

Requires Docker and Docker Compose.

```
docker compose up --build
```

- API: http://localhost:8000 (`/health`, interactive docs at `/docs`)
- Frontend: http://localhost:5173
- PostGIS: localhost:5432 (user/password/db `lorenzini`/`lorenzini`/`lorenzini_track`, local
  development only)

Environment variables are read from `backend/.env` and `frontend/.env`; copy them from the
`.env.example` files when starting fresh.

Without Docker for the app itself (PostGIS still needed at `DATABASE_URL`):

```
cd backend && pip install -e ".[dev]" && alembic upgrade head && uvicorn app.main:app --reload
cd frontend && npm install && npm run dev
```

## Loading data

Each dataset has a script under `backend/app/ingestion/`; readers normalise the source and a
shared loader upserts it. For example:

```
cd backend
python -m app.ingestion.gbif_whale_sharks
python -m app.ingestion.imos_sharks
```

## Checks

```
backend/scripts/test.sh                          # backend tests on a fresh, disposable PostGIS
cd backend && ruff check .
cd frontend && npm run build && npm run lint     # type-check, build, oxlint
```

`backend/scripts/test.sh` starts the `db-test` compose service (data in tmpfs, port 5433),
migrates it, runs pytest and removes it again.
