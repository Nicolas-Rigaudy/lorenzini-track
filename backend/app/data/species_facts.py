"""Curated natural-history facts per species, keyed by scientific name.

These power the species "learning resource" profile (size schematic, habitat block,
taxonomy, quick facts). We curate them by hand rather than pulling from Wikidata because
the structured coverage of depth range, diet, temperature and size in Wikidata is too
sparse/inconsistent to be reliable. Live image, description and IUCN status are still
fetched client-side from Wikipedia/Wikidata; these fields fill in what those lack.

Sources: IUCN Red List assessments, FishBase, and species literature. Ranges are
"maximum reported" unless noted. Add a new entry when ingesting a new species; the API
degrades gracefully (returns nulls) for a species with no entry here.
"""

from typing import TypedDict


class SpeciesFacts(TypedDict, total=False):
    common_name: str
    taxon_class: str
    taxon_order: str
    taxon_family: str
    body_plan: str  # "shark" | "ray" — selects the size-schematic silhouette
    max_length_m: float
    typical_length_m: float
    max_weight_kg: float
    lifespan_years: int
    depth_min_m: float
    depth_max_m: float
    temp_min_c: float
    temp_max_c: float
    diet: str
    feeding: str
    distribution: str
    habitat: str


SPECIES_FACTS: dict[str, SpeciesFacts] = {
    "Rhincodon typus": {
        "common_name": "Whale shark",
        "taxon_class": "Chondrichthyes",
        "taxon_order": "Orectolobiformes",
        "taxon_family": "Rhincodontidae",
        "body_plan": "shark",
        "max_length_m": 18.8,
        "typical_length_m": 12.0,
        "max_weight_kg": 19000,
        "lifespan_years": 130,
        "depth_min_m": 0,
        "depth_max_m": 1928,
        "temp_min_c": 21,
        "temp_max_c": 30,
        "diet": "Plankton, krill, fish eggs and small fish",
        "feeding": "Filter feeder",
        "distribution": "Circumtropical — all warm-temperate and tropical seas",
        "habitat": "Highly migratory; open ocean and coastal shelves, often near seasonal "
        "plankton blooms such as coral spawning.",
    },
    "Cetorhinus maximus": {
        "common_name": "Basking shark",
        "taxon_class": "Chondrichthyes",
        "taxon_order": "Lamniformes",
        "taxon_family": "Cetorhinidae",
        "body_plan": "shark",
        "max_length_m": 12.3,
        "typical_length_m": 8.0,
        "max_weight_kg": 6000,
        "lifespan_years": 50,
        "depth_min_m": 0,
        "depth_max_m": 1264,
        "temp_min_c": 8,
        "temp_max_c": 15,
        "diet": "Zooplankton (copepods)",
        "feeding": "Filter feeder",
        "distribution": "Coastal-pelagic in boreal to warm-temperate waters of both hemispheres",
        "habitat": "Migratory; surface-feeds on plankton patches in summer, moves to deeper "
        "water in winter.",
    },
}
