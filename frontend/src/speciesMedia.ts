// Curated per-species imagery (verified Wikimedia URLs):
//   photo        — a real photograph, used for the hero, gallery card and map pin, overriding
//                  Wikipedia's default lead image where that is a diagram/illustration.
//   sizeDiagram  — a real size-comparison diagram (animal vs human/diver to scale). When set,
//                  the profile shows it instead of the fallback bar chart.
// Populated from sourced data; species without an entry fall back to the Wikipedia thumbnail
// (photo) and the bar chart (size).

export interface SpeciesMedia {
  photo?: string
  sizeDiagram?: string
}

export const SPECIES_MEDIA: Record<string, SpeciesMedia> = {}

export function speciesPhoto(name: string, fallback?: string | null): string | null {
  return SPECIES_MEDIA[name]?.photo ?? fallback ?? null
}

export function speciesSizeDiagram(name: string): string | null {
  return SPECIES_MEDIA[name]?.sizeDiagram ?? null
}
