const STATUS_COLORS: Record<string, string> = {
  'least concern': '#4b8f3a',
  'near threatened': '#8ea23a',
  vulnerable: '#e0a52c',
  endangered: '#e0632c',
  'critically endangered': '#c62828',
  'extinct in the wild': '#5b2b6b',
  extinct: '#1a1a1a',
  'data deficient': '#7a8896',
}

export function statusColor(status: string): string {
  return STATUS_COLORS[status.toLowerCase()] ?? 'var(--color-ink-faint)'
}

export interface SpeciesSummary {
  title: string
  description: string | null
  extract: string | null
  thumbnailUrl: string | null
  pageUrl: string | null
  wikidataId: string | null
  conservationStatus: string | null
}

const cache = new Map<string, SpeciesSummary | null>()

// Wikidata property P141 = "IUCN conservation status". Its value is itself a Wikidata item
// (e.g. "endangered"), so resolving it takes a second lookup.
async function fetchConservationStatus(wikidataId: string): Promise<string | null> {
  const entity = await fetch(`https://www.wikidata.org/wiki/Special:EntityData/${wikidataId}.json`)
    .then((r) => (r.ok ? r.json() : null))
    .catch(() => null)

  const statusClaim = entity?.entities?.[wikidataId]?.claims?.P141?.[0]?.mainsnak?.datavalue?.value
  const statusId = statusClaim?.id
  if (!statusId) return null

  const statusEntity = await fetch(`https://www.wikidata.org/wiki/Special:EntityData/${statusId}.json`)
    .then((r) => (r.ok ? r.json() : null))
    .catch(() => null)

  return statusEntity?.entities?.[statusId]?.labels?.en?.value ?? null
}

export async function fetchSpeciesSummary(scientificName: string): Promise<SpeciesSummary | null> {
  if (cache.has(scientificName)) return cache.get(scientificName) ?? null

  const title = scientificName.trim().replace(/\s+/g, '_')
  const response = await fetch(
    `https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(title)}`,
  )

  if (!response.ok) {
    cache.set(scientificName, null)
    return null
  }

  const data = await response.json()
  const wikidataId = data.wikibase_item ?? null

  const summary: SpeciesSummary = {
    title: data.title,
    description: data.description ?? null,
    extract: data.extract ?? null,
    thumbnailUrl: data.thumbnail?.source ?? null,
    pageUrl: data.content_urls?.desktop?.page ?? null,
    wikidataId,
    conservationStatus: wikidataId ? await fetchConservationStatus(wikidataId) : null,
  }

  cache.set(scientificName, summary)
  return summary
}
