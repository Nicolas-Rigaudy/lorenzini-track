// Categorical palette for distinguishing species on the map. Chosen to read clearly against
// the blue bathymetry and to sit with the teal/deep-ocean UI — deliberately no orange.
export const SPECIES_PALETTE = [
  '#2ec4b6', // teal
  '#f4d35e', // gold
  '#9b5de5', // violet
  '#48cae4', // sky
  '#c5d86d', // lime
  '#f15bb5', // magenta
  '#ff8fa3', // salmon
  '#5e60ce', // indigo
  '#43aa8b', // sea green
  '#d1495b', // crimson
  '#118ab2', // blue
  '#b5838d', // mauve
  '#06d6a0', // mint
  '#8338ec', // purple
]

const FALLBACK = '#9fb2bd'

// Each taxon family gets a base hue; species within a family are shades of it. This is far
// more cohesive than a rainbow — related animals read as related — while staying distinct.
const GROUP_HUE: Record<string, number> = {
  shark: 215, // blue
  ray: 175, // teal
  turtle: 130, // green
  pinniped: 35, // warm sand
  seabird: 280, // violet
  sirenian: 325, // magenta
  other: 250,
}

export interface SpeciesColorInput {
  scientific_name: string
  taxon_group?: string
}

/** Stable species→colour map, coloured by taxon family (shades within a family). The same
 * species always keeps the same colour regardless of filtering, and every accent (dots,
 * tracks, legend, gallery, profile) uses this one map. */
export function buildSpeciesColors(species: SpeciesColorInput[]): Record<string, string> {
  const groups = new Map<string, string[]>()
  for (const s of species) {
    const g = s.taxon_group || 'other'
    if (!groups.has(g)) groups.set(g, [])
    groups.get(g)!.push(s.scientific_name)
  }
  const map: Record<string, string> = {}
  for (const [group, names] of groups) {
    const base = GROUP_HUE[group] ?? GROUP_HUE.other
    const sorted = [...new Set(names)].sort()
    const n = sorted.length
    sorted.forEach((name, i) => {
      // Keep the hue in a narrow band so a family stays visually itself (sharks stay blue, not
      // green or purple) and tell members apart mainly by lightness. Lightness is interleaved
      // (dark, light, dark, ...) so alphabetical neighbours never get near-identical shades.
      const spread = n === 1 ? 0 : (i / (n - 1) - 0.5) * Math.min(44, 6 * (n - 1))
      const hue = Math.round((base + spread + 360) % 360)
      const half = Math.ceil(n / 2)
      const rank = i % 2 === 0 ? i / 2 : half + (i - 1) / 2
      const light = n === 1 ? 55 : Math.round(38 + (rank / (n - 1)) * 34) // 38%..72%
      map[name] = `hsl(${hue}, 52%, ${light}%)`
    })
  }
  return map
}

export function speciesColor(colors: Record<string, string>, name: string | null | undefined): string {
  return (name && colors[name]) || FALLBACK
}
