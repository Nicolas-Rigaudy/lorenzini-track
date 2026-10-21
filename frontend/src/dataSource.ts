import { API_BASE_URL, STATIC_DATA_URL, STATIC_MODE } from './config'
import type { Study } from './types'

// One place that knows whether data comes from the API or from the files the export
// command writes (backend/app/export). Callers get the same shapes either way.

interface OccurrenceCollection {
  type: 'FeatureCollection'
  total: number
  features: { properties: Record<string, unknown> }[]
}

const getJson = <T>(url: string): Promise<T> =>
  fetch(url).then((r) => {
    if (!r.ok) throw new Error(`${url}: ${r.status}`)
    return r.json()
  })

export const speciesSlug = (name: string) => name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')

let studiesRequest: Promise<Study[]> | null = null

export function fetchStudies(): Promise<Study[]> {
  studiesRequest ??= getJson<Study[]>(STATIC_MODE ? `${STATIC_DATA_URL}/studies.json` : `${API_BASE_URL}/studies`)
  return studiesRequest
}

export const speciesListUrl = () => (STATIC_MODE ? `${STATIC_DATA_URL}/species.json` : `${API_BASE_URL}/species`)

export const speciesDetailUrl = (name: string) =>
  STATIC_MODE
    ? `${STATIC_DATA_URL}/species/${speciesSlug(name)}.json`
    : `${API_BASE_URL}/species/${encodeURIComponent(name)}`

export async function fetchOccurrences(
  studyId: number | null,
  speciesName: string | null,
): Promise<OccurrenceCollection> {
  if (!STATIC_MODE) {
    const params: string[] = []
    if (studyId) params.push(`study_id=${studyId}`)
    if (speciesName) params.push(`scientific_name=${encodeURIComponent(speciesName)}`)
    return getJson(`${API_BASE_URL}/occurrences${params.length ? `?${params.join('&')}` : ''}`)
  }

  // The export writes one file per study; a species is the union of its studies' files.
  const studyIds = studyId
    ? [studyId]
    : (await fetchStudies()).filter((s) => speciesName && s.species.includes(speciesName)).map((s) => s.id)
  const files = await Promise.all(
    studyIds.map((id) => getJson<OccurrenceCollection>(`${STATIC_DATA_URL}/occurrences/study-${id}.geojson`)),
  )
  const features = files
    .flatMap((f) => f.features)
    .filter((f) => !speciesName || f.properties.scientific_name === speciesName)
  return { type: 'FeatureCollection', total: features.length, features }
}
