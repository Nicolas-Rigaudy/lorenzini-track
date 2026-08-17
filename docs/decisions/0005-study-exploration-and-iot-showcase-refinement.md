# 0005 — Refinement: Historical Study-Exploration Platform + IoT Telemetry Showcase

Status: accepted
Date: 2026-08-17

## Context

Decision 0001 set the product direction as a layered explorer (concepts 1+2+3) with concept 6
(simulated telemetry) as a companion. Decision 0004 established that live/near-live tracking data
is not realistically available, and that the absence is substantially deliberate (poaching
prevention), not just a gap to work around.

## Problem

Given decision 0004, the product's centre of gravity needs to shift from "explorer that might
someday show live movement" to something that's honest about working entirely with historical/
archived data - without that feeling like a downgrade.

## Decision

Refine (not replace) decision 0001's direction:

1. **The core product becomes a historical study-exploration platform.** Positioned explicitly as
   filling the gap between Movebank (rich data, poor public UX) and OCEARCH (great UX, closed/
   narrow data) identified in `docs/research/01-existing-platforms.md` - same gap as before, but
   now framed around "explore studies and their data well," not "watch animals move now."
2. **Concept 6 (simulated telemetry) is promoted from companion module to a primary showcase
   feature**, not just a pipeline-de-risking exercise. Its purpose is now explicitly to
   demonstrate real IoT/connected-device engineering practice (battery drain modelling,
   transmission gaps, Argos-class positional noise, GPS jitter, tag failure) applied to a domain
   outside the user's professional day job - this is the strongest personal-differentiation lever
   available, per the original brief's goal of demonstrating existing engineering expertise
   alongside newly-learned scientific knowledge.
3. Every simulated data point/track must be clearly and persistently labelled as synthetic in the
   UI - never presented ambiguously alongside real historical data (ties to the scientific-rigour
   principle in `docs/research/06-scientific-considerations.md` and decision 0004's "make
   limitations visible" framing).

## Reasoning

This isn't a pivot - concepts 1/2/3 and 6 from decision 0001 are unchanged. What changes is
emphasis: decision 0004 removed "live-ish" as a plausible axis of differentiation, which makes
"quality of historical/study exploration UX" and "engineering-showcase simulation" the two axes
actually worth investing the most design effort in.

## Consequences

- Study-exploration mode (per-study data + summary + source citations) becomes higher priority in
  the near-term roadmap than it was in the original MVP plan.
- The simulated-telemetry module should get more product/UX investment than "a de-risking
  exercise" implies - e.g. a dedicated view/section, not just an internal pipeline test.
- No change to data sources, architecture, or the decisions already made in 0002/0003.
