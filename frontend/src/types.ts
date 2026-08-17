export interface Study {
  id: number
  title: string
  abstract: string | null
  data_provider: string | null
  source_url: string | null
  license: string | null
  rights_holder: string | null
  published_date: string | null
  record_count: number
  date_range: { start: string | null; end: string | null }
  species: string[]
}

export function formatDate(iso: string | null): string {
  if (!iso) return '?'
  return iso.slice(0, 10)
}
