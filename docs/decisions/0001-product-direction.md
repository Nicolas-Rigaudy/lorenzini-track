# 0001 — Product Direction: Layered Explorer (Concepts 1+2+3) with a Simulated-Telemetry Companion (Concept 6)

Status: accepted
Date: 2026-08-17

## Context

The project kickoff required a research phase (see `docs/research/00-summary-and-recommendations.md`
and the seven supporting topic docs) before any implementation, to avoid cloning an existing
platform (OCEARCH, Movebank, OBIS, etc.) without genuine differentiation.

## Problem

Eight candidate product concepts were identified and evaluated (`docs/research/05-product-opportunities.md`).
No single concept was obviously best in isolation — several were complementary rather than
competing, and some (data-quality layer, regional navigation) were really features rather than
standalone products.

## Alternatives considered

- Build concept 1 (biodiversity+environment explorer) alone — safest, highest data feasibility,
  but least differentiated from what OBIS/GBIF already effectively enable.
- Build concept 3 (telemetry uncertainty explainer) alone — most original, but narrow surface area
  and less demo-able without real tracks to visualise uncertainty on.
- Build concept 6 (simulated telemetry) as the primary product — lowest external-dependency risk,
  strong fit to existing IoT background, but weaker marine-biology learning value on its own.
- Build all three core concepts as one layered product (chosen).

## Decision

Build concepts 1, 2, and 3 as layers of a single product, not separate builds:
- **Concept 1** (species/place + environmental context) is the foundation/navigation layer.
- **Concept 2** (individual animal movement) is the flagship interactive feature.
- **Concept 3** (telemetry technology/uncertainty explainer) is the scientific differentiator,
  applied wherever concept 2's tracks or concept 1's occurrence data are shown.

**Concept 6** (simulated telemetry / digital twin) is adopted as an early companion module, to be
built before or alongside real external-data integration, specifically to de-risk the
ingestion→store→serve pipeline with zero external API dependency.

Concepts 4 (data-quality/effort) and 7 (regional navigation) become design principles/features
within concept 1 rather than standalone builds. Concepts 5 (conservation intelligence) and 8
(3D/depth) are deferred as credible v2 expansions.

## Reasoning

No existing platform (topic 1 research) combines multi-species biodiversity, movement, environmental
context, and visible data-quality/uncertainty in one open tool — this gap is best filled by an
integrated product, not a single-feature one. Concept 3 specifically is backed by concrete,
sourced mechanisms (Argos accuracy classes, occupancy-model effort/detection separation — see
`docs/research/06-scientific-considerations.md`), not just intent, making it a credible
differentiator rather than a marketing angle. Concept 6 reuses the user's professional
IoT/fleet-management background directly and requires no external data source to start building
against, making it a low-risk way to validate the pipeline early.

## Consequences

- MVP scope is deliberately narrow (see `docs/research/00-summary-and-recommendations.md` §9): one
  environmental variable, one curated real track, one synthetic track, conservation status —
  rather than broad coverage of any single dimension.
- Telemetry access (concept 2/3) becomes the primary external-dependency risk, since Movebank/OTN
  data is per-study/permission-gated (see decision 0002 for the specific dataset chosen).
- Scope-creep risk (adding "just one more layer") must be actively guarded against — the phased
  6-month evolution path exists specifically to sequence this.
