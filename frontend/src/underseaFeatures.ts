import { UNDERSEA_FEATURE_NAMES_URL } from './config'

interface FeatureCollection {
  type: 'FeatureCollection'
  features: object[]
}

const PAGE_SIZE = 2000

async function fetchPage(offset: number): Promise<FeatureCollection> {
  const params = new URLSearchParams({
    where: '1=1',
    outFields: 'NAME,TYPE',
    resultOffset: String(offset),
    resultRecordCount: String(PAGE_SIZE),
    f: 'geojson',
  })
  const response = await fetch(`${UNDERSEA_FEATURE_NAMES_URL}?${params}`)
  return response.json()
}

export async function fetchAllUnderseaFeatureNames(): Promise<FeatureCollection> {
  const features = []
  let offset = 0

  while (true) {
    const page = await fetchPage(offset)
    features.push(...page.features)
    if (page.features.length < PAGE_SIZE) break
    offset += PAGE_SIZE
  }

  return { type: 'FeatureCollection', features }
}
