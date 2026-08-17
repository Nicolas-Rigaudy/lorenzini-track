# 06 — Scientific Considerations

Status: draft (research phase, topic 6 of N)

Purpose: establish the vocabulary and evidence base for scientific rigour — the distinctions the
product must respect, and the concrete bias/uncertainty mechanisms behind each data type. This
directly underpins concept 3 (telemetry/uncertainty explainer) from topic 5, and constrains how
*any* chosen concept may present data.

---

## The core distinctions (what the data actually is)

| Term | Meaning | Source in this project |
|---|---|---|
| **Observation / Occurrence** | A record that a species was seen/detected at a place and time, by some observer/method, with no implied continuity. | OBIS/GBIF Darwin Core `Occurrence` records |
| **Detection** | A binary/probabilistic signal that an already-tagged animal was near a fixed sensor (e.g. acoustic receiver) — tells you presence-in-range, not exact position. | OTN acoustic telemetry |
| **Telemetry location / fix** | An estimated position of a tagged individual at a point in time, itself an *estimate* with an associated error (see Argos below), not a ground-truth coordinate. | Movebank/Argos satellite tags |
| **Reconstructed track** | A path built by connecting/interpolating/filtering a sequence of telemetry locations — inherently a **model output**, not raw data; different reconstruction methods (state-space models, Kalman filtering) produce different tracks from the same raw fixes. | Derived, not a primary data type |
| **Distribution** | Where a species is known/inferred to occur, typically built from aggregated occurrence records — reflects *where people looked and found something*, not necessarily the species' full range. | Derived from OBIS/GBIF |
| **Abundance** | How many individuals exist/are present — occurrence/presence data alone **cannot** support abundance claims without an explicit sampling-design correction (e.g. distance sampling, capture-recapture) that this project's data sources generally do not provide. | Out of scope for direct claims |
| **Habitat suitability** | A modelled prediction of where conditions are suitable for a species, from a species distribution model (SDM) combining occurrence + environmental covariates — again a **model output** with its own assumptions and error, not observed fact. | Possible future derived layer, not raw data |
| **Population estimate** | A number derived from structured survey methodology — this project's opportunistic/citizen-science-adjacent and telemetry data sources do **not** support this without borrowing external published estimates (e.g. citing IUCN assessment population figures directly rather than deriving one). | Never derive; only cite external assessments |

**Working rule for the product**: every visualisation must be labelled with the correct term from
this table (or a plain-language equivalent), and the UI must never silently upgrade "occurrence
records exist here" into "the species lives here" or "distribution" into "abundance." This is a
direct, checkable design constraint, not just an intention.

---

## Sampling bias / observation effort (biodiversity data)

- Citizen-science / opportunistic occurrence data (which underlies a meaningful share of
  OBIS/GBIF records) is **convenience-sampled**: contributors choose what, where, and when to
  record, with no standardized protocol. This means occurrence density is a *confound* of two
  things — the ecological process (species actually being there) and the observation process
  (someone being there to look, being willing/able to identify it correctly).
- **Occupancy modelling** is the standard ecological framework for separating "probability the
  species is present" from "probability it was detected given it's present" — using covariates
  like observer effort, expertise, time of day, and survey method. This project is unlikely to run
  full occupancy models at MVP, but the *concept* (effort ≠ presence/absence signal) should shape
  any UI that shows raw occurrence density, e.g. by pairing an occurrence map with an effort/record
  density map so users can visually separate "few sightings" from "few observers."
- **Practical implication for concept 4/1 from topic 5**: a naive heatmap of OBIS points will look
  like a map of human research/tourism activity as much as a map of animal presence — this is the
  single most important scientific-honesty risk in this project and should be called out
  explicitly wherever occurrence data is shown.

Sources: [Estimates of observer expertise improve species distributions from citizen science data](https://besjournals.onlinelibrary.wiley.com/doi/10.1111/2041-210X.12838),
[occAssess: assessing potential biases in species occurrence data](https://pmc.ncbi.nlm.nih.gov/articles/PMC8601935/),
[Using Semistructured Surveys to Improve Citizen Science Data](https://academic.oup.com/bioscience/article/69/3/170/5382641)

---

## Telemetry spatial uncertainty (satellite tracking)

- **Argos system location classes**: each fix is assigned an error class (3, 2, 1, 0, A, B, in
  decreasing accuracy) with nominal uncertainty of <250m (class 3) down to >1500m (class 0), and
  classes A/B carrying unreported errors that can range **8,000m–30,000m**.
- **Critical, easily-missed fact**: for many real marine tracking studies, the *least accurate*
  classes (0, A, B, Z) dominate the dataset — one cited elephant seal study had **89% of its
  fixes in the low-accuracy classes**. A naive "connect the dots" track visualisation will imply
  far more positional precision than the underlying data supports.
- **Species-specific variation**: accuracy also varies by species/behaviour (e.g. deep-diving
  whales surface less often, degrading fix quality further) — meaning uncertainty isn't a single
  constant to apply uniformly, it varies per point and per species.
- **Reconstruction is a modelling choice**: converting a noisy fix sequence into a "track" (via
  state-space models, Kalman filtering, or simple interpolation) produces materially different
  results depending on method — the product should be honest that any displayed "path" is one
  possible reconstruction, not a recorded fact, ideally by showing raw fixes (with error radius)
  alongside/underneath any smoothed track line.
- **Design implication for concept 2/3**: this is exactly the kind of thing that makes concept 3
  (telemetry uncertainty explainer) both scientifically important and genuinely differentiated —
  showing error ellipses/classes on real Argos-based tracks, rather than hiding them, is a concrete
  and checkable feature, not just a principle.

Sources: [Error Properties of Argos Satellite Telemetry Locations](https://www.researchgate.net/publication/236925154_Error_Properties_of_Argos_Satellite_Telemetry_Locations_Using_Least_Squares_and_Kalman_Filtering),
[An at-sea assessment of Argos location accuracy for three species of large whales](https://animalbiotelemetry.biomedcentral.com/articles/10.1186/s40317-020-00207-x),
[Modelling animal movement using the Argos satellite telemetry location error ellipse](https://besjournals.onlinelibrary.wiley.com/doi/full/10.1111/2041-210X.12311),
[Moderating Argos location errors in animal tracking data](https://besjournals.onlinelibrary.wiley.com/doi/abs/10.1111/j.2041-210X.2012.00245.x)

---

## Acoustic telemetry uncertainty (different failure mode than satellite)

Not covered by fresh search this round but established from topic 1/2 findings and general
domain knowledge to confirm later with a dedicated source pass if concept 2/3 is selected:

- Acoustic detections are **presence-in-range**, not position — a detection only tells you the
  tagged animal was within a receiver's detection radius (which itself varies with noise,
  bathymetry, water conditions) at that time.
- Absence of detection is **not** evidence of absence — it could mean the animal wasn't near any
  receiver, a real coverage gap rather than a biological signal — receiver array placement is
  itself a major source of spatial bias (arrays cluster near river mouths, coastlines,
  research-funded regions).
- **Design implication**: acoustic and satellite data should never be shown on the same map with
  the same visual weight/style without a clear legend distinguishing "estimated position ± error"
  from "detected within range of a receiver at this location" — conflating the two is a realistic
  and easy-to-make scientific-honesty mistake.

**Flag**: verify this section against a primary OTN/acoustic-telemetry methods source before
publishing any acoustic-telemetry feature — currently based on general domain knowledge rather
than a source fetched this session.

---

## Other bias/uncertainty categories to keep in view (lighter treatment, revisit if relevant concept is chosen)

- **Tag failure / battery degradation** — telemetry time series often end abruptly (tag failure,
  battery death, animal death, tag detachment) rather than at a natural/meaningful stopping point;
  a track "ending" on a map should not be visually implied as the animal stopping there.
- **Transmission gaps** — satellite tags only transmit when the animal surfaces; deep/long dives
  create real temporal gaps, not just spatial ones — gap length itself is informative (species
  diving behaviour) but must not be silently interpolated away.
- **Species identification uncertainty** — particularly relevant for citizen-science observations
  of visually similar species (e.g. shark species misidentification) — Darwin Core has an
  `identificationVerificationStatus`-type field for this; worth surfacing rather than dropping at
  ingestion.
- **Geographic sampling bias** — well-funded/accessible regions (US/Europe/Australia coastlines)
  are dramatically overrepresented in both occurrence and telemetry data relative to
  under-resourced regions — a genuinely global product should visualise this bias rather than
  present a misleadingly even-looking global map.

---

## Working principle for the whole product

Every layer of the product touches at least one of these distinctions. Rather than treating
scientific rigour as a caveat/disclaimer bolted onto the UI, the strongest version of any chosen
concept treats **making these limitations visible as a feature**, not a compliance checkbox — this
was explicitly identified as a possible differentiator in the original brief and is now backed by
concrete, sourced mechanisms (Argos error classes, occupancy-model effort/detection separation,
acoustic presence-vs-position) rather than a vague intention. This should be treated as a
non-negotiable constraint on whatever concept is ultimately chosen, not an optional polish item
for later.
