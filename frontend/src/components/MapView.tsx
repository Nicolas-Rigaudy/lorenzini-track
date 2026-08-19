import { useEffect, useRef } from 'react'
import maplibregl, { type Map as MapLibreMap, type StyleSpecification } from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { API_BASE_URL, BATHYMETRY_TILE_URL, MAP_STYLE_URL } from '../config'
import { fetchAllUnderseaFeatureNames } from '../underseaFeatures'

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

// A distinct per-individual palette (not the species palette) so two animals of the same
// species are visually separable. Bright, high-contrast, no orange.
const TRACK_COLORS = [
  '#ffd166',
  '#06d6a0',
  '#ef476f',
  '#4cc9f0',
  '#b892ff',
  '#c5f06d',
  '#f15bb5',
  '#5e8bff',
]

// Connect each organism's fixes into a chronological LineString, coloured per individual.
// Only organisms with 2+ fixes produce a track (so aggregated single-cell datasets stay
// as plain points).
function buildTracks(features: OccFeature[]) {
  const byOrganism = new Map<string, OccFeature[]>()
  for (const f of features) {
    const org = f.properties?.organism_id
    if (typeof org !== 'string' || !org) continue
    if (!byOrganism.has(org)) byOrganism.set(org, [])
    byOrganism.get(org)!.push(f)
  }
  const orgs = [...byOrganism.keys()].sort()
  const lines = orgs.flatMap((org, i) => {
    const pts = byOrganism.get(org)!
    if (pts.length < 2) return []
    pts.sort((a, b) =>
      String(a.properties.event_date_start).localeCompare(String(b.properties.event_date_start)),
    )
    return [
      {
        type: 'Feature' as const,
        geometry: {
          type: 'LineString' as const,
          coordinates: pts.map((p) => p.geometry.coordinates),
        },
        properties: { organism_id: org, track_color: TRACK_COLORS[i % TRACK_COLORS.length] },
      },
    ]
  })
  return { type: 'FeatureCollection' as const, features: lines }
}

function addOccurrenceLayers(map: MapLibreMap, onPointClick: (studyId: number) => void) {
  map.addSource('tracks', { type: 'geojson', data: { type: 'FeatureCollection', features: [] } })
  // A wider casing beneath each track gives it contrast against the map and against other
  // crossing tracks; the coloured line on top is per-individual.
  map.addLayer({
    id: 'occurrence-track-casing',
    type: 'line',
    source: 'tracks',
    layout: { 'line-cap': 'round', 'line-join': 'round' },
    paint: {
      'line-color': 'rgba(255,255,255,0.75)',
      'line-width': ['interpolate', ['linear'], ['zoom'], 2, 4, 7, 8],
      'line-opacity': 0.7,
    },
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

  map.addSource('occurrences', {
    type: 'geojson',
    data: { type: 'FeatureCollection', features: [] },
  })
  map.addLayer({
    id: 'occurrence-point',
    type: 'circle',
    source: 'occurrences',
    paint: {
      // Smaller when zoomed out so the underlying tracks stay visible; larger up close.
      'circle-radius': ['interpolate', ['linear'], ['zoom'], 2, 3, 7, 5.5],
      'circle-color': '#9fb2bd',
      'circle-stroke-color': '#ffffff',
      'circle-stroke-width': 1,
      'circle-opacity': 0.9,
    },
  })

  map.on('click', 'occurrence-point', (e) => {
    const p = e.features?.[0]?.properties
    if (p && p.study_id != null) onPointClick(Number(p.study_id))
  })
  map.on('mouseenter', 'occurrence-point', () => (map.getCanvas().style.cursor = 'pointer'))
  map.on('mouseleave', 'occurrence-point', () => (map.getCanvas().style.cursor = ''))
}

async function loadOccurrences(
  map: MapLibreMap,
  studyId: number | null,
  speciesName: string | null,
  flyTo: boolean,
) {
  let url = `${API_BASE_URL}/occurrences`
  if (studyId) {
    url += `?study_id=${studyId}`
  } else if (speciesName) {
    url += `?scientific_name=${encodeURIComponent(speciesName)}`
  }
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
    const lons = data.features.map((f: { geometry: { coordinates: number[] } }) => f.geometry.coordinates[0])
    const lats = data.features.map((f: { geometry: { coordinates: number[] } }) => f.geometry.coordinates[1])
    map.fitBounds(
      [
        [Math.min(...lons), Math.min(...lats)],
        [Math.max(...lons), Math.max(...lats)],
      ],
      { padding: 80, duration: 1000, maxZoom: 8 },
    )
  }

  return data.features as OccFeature[]
}

// Rebuild the track lines from the year-filtered fixes so paths honour the time slider too
// (a LineString has no single year, so the point filter alone can't hide them).
function updateTracks(map: MapLibreMap, features: OccFeature[], range: [number, number] | null) {
  const inRange = range
    ? features.filter((f) => {
        const y = f.properties?.year
        return typeof y === 'number' && y >= range[0] && y <= range[1]
      })
    : features
  const src = map.getSource('tracks') as maplibregl.GeoJSONSource | undefined
  src?.setData(buildTracks(inRange))
}

interface MapViewProps {
  selectedStudyId: number | null
  selectedSpeciesName: string | null
  speciesColors: Record<string, string>
  theme: 'light' | 'dark'
  yearRange: [number, number] | null
  onSelectStudy: (studyId: number) => void
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
  onSelectStudy,
}: MapViewProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<MapLibreMap | null>(null)
  const readyRef = useRef(false)
  const colorsRef = useRef(speciesColors)
  const themeRef = useRef(theme)
  const rangeRef = useRef(yearRange)
  const featuresRef = useRef<OccFeature[]>([])
  const selectStudyRef = useRef(onSelectStudy)
  selectStudyRef.current = onSelectStudy

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
            minzoom: 3,
            paint: {
              'circle-radius': 2.5,
              'circle-color': '#0d3a52',
            },
          })

          mapRef.current.addLayer({
            id: 'undersea-feature-label',
            type: 'symbol',
            source: 'undersea-features',
            minzoom: 3,
            layout: {
              'text-field': ['concat', ['get', 'NAME'], ' ', ['get', 'TYPE']],
              'text-font': ['Noto Sans Italic'],
              'text-size': 12,
              'text-variable-anchor': ['top'],
              'text-radial-offset': 0.4,
            },
            paint: {
              'text-color': '#0d3a52',
              'text-halo-color': 'rgba(255,255,255,0.95)',
              'text-halo-width': 1.8,
            },
          })

          applyMapTheme(mapRef.current as MapLibreMap, themeRef.current)
        })

        addOccurrenceLayers(mapRef.current as MapLibreMap, (id) => selectStudyRef.current(id))
        mapRef.current.setPaintProperty('occurrence-point', 'circle-color', colorExpression(colorsRef.current))
        applyMapTheme(mapRef.current as MapLibreMap, themeRef.current)
        applyYearFilter(mapRef.current as MapLibreMap, rangeRef.current)
        readyRef.current = true
        loadOccurrences(mapRef.current as MapLibreMap, selectedStudyId, selectedSpeciesName, false).then(
          (feats) => {
            featuresRef.current = feats
            if (mapRef.current) updateTracks(mapRef.current, feats, rangeRef.current)
          },
        )
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
    loadOccurrences(mapRef.current, selectedStudyId, selectedSpeciesName, true).then((feats) => {
      featuresRef.current = feats
      if (mapRef.current) updateTracks(mapRef.current, feats, rangeRef.current)
    })
  }, [selectedStudyId, selectedSpeciesName])

  useEffect(() => {
    colorsRef.current = speciesColors
    const map = mapRef.current
    if (!readyRef.current || !map || !map.getLayer('occurrence-point')) return
    map.setPaintProperty('occurrence-point', 'circle-color', colorExpression(speciesColors))
  }, [speciesColors])

  useEffect(() => {
    themeRef.current = theme
    if (readyRef.current && mapRef.current) applyMapTheme(mapRef.current, theme)
  }, [theme])

  useEffect(() => {
    rangeRef.current = yearRange
    if (readyRef.current && mapRef.current) {
      applyYearFilter(mapRef.current, yearRange)
      updateTracks(mapRef.current, featuresRef.current, yearRange)
    }
  }, [yearRange])

  return <div ref={containerRef} style={{ position: 'absolute', inset: 0 }} />
}
