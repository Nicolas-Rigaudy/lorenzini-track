# Licence register

Every dataset, photo and basemap the demo uses. "Checked" is the date the licence was read at
the source named in the row. Rows marked "to check" were not read at the source yet.
The Darwin Core archives come from the OBIS-SEAMAP IPT (`https://ipt.env.duke.edu/eml.do?r=<id>`);
the licence is the `intellectualRights` text of that EML file.

## Datasets

| Dataset | Provider | Licence | Source | Checked |
|---|---|---|---|---|
| Ningaloo Outlook Whale Shark tracking (1-degree cells) | Bardi Jawi Turtle Tracking | CC BY-NC 4.0 | zd_1298_1deg, https://doi.org/10.82144/ceda90f3 | 2026-10-22 |
| Manx Basking Shark Watch 2017-2018 (1-degree cells) | Manx Basking Shark Watch | CC BY-NC 4.0 | zd_1512_1deg, https://doi.org/10.82144/e5db0624 | 2026-10-22 |
| MesoAmerican Reef shark habitat and environmental preferences (1-degree cells) | MarAlliance | CC BY-NC 4.0 | zd_1225_1deg, https://doi.org/10.82144/65b7cbea | 2026-10-22 |
| Basking shark long-term biologging (breaching behaviour study) | Edinburgh Napier University | CC BY-NC 4.0 | zd_2383, https://seamap.env.duke.edu/dataset/2383 | 2026-10-22 |
| Giant Devil Rays in the North-Western Mediterranean Sea | Tethys Research Institute | CC BY-NC 4.0 | zd_1370, https://doi.org/10.82144/8be2e338 | 2026-10-22 |
| Green sea turtle telemetry in Northwest Costa Rica | Fundacion Oceanografic | CC BY-NC 4.0 | zd_2385, https://seamap.env.duke.edu/dataset/2385 | 2026-10-22 |
| Grey seals GPS telemetry in Molene Archipelago | CEBC | CC BY-NC 4.0 | zd_2028, https://doi.org/10.82144/5f44abaf | 2026-10-22 |
| Leatherback Tracking in South Africa | University of Pisa | CC BY 4.0 | zd_439, https://doi.org/10.82144/e379e535 | 2026-10-22 |
| Florida Manatee Synoptic Aerial Survey 1991-2019 | Florida FWC, FWRI | CC BY-NC 4.0 | zd_765, https://doi.org/10.82144/2b3f1ae9 | 2026-10-22 |
| University of Liverpool seabird tracking in Anguilla 2012-2015 | University of Liverpool | CC BY-NC 4.0 | zd_1279, https://doi.org/10.82144/aef3a0fc | 2026-10-22 |
| IMOS Animal Tracking Facility, acoustic detections 2007-2021 | IMOS | CC BY 4.0 | GBIF dataset 3f4d4bf1-5f9a-43f2-a0d8-ff6ed5952796, https://doi.org/10.15468/3h7tnh | 2026-10-22 |
| Simulated hammerhead fleet (this repo) | Lorenzini Track | CC BY 4.0 (proposed, owner confirms) | `backend/app/simulator` | n/a |

Notes:
- Nine of the eleven real datasets are CC BY-NC. The demo is non-commercial, so they can be
  shown with attribution. A commercial use of the site or its exported files would need each
  provider's permission.
- The IMOS dataset is not part of 1.0 (owner decision 2026-10-16) and is not loaded by the
  Pages workflow. Its licence is recorded for 1.2.
- Each stored occurrence keeps its `license` field from the archive.

## Photos and diagrams

Curated in `frontend/src/speciesMedia.ts`, all from Wikimedia Commons, read through the
Commons API (`extmetadata`) on 2026-10-22.

| File | Licence |
|---|---|
| Basking-Shark-Scale-Chart-SVG-Steveoc86-001.svg | CC BY-SA 4.0 |
| Whale-Shark-Scale-Chart-SVG-Steveoc86.svg | CC BY-SA 4.0 |
| Bull_shark_size.svg | CC BY-SA 4.0 |
| Tiger_shark_size.svg | CC BY-SA 3.0 |
| Requin bouledogue (Carcharhinus leucas) (Ifremer 00813-92510 - 53590).jpg | CC BY 4.0 |

The species pages also load the lead image and text of each species' Wikipedia article at
runtime. Those images carry their own licences on Commons and the UI shows no per-image credit
yet.

## Basemap and context layers

| Layer | Provider | Licence | Checked |
|---|---|---|---|
| Basemap (OpenFreeMap Liberty style) | OpenFreeMap, OpenMapTiles, OpenStreetMap | to check (OSM data is ODbL) | no |
| Bathymetry tiles (EMODnet Bathymetry base layer) | EMODnet, GEBCO | to check | no |
| Undersea feature names | GEBCO/SCUFN via NOAA NCEI | to check | no |
| Species text and status | Wikipedia, Wikidata | to check (CC BY-SA, CC0) | no |

## Open

- Read and record the "to check" rows, then show an attribution for each visible layer. The
  map shows only the EMODnet / GEBCO line today.
- Credit lines for the Wikimedia images in the species pages.
