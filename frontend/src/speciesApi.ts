import { API_BASE_URL } from './config'

export interface SpeciesFacts {
  common_name: string | null
  taxon_class: string | null
  taxon_order: string | null
  taxon_family: string | null
  body_plan: 'shark' | 'ray' | null
  max_length_m: number | null
  typical_length_m: number | null
  max_weight_kg: number | null
  lifespan_years: number | null
  depth_min_m: number | null
  depth_max_m: number | null
  temp_min_c: number | null
  temp_max_c: number | null
  diet: string | null
  feeding: string | null
  distribution: string | null
  habitat: string | null
}

export interface SpeciesListItem {
  scientific_name: string
  vernacular_name: string | null
  common_name: string | null
  body_plan: 'shark' | 'ray' | null
  taxon_group: string
  record_count: number
  study_count: number
  date_range: { start: string | null; end: string | null }
  centroid_lat: number | null
  centroid_lon: number | null
}

export interface YearCount {
  year: number
  count: number
}

export interface SpeciesDetail extends SpeciesListItem {
  facts: SpeciesFacts | null
  monthly_histogram: number[]
  yearly_histogram: YearCount[]
  tag_count: number
  study_ids: number[]
}

export async function fetchSpeciesList(): Promise<SpeciesListItem[]> {
  return fetch(`${API_BASE_URL}/species`).then((r) => r.json())
}

export async function fetchSpeciesDetail(scientificName: string): Promise<SpeciesDetail> {
  return fetch(`${API_BASE_URL}/species/${encodeURIComponent(scientificName)}`).then((r) =>
    r.json(),
  )
}
