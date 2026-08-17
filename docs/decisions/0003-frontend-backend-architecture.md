# 0003 — Frontend/Backend Architecture: Decoupled React Frontend + FastAPI Backend

Status: accepted
Date: 2026-08-17

## Context

Topic 7 research (`docs/research/07-technical-options.md`) settled the broad stack category
(Python/PostgreSQL+PostGIS/FastAPI/MapLibre) but left four concrete shape decisions open: frontend
framework, basemap tile source, how frontend and backend fit together as a deployable, and the
database access layer.

## Problem

These four decisions needed the user's judgment (framework/tooling preference, CV goals, existing
team familiarity) rather than being derivable from the research alone.

## Decision

1. **Frontend framework: React** (via Vite). Chosen over plain JS or Svelte because the user's
   frontend team works in React/React Native — this project doubles as React onboarding practice.
   Map rendering uses `maplibre-gl` directly (or its React-compatible wrapper), not a heavier
   map-abstraction library, to stay close to the underlying MapLibre API.
2. **Basemap tiles: OpenFreeMap**. Free, open-source, no API key, no usage limits, self-hostable
   later if needed. Chosen over MapTiler (needs a key, has a request cap) and plain OSM raster
   tiles (usage policy discourages app/production use).
3. **Architecture shape: decoupled frontend + backend.** Two independent deployables — a static
   Vite/React build and a standalone FastAPI service — communicating over REST/GeoJSON with CORS.
   Chosen over a single FastAPI-serves-static-frontend process because the user wants a clear
   separated-architecture story for their CV and is already comfortable operating more than one
   deployable. This is still consistent with decision 0001/the brief's "no
   Kubernetes/microservices/event buses" constraint — it's two simple components, not a
   distributed system.
4. **Database access layer: SQLAlchemy + GeoAlchemy2 + Alembic.** Chosen because the user's team
   already uses this stack professionally — no new tooling to learn, standard PostGIS-in-Python
   path, Alembic gives real schema migrations as the data model evolves.

## Reasoning

Each choice optimises for a different real constraint: React for deliberate skill-building
alignment with the user's team, OpenFreeMap for zero licensing/cost friction consistent with the
project's "inexpensive" hosting goal, decoupled architecture for CV/portfolio presentation despite
being marginally more operational overhead than a single process, and SQLAlchemy/GeoAlchemy2/Alembic
for zero learning-curve cost given existing team familiarity.

## Consequences

- Two separate local dev processes (Vite dev server + FastAPI/uvicorn) during development, with
  CORS configured on the backend for local cross-origin requests.
- Two separate deployment targets eventually needed (e.g. a static host for the frontend build,
  a separate service host for the API) — deferred per the "hosting-agnostic during MVP" stance in
  topic 7, but the architecture should be built with this separation in mind from the start
  (e.g. the frontend must never assume same-origin with the API).
- Alembic migrations must be set up from the first schema change, not retrofitted later.
- If OpenFreeMap ever proves insufficiently reliable/mature, MapTiler's free tier is the documented
  fallback (topic 7/this decision) — swapping tile sources should be a config change, not a
  rearchitecture, so the tile source should not be hardcoded deep in map-init logic.
