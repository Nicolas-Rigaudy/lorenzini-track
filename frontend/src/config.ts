export const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

// OpenFreeMap (https://openfreemap.org) - free, open, no API key required.
// Kept as a config value (not hardcoded in map-init logic) so switching to
// another vector-tile provider (e.g. MapTiler) later is a one-line change.
export const MAP_STYLE_URL = import.meta.env.VITE_MAP_STYLE_URL ?? 'https://tiles.openfreemap.org/styles/liberty'

// EMODnet Bathymetry World Base Layer (EBWBL) - GEBCO-derived globally, higher-resolution
// EMODnet grid around Europe. Free, no API key. https://tiles.emodnet-bathymetry.eu/
// This is a raster (not vector) tile source covering land + sea depth/elevation relief.
// Proxied through our own backend (app/api/routes/tiles.py) because the upstream server
// sends no CORS headers, so browsers can't load its tiles cross-origin directly.
export const BATHYMETRY_TILE_URL =
  import.meta.env.VITE_BATHYMETRY_TILE_URL ?? `${API_BASE_URL}/tiles/bathymetry/{z}/{x}/{y}.png`

// GEBCO/SCUFN Gazetteer of Undersea Feature Names (ridges, trenches, seamounts, etc.),
// hosted by NOAA/NCEI as a public Esri Feature Service (CORS-open, no API key required).
// https://www.gebco.net/data-products/undersea-feature-names
export const UNDERSEA_FEATURE_NAMES_URL =
  import.meta.env.VITE_UNDERSEA_FEATURE_NAMES_URL ??
  'https://services2.arcgis.com/C8EMgrsFcRFL6LrL/arcgis/rest/services/Undersea_Features/FeatureServer/0/query'
