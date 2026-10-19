# 0002 — Flagship Movement Dataset: Ningaloo Outlook Whale Shark Tracking (GBIF, aggregated)

Status: superseded by [0007](0007-lorenzini-track-framing.md) (was accepted as interim)
Date: 2026-08-17

## Context

Decision 0001 requires one real, curated animal-movement dataset to anchor the MVP's flagship
track feature (concept 2) and demonstrate telemetry uncertainty (concept 3). The user's preferred
species was the scalloped hammerhead shark, with openness to other shark species.

## Problem

Finding a dataset that is simultaneously (a) a real shark species, (b) genuine lat/lon satellite
telemetry (not just depth/temperature sensor data), (c) zero-friction to access (no registration
or permission request), and (d) rich enough to demonstrate telemetry uncertainty, proved difficult:
most published shark satellite-tracking studies do not state where their raw data is publicly
deposited, and platforms that do host it (OBIS-SEAMAP, Movebank) largely gate raw per-fix data
behind per-study/per-dataset permission requests.

## Alternatives considered

1. **Scalloped hammerhead depth/temperature/accelerometer data** (Dryad, DOI
   10.5061/dryad.p8cz8w9v0, Kāneʻohe Bay, Hawaiʻi, 10 sharks) — confirmed real and openly
   licensed, but has no lat/lon positions (archival dive-depth data only, from a single release
   site) — cannot support a map-based track feature. **Deferred to a later feature** (dive-behaviour/
   thermoregulation storytelling), not dropped.
2. **Ningaloo Outlook Whale Shark tracking, raw per-fix** (OBIS-SEAMAP/CSIRO, Ningaloo Reef,
   Western Australia) — real Argos satellite telemetry with lat/lon, timestamps, **and per-fix
   location class** (Argos accuracy indicator) — an excellent match for concept 3, but access is
   "permission required" via OBIS-SEAMAP registration + stated intent. **Kept as a follow-up
   option**, not selected now.
3. **Ningaloo Outlook Whale Shark tracking, GBIF-aggregated** (chosen) — same underlying study,
   published to GBIF pre-aggregated to 1° grid cells, Darwin Core Archive, directly downloadable
   with no login (`https://ipt.env.duke.edu/archive.do?r=zd_1298_1deg`), CC BY-NC 4.0.

## Decision

Use the GBIF-published, 1°-cell-aggregated Ningaloo Outlook Whale Shark tracking dataset to build
and validate the ingestion→store→serve pipeline and the map/track UI first.

## Reasoning

Zero access friction lets Month 1–2 work (pipeline, API, frontend map) start immediately without
waiting on a registration/approval process. The tradeoff is explicit and accepted: 1°-cell
aggregation removes the per-fix Argos location-class field that would otherwise directly power the
uncertainty-visualisation feature (decision 0001, concept 3) — this dataset alone cannot fully
deliver that differentiator.

## Consequences

- The MVP's initial track feature will be species = **whale shark**, not scalloped hammerhead —
  a deliberate, temporary substitution for pipeline-building purposes, not a final species choice.
- Concept 3 (uncertainty visualisation) cannot be fully realised on this aggregated dataset alone.
  **Follow-up action**: register for the raw, per-fix Ningaloo dataset via OBIS-SEAMAP (alternative
  2 above) once the pipeline is working, to unlock real location-class/uncertainty data — or
  register for a genuinely open raw hammerhead satellite-position dataset if one is later confirmed.
- The hammerhead depth/temperature dataset (alternative 1) remains a real, ready-to-use option for
  a later diving-behaviour feature and should not be re-researched from scratch.
- This decision should be revisited once the core pipeline exists — it is explicitly an interim,
  pipeline-unblocking choice, not a final statement that whale sharks replace hammerheads as the
  project's flagship species.
