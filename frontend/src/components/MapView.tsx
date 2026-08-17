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
      { id: 'bathymetry', type: 'raster', source: 'bathymetry' },
      ...baseStyle.layers.filter((l) => KEPT_VECTOR_LAYER_IDS.has(l.id)),
    ],
  }
}

export function MapView() {
  const containerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<MapLibreMap | null>(null)

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
              'circle-radius': 2,
              'circle-color': '#2b6e8f',
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
              'text-size': 11,
              'text-variable-anchor': ['top'],
              'text-radial-offset': 0.4,
            },
            paint: {
              'text-color': '#2b6e8f',
              'text-halo-color': 'rgba(255,255,255,0.85)',
              'text-halo-width': 1,
            },
          })
        })

        fetch(`${API_BASE_URL}/occurrences`)
          .then((r) => r.json())
          .then((data) => {
            if (cancelled || !mapRef.current) return

            mapRef.current.addSource('occurrences', { type: 'geojson', data })

            mapRef.current.addLayer({
              id: 'occurrence-point',
              type: 'circle',
              source: 'occurrences',
              paint: {
                'circle-radius': 5,
                'circle-color': '#e8702a',
                'circle-stroke-color': '#ffffff',
                'circle-stroke-width': 1,
              },
            })

            mapRef.current.on('click', 'occurrence-point', (e) => {
              const feature = e.features?.[0]
              if (!feature) return
              const p = feature.properties as Record<string, unknown>

              new maplibregl.Popup()
                .setLngLat(e.lngLat)
                .setHTML(
                  `<strong>${p.vernacular_name ?? p.scientific_name}</strong><br/>` +
                    `<em>${p.scientific_name}</em><br/>` +
                    `${p.event_date_start ?? ''} &ndash; ${p.event_date_end ?? ''}<br/>` +
                    `Position uncertainty: ~${Math.round(Number(p.coordinate_uncertainty_in_meters) / 1000)} km` +
                    ` (aggregated per 1° grid cell)`,
                )
                .addTo(mapRef.current as MapLibreMap)
            })

            mapRef.current.on(
              'mouseenter',
              'occurrence-point',
              () => (mapRef.current!.getCanvas().style.cursor = 'pointer'),
            )
            mapRef.current.on(
              'mouseleave',
              'occurrence-point',
              () => (mapRef.current!.getCanvas().style.cursor = ''),
            )
          })
      })
    })

    return () => {
      cancelled = true
      mapRef.current?.remove()
      mapRef.current = null
    }
  }, [])

  return <div ref={containerRef} style={{ position: 'absolute', inset: 0 }} />
}
