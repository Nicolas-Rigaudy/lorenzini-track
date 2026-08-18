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

function addOccurrenceLayer(map: MapLibreMap) {
  map.addSource('occurrences', {
    type: 'geojson',
    data: { type: 'FeatureCollection', features: [] },
  })

  map.addLayer({
    id: 'occurrence-point',
    type: 'circle',
    source: 'occurrences',
    paint: {
      'circle-radius': 5,
      'circle-color': '#9fb2bd',
      'circle-stroke-color': '#ffffff',
      'circle-stroke-width': 1,
    },
  })

  map.on('click', 'occurrence-point', (e) => {
    const feature = e.features?.[0]
    if (!feature) return
    const p = feature.properties as Record<string, unknown>

    const uncM = Number(p.coordinate_uncertainty_in_meters)
    const uncertainty =
      Number.isFinite(uncM) && uncM > 0
        ? `<br/>Position uncertainty: ~${uncM >= 1000 ? `${Math.round(uncM / 1000)} km` : `${Math.round(uncM)} m`}`
        : ''

    new maplibregl.Popup()
      .setLngLat(e.lngLat)
      .setHTML(
        `<strong>${p.vernacular_name ?? p.scientific_name}</strong><br/>` +
          `<em>${p.scientific_name}</em><br/>` +
          `${p.event_date_start ?? ''} &ndash; ${p.event_date_end ?? ''}` +
          uncertainty,
      )
      .addTo(map)
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
}

interface MapViewProps {
  selectedStudyId: number | null
  selectedSpeciesName: string | null
  speciesColors: Record<string, string>
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

export function MapView({ selectedStudyId, selectedSpeciesName, speciesColors }: MapViewProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<MapLibreMap | null>(null)
  const readyRef = useRef(false)
  const colorsRef = useRef(speciesColors)

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
        })

        addOccurrenceLayer(mapRef.current as MapLibreMap)
        mapRef.current.setPaintProperty('occurrence-point', 'circle-color', colorExpression(colorsRef.current))
        readyRef.current = true
        loadOccurrences(mapRef.current as MapLibreMap, selectedStudyId, selectedSpeciesName, false)
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
    loadOccurrences(mapRef.current, selectedStudyId, selectedSpeciesName, true)
  }, [selectedStudyId, selectedSpeciesName])

  useEffect(() => {
    colorsRef.current = speciesColors
    const map = mapRef.current
    if (!readyRef.current || !map || !map.getLayer('occurrence-point')) return
    map.setPaintProperty('occurrence-point', 'circle-color', colorExpression(speciesColors))
  }, [speciesColors])

  return <div ref={containerRef} style={{ position: 'absolute', inset: 0 }} />
}
