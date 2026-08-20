import { useEffect, useRef } from 'react'
import maplibregl, { type Map as MapLibreMap, type StyleSpecification } from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { API_BASE_URL, BATHYMETRY_TILE_URL, MAP_STYLE_URL } from '../config'
import { fetchAllUnderseaFeatureNames } from '../underseaFeatures'
import { fetchSpeciesSummary } from '../species'
import type { SpeciesListItem } from '../speciesApi'
import { speciesPhoto } from '../speciesMedia'

// OpenFreeMap's vector style has no ocean-depth/elevation data (OSM doesn't map the seafloor).
// We keep only its boundary/label layers and put the EMODnet bathymetry raster underneath,
// so we get real depth/elevation relief for both land and sea instead of flat fill colours.
const KEPT_VECTOR_LAYER_IDS = new Set([
  'boundary_3',
  'boundary_2',
  'boundary_disputed',
  'waterway_line_label',
  'water_name_point_label',
  'water_name_line_label',
  'label_other',
  'label_village',
  'label_town',
  'label_state',
  'label_city',
  'label_city_capital',
  'label_country_3',
  'label_country_2',
  'label_country_1',
])

async function buildStyle(): Promise<StyleSpecification> {
  const baseStyle: StyleSpecification = await fetch(MAP_STYLE_URL).then((r) => r.json())

  return {
    version: baseStyle.version,
    glyphs: baseStyle.glyphs,
    sprite: baseStyle.sprite,
    sources: {
      ...baseStyle.sources,
      bathymetry: {
        type: 'raster',
        tiles: [BATHYMETRY_TILE_URL],
        tileSize: 256,
        maxzoom: 15,
        attribution: 'Bathymetry: EMODnet / GEBCO',
      },
    },
    layers: [
      {
        id: 'bathymetry',
        type: 'raster',
        source: 'bathymetry',
        paint: {
          'raster-saturation': -0.3,
        },
      },
      {
        id: 'bathymetry-blue-wash',
        type: 'background',
        paint: {
          // The raw EMODnet/GEBCO relief uses warm tan/brown for land - wash the whole map
          // with a translucent ocean-blue tint so it reads as one cohesive blue-toned scheme
          // (rather than beige) while keeping the underlying relief detail visible through it.
          'background-color': '#0f4c66',
          'background-opacity': 0.28,
        },
      },
      ...baseStyle.layers.filter((l) => KEPT_VECTOR_LAYER_IDS.has(l.id)),
    ],
  }
}

interface OccFeature {
  geometry: { coordinates: [number, number] }
  properties: Record<string, unknown>
}

// Consecutive fixes farther apart than this are treated as separate segments rather than
// joined — this avoids drawing straight lines across land between distant detections (e.g.
// coarse acoustic receiver stations around Australia).
const MAX_SEGMENT_KM = 250

function haversineKm(a: [number, number], b: [number, number]): number {
  const toRad = (d: number) => (d * Math.PI) / 180
  const [lon1, lat1] = a
  const [lon2, lat2] = b
  const dLat = toRad(lat2 - lat1)
  const dLon = toRad(lon2 - lon1)
  const h =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2
  return 2 * 6371 * Math.asin(Math.sqrt(h))
}

function decimals(n: number): number {
  const s = String(n)
  const i = s.indexOf('.')
  return i < 0 ? 0 : s.length - i - 1
}

// True for coarse, station-based (acoustic) data — receiver-station coordinates carry only
// ~2 decimals, so connecting them chronologically makes a meaningless "web" that jumps across
// land. We skip tracks for such organisms (dots only). Precise GPS/Argos telemetry (many
// decimals) still gets tracks, even when the animal revisits haul-out sites.
function isCoarse(pts: OccFeature[]): boolean {
  if (pts.length < 10) return false
  const sample = pts.slice(0, 400)
  let coarse = 0
  for (const p of sample) {
    const [lon, lat] = p.geometry.coordinates
    if (decimals(lat) <= 2 || decimals(lon) <= 2) coarse++
  }
  return coarse / sample.length > 0.5
}

// Connect each organism's fixes into chronological LineStrings, coloured by SPECIES and split
// at large gaps. A line is only drawn when we know it's the same individual (organismID) and
// the data is real GPS/Argos telemetry — station/acoustic organisms get dots only.
function buildTracks(features: OccFeature[], speciesColors: Record<string, string>) {
  const byOrganism = new Map<string, OccFeature[]>()
  for (const f of features) {
    const org = f.properties?.organism_id
    if (typeof org !== 'string' || !org) continue
    if (!byOrganism.has(org)) byOrganism.set(org, [])
    byOrganism.get(org)!.push(f)
  }
  const lines: object[] = []
  for (const [org, pts] of byOrganism) {
    if (pts.length < 2 || isCoarse(pts)) continue
    pts.sort((a, b) =>
      String(a.properties.event_date_start).localeCompare(String(b.properties.event_date_start)),
    )
    const sci = String(pts[0].properties.scientific_name ?? '')
    const color = speciesColors[sci] ?? '#9fb2bd'
    let segment: [number, number][] = [pts[0].geometry.coordinates]
    const flush = () => {
      if (segment.length >= 2) {
        lines.push({
          type: 'Feature',
          geometry: { type: 'LineString', coordinates: segment },
          properties: { organism_id: org, track_color: color },
        })
      }
    }
    for (let k = 1; k < pts.length; k++) {
      const prev = pts[k - 1].geometry.coordinates
      const cur = pts[k].geometry.coordinates
      if (haversineKm(prev, cur) > MAX_SEGMENT_KM) {
        flush()
        segment = [cur]
      } else {
        segment.push(cur)
      }
    }
    flush()
  }
  return { type: 'FeatureCollection' as const, features: lines }
}

function addOccurrenceLayers(map: MapLibreMap, onPointClick: (scientificName: string) => void) {
  // Points first (as a translucent density layer), then the tracks ON TOP so an individual's
  // path stays visible over a dense cloud of its own fixes.
  map.addSource('occurrences', {
    type: 'geojson',
    data: { type: 'FeatureCollection', features: [] },
  })
  map.addLayer({
    id: 'occurrence-point',
    type: 'circle',
    source: 'occurrences',
    paint: {
      // Smaller when zoomed out so tracks stay visible; noticeably larger when zoomed in.
      'circle-radius': ['interpolate', ['linear'], ['zoom'], 2, 3, 7, 5.5, 11, 8],
      'circle-color': '#9fb2bd',
      'circle-stroke-color': '#ffffff',
      'circle-stroke-width': 0.5,
      'circle-stroke-opacity': 0.3,
      'circle-opacity': 0.65,
    },
  })

  map.addSource('tracks', { type: 'geojson', data: { type: 'FeatureCollection', features: [] } })
  // A wider casing beneath each track gives it contrast against the map and other tracks;
  // the coloured line on top is per-individual.
  map.addLayer({
    id: 'occurrence-track-casing',
    type: 'line',
    source: 'tracks',
    layout: { 'line-cap': 'round', 'line-join': 'round' },
    paint: {
      'line-color': 'rgba(255,255,255,0.55)',
      'line-width': ['interpolate', ['linear'], ['zoom'], 2, 3, 7, 6],
      'line-opacity': 0.4,
    },
  })
  // A white glow behind the hovered individual's line so you can follow one path among many.
  map.addLayer({
    id: 'occurrence-track-highlight',
    type: 'line',
    source: 'tracks',
    layout: { 'line-cap': 'round', 'line-join': 'round' },
    paint: {
      'line-color': '#ffffff',
      'line-width': ['interpolate', ['linear'], ['zoom'], 2, 6, 7, 12],
      'line-opacity': 0.9,
      'line-blur': 2,
    },
    filter: ['==', ['get', 'organism_id'], '___none___'],
  })
  map.addLayer({
    id: 'occurrence-track',
    type: 'line',
    source: 'tracks',
    layout: { 'line-cap': 'round', 'line-join': 'round' },
    paint: {
      'line-color': ['get', 'track_color'],
      'line-width': ['interpolate', ['linear'], ['zoom'], 2, 2, 7, 4.5],
      'line-opacity': 0.95,
    },
  })

  map.on('mousemove', 'occurrence-track', (e) => {
    const org = e.features?.[0]?.properties?.organism_id
    if (org == null) return
    map.setFilter('occurrence-track-highlight', ['==', ['get', 'organism_id'], String(org)])
    map.getCanvas().style.cursor = 'pointer'
  })
  map.on('mouseleave', 'occurrence-track', () => {
    map.setFilter('occurrence-track-highlight', ['==', ['get', 'organism_id'], '___none___'])
    map.getCanvas().style.cursor = ''
  })

  const hover = new maplibregl.Popup({ closeButton: false, closeOnClick: false, offset: 10 })
  map.on('click', 'occurrence-point', (e) => {
    const p = e.features?.[0]?.properties
    if (p && p.scientific_name) onPointClick(String(p.scientific_name))
  })
  map.on('mouseenter', 'occurrence-point', () => (map.getCanvas().style.cursor = 'pointer'))
  map.on('mousemove', 'occurrence-point', (e) => {
    const p = e.features?.[0]?.properties
    if (!p) return
    const name = p.vernacular_name || p.scientific_name || 'Occurrence'
    hover.setLngLat(e.lngLat).setHTML(`<strong>${name}</strong>`).addTo(map)
  })
  map.on('mouseleave', 'occurrence-point', () => {
    map.getCanvas().style.cursor = ''
    hover.remove()
  })
}

async function loadOccurrences(
  map: MapLibreMap,
  studyId: number | null,
  speciesName: string | null,
  flyTo: boolean,
) {
  const params: string[] = []
  if (studyId) params.push(`study_id=${studyId}`)
  if (speciesName) params.push(`scientific_name=${encodeURIComponent(speciesName)}`)
  const url = `${API_BASE_URL}/occurrences${params.length ? `?${params.join('&')}` : ''}`
  const data = await fetch(url).then((r) => r.json())

  // Stamp a numeric year on each feature so the time slider can filter with a fast
  // map expression instead of re-fetching.
  for (const f of data.features) {
    const d = f.properties?.event_date_start
    f.properties.year = d ? Number(String(d).slice(0, 4)) : null
  }

  const source = map.getSource('occurrences') as maplibregl.GeoJSONSource | undefined
  source?.setData(data)

  if (flyTo && data.features.length > 0) {
    // Compute bounds with a loop — spreading 100k+ coords into Math.min/max overflows the stack.
    let minLon = Infinity
    let minLat = Infinity
    let maxLon = -Infinity
    let maxLat = -Infinity
    for (const f of data.features as OccFeature[]) {
      const [lon, lat] = f.geometry.coordinates
      if (lon < minLon) minLon = lon
      if (lon > maxLon) maxLon = lon
      if (lat < minLat) minLat = lat
      if (lat > maxLat) maxLat = lat
    }
    map.fitBounds(
      [
        [minLon, minLat],
        [maxLon, maxLat],
      ],
      { padding: 80, duration: 500, maxZoom: 8 },
    )
  }

  return data.features as OccFeature[]
}

// Rebuild the track lines from the year-filtered fixes so paths honour the time slider too
// (a LineString has no single year, so the point filter alone can't hide them).
function updateTracks(
  map: MapLibreMap,
  features: OccFeature[],
  range: [number, number] | null,
  speciesColors: Record<string, string>,
) {
  const inRange = range
    ? features.filter((f) => {
        const y = f.properties?.year
        return typeof y === 'number' && y >= range[0] && y <= range[1]
      })
    : features
  const src = map.getSource('tracks') as maplibregl.GeoJSONSource | undefined
  src?.setData(buildTracks(inRange, speciesColors))
}

interface MapViewProps {
  selectedStudyId: number | null
  selectedSpeciesName: string | null
  speciesColors: Record<string, string>
  theme: 'light' | 'dark'
  yearRange: [number, number] | null
  speciesList: SpeciesListItem[]
  onPickSpecies: (scientificName: string) => void
}

function makeSpeciesMarkerEl(color: string, label: string): HTMLDivElement {
  const el = document.createElement('div')
  el.style.cssText = [
    'width:40px',
    'height:40px',
    'border-radius:50%',
    'cursor:pointer',
    `border:3px solid ${color}`,
    'box-shadow:0 1px 8px rgba(0,0,0,0.45)',
    `background:${color}`,
    'background-size:cover',
    'background-position:center',
  ].join(';')
  el.title = label
  return el
}

function applyYearFilter(map: MapLibreMap, range: [number, number] | null) {
  if (!map.getLayer('occurrence-point')) return
  map.setFilter(
    'occurrence-point',
    range ? ['all', ['>=', ['get', 'year'], range[0]], ['<=', ['get', 'year'], range[1]]] : null,
  )
}

// The base map is a fixed raster; in dark mode we deepen the ocean wash and flip the
// undersea-feature label/point colours so the chart reads as "ocean night".
function applyMapTheme(map: MapLibreMap, theme: 'light' | 'dark') {
  const dark = theme === 'dark'
  if (map.getLayer('bathymetry-blue-wash')) {
    map.setPaintProperty('bathymetry-blue-wash', 'background-color', dark ? '#05141d' : '#0f4c66')
    map.setPaintProperty('bathymetry-blue-wash', 'background-opacity', dark ? 0.58 : 0.28)
  }
  if (map.getLayer('bathymetry')) {
    map.setPaintProperty('bathymetry', 'raster-saturation', dark ? -0.45 : -0.3)
    map.setPaintProperty('bathymetry', 'raster-brightness-max', dark ? 0.72 : 1)
  }
  if (map.getLayer('undersea-feature-label')) {
    map.setPaintProperty('undersea-feature-label', 'text-color', dark ? '#bcd6e2' : '#0d3a52')
    map.setPaintProperty(
      'undersea-feature-label',
      'text-halo-color',
      dark ? 'rgba(4,18,26,0.9)' : 'rgba(255,255,255,0.95)',
    )
  }
  if (map.getLayer('undersea-feature-point')) {
    map.setPaintProperty('undersea-feature-point', 'circle-color', dark ? '#7fb2c6' : '#0d3a52')
  }
  if (map.getLayer('occurrence-track-casing')) {
    map.setPaintProperty(
      'occurrence-track-casing',
      'line-color',
      dark ? 'rgba(6,20,28,0.85)' : 'rgba(255,255,255,0.8)',
    )
  }
}

function colorExpression(speciesColors: Record<string, string>): maplibregl.ExpressionSpecification | string {
  const entries = Object.entries(speciesColors)
  if (entries.length === 0) return '#9fb2bd'
  return [
    'match',
    ['get', 'scientific_name'],
    ...entries.flatMap(([name, color]) => [name, color]),
    '#9fb2bd',
  ] as maplibregl.ExpressionSpecification
}

export function MapView({
  selectedStudyId,
  selectedSpeciesName,
  speciesColors,
  theme,
  yearRange,
  speciesList,
  onPickSpecies,
}: MapViewProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<MapLibreMap | null>(null)
  const readyRef = useRef(false)
  const colorsRef = useRef(speciesColors)
  const themeRef = useRef(theme)
  const rangeRef = useRef(yearRange)
  const featuresRef = useRef<OccFeature[]>([])
  const speciesListRef = useRef(speciesList)
  speciesListRef.current = speciesList
  const markersRef = useRef<maplibregl.Marker[]>([])
  const pickSpeciesRef = useRef(onPickSpecies)
  pickSpeciesRef.current = onPickSpecies

  function clearSpeciesMarkers() {
    markersRef.current.forEach((m) => m.remove())
    markersRef.current = []
  }

  // Overview: one image pin per species at its centroid, instead of a cloud of dots.
  function showSpeciesMarkers(map: MapLibreMap) {
    clearSpeciesMarkers()
    for (const s of speciesListRef.current) {
      if (s.centroid_lat == null || s.centroid_lon == null) continue
      const color = colorsRef.current[s.scientific_name] ?? '#9fb2bd'
      const el = makeSpeciesMarkerEl(color, s.common_name ?? s.scientific_name)
      el.addEventListener('click', () => pickSpeciesRef.current(s.scientific_name))
      markersRef.current.push(
        new maplibregl.Marker({ element: el }).setLngLat([s.centroid_lon, s.centroid_lat]).addTo(map),
      )
      fetchSpeciesSummary(s.scientific_name).then((sum) => {
        const photo = speciesPhoto(s.scientific_name, sum?.thumbnailUrl)
        if (photo) el.style.backgroundImage = `url(${photo})`
      })
    }
  }

  function clearOccurrences(map: MapLibreMap) {
    const empty = { type: 'FeatureCollection' as const, features: [] }
    ;(map.getSource('occurrences') as maplibregl.GeoJSONSource | undefined)?.setData(empty)
    ;(map.getSource('tracks') as maplibregl.GeoJSONSource | undefined)?.setData(empty)
    featuresRef.current = []
  }

  function refresh(map: MapLibreMap, studyId: number | null, speciesName: string | null, flyTo: boolean) {
    if (!studyId && !speciesName) {
      clearOccurrences(map)
      showSpeciesMarkers(map)
      return
    }
    clearSpeciesMarkers()
    loadOccurrences(map, studyId, speciesName, flyTo).then((feats) => {
      featuresRef.current = feats
      if (mapRef.current) updateTracks(mapRef.current, feats, rangeRef.current, colorsRef.current)
    })
  }

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return

    let cancelled = false

    buildStyle().then((style) => {
      if (cancelled || !containerRef.current) return

      mapRef.current = new maplibregl.Map({
        container: containerRef.current,
        style,
        center: [0, 0],
        zoom: 1.5,
        // Keep many more tiles cached and don't re-fetch expired ones, so panning/zooming
        // doesn't constantly reload the bathymetry raster.
        maxTileCacheSize: 2000,
        refreshExpiredTiles: false,
      })

      mapRef.current.addControl(new maplibregl.NavigationControl(), 'top-right')

      mapRef.current.on('load', () => {
        fetchAllUnderseaFeatureNames().then((data) => {
          if (cancelled || !mapRef.current) return

          mapRef.current.addSource('undersea-features', { type: 'geojson', data })

          mapRef.current.addLayer({
            id: 'undersea-feature-point',
            type: 'circle',
            source: 'undersea-features',
            minzoom: 4,
            paint: {
              'circle-radius': 1.6,
              'circle-color': '#0d3a52',
              // Fade the markers in gradually rather than popping in at low zoom.
              'circle-opacity': ['interpolate', ['linear'], ['zoom'], 4, 0, 6, 0.5],
            },
          })

          mapRef.current.addLayer({
            id: 'undersea-feature-label',
            type: 'symbol',
            source: 'undersea-features',
            minzoom: 5,
            layout: {
              'text-field': ['concat', ['get', 'NAME'], ' ', ['get', 'TYPE']],
              'text-font': ['Noto Sans Italic'],
              'text-size': 10.5,
              'text-variable-anchor': ['top'],
              'text-radial-offset': 0.4,
            },
            paint: {
              'text-color': '#0d3a52',
              'text-halo-color': 'rgba(255,255,255,0.9)',
              'text-halo-width': 1.2,
              'text-opacity': ['interpolate', ['linear'], ['zoom'], 5, 0, 6.5, 0.7],
            },
          })

          applyMapTheme(mapRef.current as MapLibreMap, themeRef.current)
        })

        addOccurrenceLayers(mapRef.current as MapLibreMap, (name) => pickSpeciesRef.current(name))
        mapRef.current.setPaintProperty('occurrence-point', 'circle-color', colorExpression(colorsRef.current))
        applyMapTheme(mapRef.current as MapLibreMap, themeRef.current)
        applyYearFilter(mapRef.current as MapLibreMap, rangeRef.current)
        readyRef.current = true
        refresh(mapRef.current as MapLibreMap, selectedStudyId, selectedSpeciesName, false)
      })
    })

    return () => {
      cancelled = true
      mapRef.current?.remove()
      mapRef.current = null
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    if (!readyRef.current || !mapRef.current) return
    refresh(mapRef.current, selectedStudyId, selectedSpeciesName, true)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedStudyId, selectedSpeciesName])

  // When the species list loads (or changes), refresh the overview pins if we're in overview.
  useEffect(() => {
    if (!readyRef.current || !mapRef.current) return
    if (!selectedStudyId && !selectedSpeciesName) showSpeciesMarkers(mapRef.current)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [speciesList])

  useEffect(() => {
    colorsRef.current = speciesColors
    const map = mapRef.current
    if (!readyRef.current || !map || !map.getLayer('occurrence-point')) return
    map.setPaintProperty('occurrence-point', 'circle-color', colorExpression(speciesColors))
    // Recolour tracks too (they were built with a fallback colour if colours loaded late).
    updateTracks(map, featuresRef.current, rangeRef.current, speciesColors)
  }, [speciesColors])

  useEffect(() => {
    themeRef.current = theme
    if (readyRef.current && mapRef.current) applyMapTheme(mapRef.current, theme)
  }, [theme])

  useEffect(() => {
    rangeRef.current = yearRange
    if (readyRef.current && mapRef.current) {
      applyYearFilter(mapRef.current, yearRange)
      updateTracks(mapRef.current, featuresRef.current, yearRange, colorsRef.current)
    }
  }, [yearRange])

  return <div ref={containerRef} style={{ position: 'absolute', inset: 0 }} />
}
