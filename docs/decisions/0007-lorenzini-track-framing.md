# 0007 — Lorenzini Track: Shark Telemetry Showcase, Simulated Fleet as Flagship

Status: accepted; scope line superseded by [0008](0008-sharks-lead-other-species-kept.md)
Date: 2026-10-16 (recorded 2026-10-19)
Supersedes: the interim flagship choice in [0002](0002-flagship-track-dataset.md)

## Context

The 0.1 prototype (codename poseidon) grew into a broad marine-wildlife explorer: eleven real
datasets across sharks, a ray, turtles, a seal, a manatee and seabirds. Decision 0002 picked the
GBIF-aggregated Ningaloo whale shark data as an *interim* flagship to unblock the pipeline, and
said it should be revisited once the pipeline existed. It now exists.

Two things did not change since 0002: open, per-fix shark satellite tracks are still mostly
access-restricted, and decision 0004 still rules out publishing precise, recent positions of
threatened animals.

## Decision

On 2026-10-16 the owner reframed the project:

- **Name:** Lorenzini Track, "an open research project on shark telemetry, from tag to map",
  after Stefano Lorenzini, who described the ampullae of Lorenzini in 1678. `poseidon` stays only
  as a codename in history notes and the local folder name.
- **Purpose:** a portfolio showcase. 1.0 is a live demo link plus a case-study README, not an
  installable product.
- **Scope:** sharks only. Other taxa are cut from code, data scripts and facts. *(Superseded on
  2026-10-19 by [0008](0008-sharks-lead-other-species-kept.md): sharks lead, other species stay.)*
- **Flagship:** a seeded, simulated fleet of scalloped hammerheads off eastern Australia, with
  fin-mounted satellite tags and acoustic tags, built from published movement models and labelled
  as simulated everywhere. It replaces the whale shark data as the flagship.
- **Real data:** open shark occurrences (OBIS/GBIF) and environmental layers are context, shown
  with their caveats and under the sensitivity rules. No real IMOS detections in 1.0.
- **Licences and hosting:** MIT for code, CC BY 4.0 for docs and simulated data, non-commercial
  demo; static hosting on GitHub Pages, personal domain later.

The product brief (`logics/product/prod_001_lorenzini_track_shark_telemetry_from_tag_to_map.md`)
and the roadmap (`logics/roadmap/road_001_lorenzini_track_to_1_0.md`) hold the detail.

## Reasoning

- A simulated fleet is the only way to show per-fix uncertainty (Argos location classes, acoustic
  detection ranges, gaps) without restricted data, and it is fully reproducible from a seed.
- Simulation also lets the project show the engineering side, from tag to gateway to processing,
  which open occurrence data cannot.
- One story (shark telemetry) reads better as a showcase than a broad multi-taxon explorer.

## Consequences

- The whale shark 1° data is context, not a track; 0002's follow-up to request raw Ningaloo
  fixes is dropped for 1.0.
- 0002's "hammerhead remains the preferred species" is now delivered through simulation.
- Milestone 0.2 removes non-shark ingestion scripts, facts, colours and the undersea POI layer,
  and renames the project (the removals were dropped by 0008); later milestones build the
  simulator, pipeline and views.
- Decision 0001's "no message bus" will be revisited separately when MQTT is added for the
  simulated near-real-time trackers (milestone 0.3). *(Revisited in [0009](0009-two-transport-networks.md): Argos-style
  batches for satellite tags, MQTT for near-real-time trackers.)*
