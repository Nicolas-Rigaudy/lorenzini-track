# 0006 — Second Study Dataset: Manx Basking Shark Watch

Status: accepted
Date: 2026-08-17

## Context

Decision 0005 refined the product toward a historical study-exploration platform. Building
species-browsing features (filter studies by species, a species page listing all its studies)
genuinely needs at least two studies/species to test against - a single-study dataset can't
validate that a filter or list actually works.

## Decision

Ingest a second real, zero-friction dataset using the same GBIF/OBIS-SEAMAP STAT pattern as
decision 0002: **Manx Basking Shark Watch 2017-2018** (GBIF dataset
`20b89c9f-0a89-4fb6-9dd0-473bba1f656d`), species *Cetorhinus maximus* (basking shark) - a
different genus from the whale shark dataset already ingested.

Verified directly (not assumed) before use: 3 real occurrence records, Irish Sea region, 2017,
CC BY-NC 4.0 licence, same Darwin Core Archive structure as decision 0002's dataset.

## Reasoning

Same zero-friction rationale as decision 0002 (direct download, no registration). Chosen
specifically because it's a *different* shark genus, not more whale shark data, so
species-filtering/browsing features have a real second species to distinguish.

The shared ingestion logic (fetching, EML parsing, upserting) was extracted from
`gbif_whale_sharks.py` into `app/ingestion/stat_archive.py` once a second dataset needed the
same logic, with `gbif_whale_sharks.py` and the new `gbif_basking_shark.py` reduced to thin
per-dataset entry points (archive URL only).

## Consequences

- Adding further STAT/OBIS-SEAMAP-origin datasets going forward should follow the same
  thin-wrapper-over-`stat_archive.ingest()` pattern rather than duplicating the parsing logic.
- This dataset is very small (3 records) - fine for validating multi-study UI, but not meant to
  be a rich example on its own.
