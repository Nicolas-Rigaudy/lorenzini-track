export interface SpeciesSummary {
  title: string
  description: string | null
  extract: string | null
  thumbnailUrl: string | null
  pageUrl: string | null
}

const cache = new Map<string, SpeciesSummary | null>()

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
  const summary: SpeciesSummary = {
    title: data.title,
    description: data.description ?? null,
    extract: data.extract ?? null,
    thumbnailUrl: data.thumbnail?.source ?? null,
    pageUrl: data.content_urls?.desktop?.page ?? null,
  }

  cache.set(scientificName, summary)
  return summary
}
