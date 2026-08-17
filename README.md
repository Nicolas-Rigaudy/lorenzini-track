# poseidon (codename — user-facing name TBD)

An open-source, scientifically-honest marine wildlife/biodiversity/telemetry explorer. See
`docs/research/00-summary-and-recommendations.md` for the full research phase writeup and product
rationale, and `docs/decisions/` for the concrete architecture/product decisions made.

## What this is (short version)

A layered explorer combining open marine biodiversity data (OBIS), environmental context
(Copernicus Marine), and animal movement/telemetry — with a deliberate emphasis on making
telemetry uncertainty and data-quality limitations visible rather than hidden. See decision
[0001](docs/decisions/0001-product-direction.md) for the full reasoning.

## Repository layout

```
backend/     FastAPI + SQLAlchemy/GeoAlchemy2 API and data-ingestion CLI (Python)
frontend/    React + Vite + MapLibre GL JS explorer UI (TypeScript)
docs/
  research/    Research-phase findings (platforms, datasets, standards, product concepts)
  decisions/   Architecture/product decision log
  learning/    Domain-learning notes (GIS, marine biology, oceanography, telemetry, etc.)
notebooks/   Jupyter notebooks for data exploration
data/        Local/ingested data (gitignored — not committed)
```

Backend and frontend are deliberately decoupled (separate services, own Dockerfiles, talk over
REST/GeoJSON + CORS) — see decision [0003](docs/decisions/0003-frontend-backend-architecture.md).

## Running locally

Requires Docker and Docker Compose.

```
docker compose up --build
```

- Backend API: http://localhost:8000 (health check at `/health`, interactive docs at `/docs`)
- Frontend: http://localhost:5173
- Postgres/PostGIS: localhost:5432 (user/password/db: `poseidon`/`poseidon`/`poseidon` — local dev
  only, not for any real deployment)

Environment variables are read from `backend/.env` and `frontend/.env` (copy from the respective
`.env.example` files if starting fresh — working defaults for local dev are already checked in via
`.env.example`, `.env` itself is gitignored).

### Backend without Docker

```
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Requires a running Postgres/PostGIS instance reachable at `DATABASE_URL` (see `backend/.env`).

### Database migrations

```
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Frontend without Docker

```
cd frontend
npm install
npm run dev
```

## Data ingestion

Not yet implemented — planned as standalone CLI scripts under `backend/app/ingestion/` (no live
job queue/message bus; see decision [0001](docs/decisions/0001-product-direction.md) and
`docs/research/07-technical-options.md`). Geospatial data-processing dependencies (GeoPandas,
Xarray, Rasterio, etc.) are intentionally not yet added to `backend/pyproject.toml` — they'll be
added when the first ingestion script is written, not before.

## Status

Research phase complete (`docs/research/`). Product direction and initial architecture decided
(`docs/decisions/`). Scaffolding in progress. No ingestion or product features implemented yet.
