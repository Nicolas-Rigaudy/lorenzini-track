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
    "Mobula mobular": {
        "common_name": "Giant devil ray",
        "taxon_class": "Chondrichthyes",
        "taxon_order": "Myliobatiformes",
        "taxon_family": "Mobulidae",
        "body_plan": "ray",
        "max_length_m": 5.2,  # disc width (wingspan)
        "typical_length_m": 3.0,
        "max_weight_kg": 400,
        "lifespan_years": 20,
        "depth_min_m": 0,
        "depth_max_m": 700,
        "temp_min_c": 16,
        "temp_max_c": 26,
        "diet": "Zooplankton and small schooling fish",
        "feeding": "Filter feeder",
        "distribution": "Mediterranean Sea and warm-temperate to tropical oceans worldwide",
        "habitat": "Pelagic and deep-diving, often travelling in large schools.",
    },
    "Negaprion brevirostris": {
        "common_name": "Lemon shark",
        "taxon_class": "Chondrichthyes",
        "taxon_order": "Carcharhiniformes",
        "taxon_family": "Carcharhinidae",
        "body_plan": "shark",
        "max_length_m": 3.4,
        "typical_length_m": 2.7,
        "max_weight_kg": 180,
        "lifespan_years": 30,
        "depth_min_m": 0,
        "depth_max_m": 92,
        "temp_min_c": 20,
        "temp_max_c": 30,
        "diet": "Bony fish, crustaceans and rays",
        "feeding": "Active predator",
        "distribution": "Inshore subtropical waters of the western/eastern Atlantic and "
        "eastern Pacific",
        "habitat": "Coastal — mangroves, bays, reefs and shallow sandy flats.",
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
    "Chelonia mydas": {
        "common_name": "Green sea turtle",
        "taxon_class": "Reptilia",
        "taxon_order": "Testudines",
        "taxon_family": "Cheloniidae",
        "max_length_m": 1.5,
        "typical_length_m": 1.1,
        "max_weight_kg": 315,
        "lifespan_years": 90,
        "depth_min_m": 0,
        "depth_max_m": 130,
        "temp_min_c": 20,
        "temp_max_c": 30,
        "diet": "Seagrasses and algae (adults)",
        "feeding": "Herbivore",
        "distribution": "Tropical and subtropical seas worldwide",
        "habitat": "Coastal seagrass pastures; migrates long distances to natal nesting beaches.",
    },
    "Dermochelys coriacea": {
        "common_name": "Leatherback turtle",
        "taxon_class": "Reptilia",
        "taxon_order": "Testudines",
        "taxon_family": "Dermochelyidae",
        "max_length_m": 2.2,
        "typical_length_m": 1.6,
        "max_weight_kg": 900,
        "lifespan_years": 50,
        "depth_min_m": 0,
        "depth_max_m": 1280,
        "temp_min_c": 5,
        "temp_max_c": 30,
        "diet": "Jellyfish and other gelatinous plankton",
        "feeding": "Specialist predator",
        "distribution": "Global — the most widely distributed reptile, tropical to subpolar",
        "habitat": "Open ocean; deep-diving and able to keep warm in cold water.",
    },
    "Halichoerus grypus": {
        "common_name": "Grey seal",
        "taxon_class": "Mammalia",
        "taxon_order": "Carnivora",
        "taxon_family": "Phocidae",
        "max_length_m": 2.6,
        "typical_length_m": 2.0,
        "max_weight_kg": 400,
        "lifespan_years": 40,
        "depth_min_m": 0,
        "depth_max_m": 300,
        "temp_min_c": 2,
        "temp_max_c": 18,
        "diet": "Fish (sandeels, cod, flatfish), some cephalopods",
        "feeding": "Predator",
        "distribution": "Coasts of the North Atlantic, both eastern and western",
        "habitat": "Coastal shelf waters; hauls out on rocky shores, sandbanks and islands.",
    },
    "Trichechus manatus latirostris": {
        "common_name": "Florida manatee",
        "taxon_class": "Mammalia",
        "taxon_order": "Sirenia",
        "taxon_family": "Trichechidae",
        "max_length_m": 4.5,
        "typical_length_m": 3.0,
        "max_weight_kg": 1600,
        "lifespan_years": 65,
        "depth_min_m": 0,
        "depth_max_m": 6,
        "temp_min_c": 20,
        "temp_max_c": 30,
        "diet": "Aquatic and marsh plants (seagrass)",
        "feeding": "Herbivore",
        "distribution": "Coastal southeastern USA, from Florida to the Gulf and Atlantic",
        "habitat": "Shallow coastal waters, estuaries, rivers and warm springs.",
    },
    "Fregata magnificens": {
        "common_name": "Magnificent frigatebird",
        "taxon_class": "Aves",
        "taxon_order": "Suliformes",
        "taxon_family": "Fregatidae",
        "max_length_m": 1.1,
        "max_weight_kg": 2,
        "lifespan_years": 30,
        "diet": "Fish and squid taken at the surface; steals food from other seabirds",
        "feeding": "Aerial surface-feeder / kleptoparasite",
        "distribution": "Tropical and subtropical Atlantic and eastern Pacific",
        "habitat": "Ranges far over warm oceans; nests colonially on islands and mangroves.",
    },
    "Sula leucogaster": {
        "common_name": "Brown booby",
        "taxon_class": "Aves",
        "taxon_order": "Suliformes",
        "taxon_family": "Sulidae",
        "max_length_m": 0.75,
        "max_weight_kg": 1.5,
        "lifespan_years": 25,
        "diet": "Fish and squid",
        "feeding": "Plunge-diver",
        "distribution": "Pantropical coastal seas",
        "habitat": "Tropical coasts and islands; forages over inshore waters.",
    },
    "Sula dactylatra": {
        "common_name": "Masked booby",
        "taxon_class": "Aves",
        "taxon_order": "Suliformes",
        "taxon_family": "Sulidae",
        "max_length_m": 0.85,
        "max_weight_kg": 2.2,
        "lifespan_years": 25,
        "diet": "Fish (esp. flying fish) and squid",
        "feeding": "Plunge-diver",
        "distribution": "Pantropical oceans",
        "habitat": "Offshore tropical waters; nests on remote islands.",
    },
    "Onychoprion fuscatus": {
        "common_name": "Sooty tern",
        "taxon_class": "Aves",
        "taxon_order": "Charadriiformes",
        "taxon_family": "Laridae",
        "max_length_m": 0.4,
        "max_weight_kg": 0.24,
        "lifespan_years": 32,
        "diet": "Small fish and squid snatched from the surface",
        "feeding": "Aerial surface-feeder",
        "distribution": "Pantropical oceans",
        "habitat": "Highly pelagic, spending years at sea; nests in dense island colonies.",
    },
    "Phaethon aethereus": {
        "common_name": "Red-billed tropicbird",
        "taxon_class": "Aves",
        "taxon_order": "Phaethontiformes",
        "taxon_family": "Phaethontidae",
        "max_length_m": 0.5,
        "max_weight_kg": 0.7,
        "lifespan_years": 30,
        "diet": "Fish and squid",
        "feeding": "Plunge-diver",
        "distribution": "Tropical Atlantic, eastern Pacific and Indian Oceans",
        "habitat": "Wide-ranging over warm oceans; nests on cliffs of tropical islands.",
    },
}
