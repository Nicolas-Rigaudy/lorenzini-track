# 0010 — Sensitivity Policy by IUCN Status

Status: proposed
Date: 2026-10-22

## Context

[0004](0004-no-live-tracking-data.md) explains why animal positions are not published live.
Item_003 needs rules that fix how fine a published position may be and how old it must be.
The values below are the first proposal and need the owner's confirmation.

## Decision

Rules run in processing (`app/processing/sensitivity.py`), before tracks are stored, so
every export and every API layer sees the same positions.

- Positions snap to the centre of a grid cell. The point's error grows to the cell's
  half-diagonal if that is larger than the Argos class error.
- A publication delay drops points newer than the delay. It applies only when a reference time
  is passed, because the simulated fleet has no real "now".
- An unknown status gets the strictest level.

| IUCN status | Grid (degrees) | Delay (days) |
|---|---|---|
| CR, DD | 0.5 | 730 |
| EN | 0.25 | 365 |
| VU | 0.1 | 180 |
| NT | 0.05 | 90 |
| LC | none | 0 |

The default rule list uses the CR row: the simulated fleet is scalloped hammerhead
(Sphyrna lewini), critically endangered.

## Consequences

- Published hammerhead positions are 0.5 degree cells (about 55 km). Fine movement is not visible.
- The delay is a policy value for real data in 1.2; it has no effect on simulated tracks.
- The UI explainer and per-point "why" (item_003 AC1) still need a visual design.
