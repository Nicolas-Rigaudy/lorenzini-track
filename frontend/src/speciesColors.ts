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

// Sharks lead the app, so they get a wider blue→cyan range instead of one hue band. Each
// entry is at least 3:1 against both the light (#fff) and dark (#10222e) panel surfaces,
// and the order puts very different colours next to each other: species are assigned in
// legend order, so neighbouring sharks in the legend never get similar blues.
const SHARK_RAMP = [
  '#12757e', // deep cyan
  '#1ea3af', // cyan
  '#1270a4', // steel blue
  '#307cf9', // bright blue
  '#188aa0', // teal blue
  '#6a90fa', // periwinkle
  '#1069cc', // royal blue
  '#1d9ddd', // sky
  '#1f5af8', // ultramarine
  '#1782c8', // azure
]

export interface SpeciesColorInput {
  scientific_name: string
  common_name?: string | null
  taxon_group?: string
}

/** Legend order (by display name). Shark colours follow it, so keep both in step. */
export function byLegendName(a: SpeciesColorInput, b: SpeciesColorInput): number {
  return (a.common_name ?? a.scientific_name).localeCompare(b.common_name ?? b.scientific_name)
}

/** Stable species→colour map, coloured by taxon family (shades within a family; sharks use
 * the wider blue→cyan ramp). The same species always keeps the same colour regardless of
 * filtering, and every accent (dots, tracks, legend, gallery, profile) uses this one map. */
export function buildSpeciesColors(species: SpeciesColorInput[]): Record<string, string> {
  const groups = new Map<string, string[]>()
  for (const s of species) {
    const g = s.taxon_group || 'other'
    if (!groups.has(g)) groups.set(g, [])
    groups.get(g)!.push(s.scientific_name)
  }
  const map: Record<string, string> = {}
  const sharks = species.filter((s) => s.taxon_group === 'shark').sort(byLegendName)
  if (sharks.length <= SHARK_RAMP.length) {
    sharks.forEach((s, i) => (map[s.scientific_name] = SHARK_RAMP[i]))
    groups.delete('shark')
  }
  for (const [group, names] of groups) {
    const base = GROUP_HUE[group] ?? GROUP_HUE.other
    const sorted = [...new Set(names)].sort()
    const n = sorted.length
    sorted.forEach((name, i) => {
      // Keep the hue in a narrow band so a family stays visually itself (turtles stay green, not
      // teal or yellow) and tell members apart mainly by lightness. Lightness is interleaved
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
