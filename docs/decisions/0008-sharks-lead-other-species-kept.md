# 0008 — Sharks Lead, Other Species Stay

Status: accepted
Date: 2026-10-19
Supersedes: the "sharks only" scope line in [0007](0007-lorenzini-track-framing.md)

## Context

Decision 0007 (2026-10-16) set the scope to sharks only: non-shark taxa were to be cut from
code, ingestion scripts and species facts, together with taxon-family colouring and the undersea
feature layer. Milestone 0.2 stopped before the deletions, waiting for the owner to confirm them.

## Decision

On 2026-10-19 the owner replaced the shark-only scope:

- **Sharks lead.** Sharks stay the headline story, the default map and list view, and the
  simulated tag fleet (scalloped hammerheads, unchanged from 0007).
- **Other species stay.** The non-shark datasets (devil ray, turtles, grey seal, manatee,
  seabirds) stay in the data and the UI, reachable through a taxon-family filter. Nothing
  species-related is deleted: ingestion scripts, `species_facts.py` entries, colours and media
  stay.
- **Taxon-family colouring stays.** Each family keeps one base hue and its species are shades
  of it.
- **Sharks get a wider blue→cyan range** (owner, 2026-10-19), so each shark species is easy to tell apart; other families keep their single hue.
- **Undersea feature names stay.** The GEBCO undersea feature layer is map detail for the sea,
  not species content. Land detail stays as it is for now; the owner will judge later whether
  it distracts.
- **Point caps stay off.** The map returns every matching occurrence until tiles arrive in
  milestone 0.5.

Everything else in 0007 stands: the name, the portfolio purpose, the simulated hammerhead fleet
as flagship, real data as context, licences and hosting.

## Reasoning

- The other datasets cost little to keep and show that the pipeline and the explorer are not
  tied to one taxon.
- Defaulting to sharks keeps the story readable: a first-time visitor sees sharks first and
  finds the rest only by asking for it.

## Consequences

- Milestone 0.2 no longer deletes code; it makes sharks the default view and adds the taxon
  filter.
- The simulated fleet, uncertainty and sensitivity work (0.3, 0.4) stays shark-only. The
  sensitivity rules in 0.4 apply to every animal-position layer, non-shark ones included.
- The licence register (0.4) covers the non-shark datasets too, since they stay in the demo.
