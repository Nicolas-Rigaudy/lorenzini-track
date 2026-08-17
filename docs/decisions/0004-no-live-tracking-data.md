# 0004 — No Live/Near-Live Animal Tracking Data, By Design (Not Just By Availability)

Status: accepted
Date: 2026-08-17

## Context

After building the first real ingestion pipeline (whale shark occurrences, decision 0002), we
investigated whether a "somewhat live" (delayed by hours/days, not real-time) animal-movement
feed was achievable, to support a more dynamic product than a single historical dataset.

## Problem

Is there any freely available, actively-updating marine wildlife tracking data source, and if
not, why not?

## Investigation

- **Movebank**: has a genuine near-live data pipeline ("thousands of active tags sending over
  3 million new data records daily") and API access is achievable with a free account (HTTP
  Basic Auth + a documented license-acceptance flow for gated studies). However, **direct search
  of the Movebank Data Repository for every major shark genus (Carcharodon, Galeocerdo, Sphyrna,
  Rhincodon, Prionace) returned zero results.** Sharks are not meaningfully represented on
  Movebank at all.
- **OBIS-SEAMAP/STAT** (the system behind our whale shark dataset): raw per-fix data requires a
  per-dataset registration with a written justification - real friction, and even once granted,
  checking the specific manta ray dataset we sampled showed a **2014-2022** date range, published
  in 2025 - i.e. fully historical despite the recent publication date.
- **Root cause, part 1 (structural)**: satellite/acoustic tags have finite battery life (days to
  months); research papers using the data are typically published years after tagging ends;
  public repositories only receive data post-publication. This alone explains most of the lag.
- **Root cause, part 2 (deliberate, and the more important one)**: the Ocean Tracking Network
  explicitly documents a **default data embargo of "the duration of the tag's battery life plus
  two years"** specifically to prevent poaching/harm
  ([source](https://oceantrackingnetwork.org/addressing-concerns-in-the-misuse-of-animal-tracking-data/)).
  Cited real incidents: tagged sharks in Western Australia were killed by authorities after being
  tracked; Bengal tiger GPS collar data was targeted by poachers; radio-tagged wolves and bears in
  North America were located and persecuted using their own tracking signals. This is standard,
  ethically-motivated practice across the field, not specific to one dataset or organisation.

## Decision

**Do not build toward live/near-live tracking as a product goal.** Treat the absence of live
data as an expected, structural, and partly deliberate property of responsible wildlife
telemetry - not a gap to keep searching for a way around.

Instead:
1. Continue using historical/archived datasets (whale shark occurrences already ingested;
   others to follow) for the movement/telemetry features (concepts 2/3 from decision 0001).
2. Add an explicit, visible explainer in the product itself: **why real-time animal locations
   are intentionally not shown**, citing the poaching-risk rationale above. This turns a
   limitation into a demonstration of the project's core "make data limitations and scientific
   context visible" differentiator (decision 0001, `docs/research/06-scientific-considerations.md`).
3. Keep the free Movebank account created during this investigation for a possible future
   non-shark marine species example (e.g. manta rays, sea turtles), not for live-data purposes.

## Consequences

- No feature work should be planned around "live tracker" as a goal.
- The product's messaging is stronger for this finding, not weaker: explaining *why* there's no
  live map of shark locations is itself a scientific-literacy and conservation-ethics teaching
  moment, consistent with the project's original learning objectives (conservation biology,
  telemetry limitations).
- If a genuinely active, public, low-embargo study is found later for a non-shark species, it can
  still be added as a secondary example - this decision rules out *searching further for shark
  live data specifically*, not all future near-live integrations.
