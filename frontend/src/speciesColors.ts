// Categorical palette for distinguishing species on the map. Chosen to read clearly against
// the blue bathymetry and to sit with the teal/deep-ocean UI — deliberately no orange.
export const SPECIES_PALETTE = [
  '#2ec4b6', // teal
  '#f2c14e', // gold
  '#9b5de5', // violet
  '#48cae4', // sky
  '#c5d86d', // lime
  '#f15bb5', // magenta
  '#ff8fa3', // salmon
  '#5e60ce', // indigo
]

const FALLBACK = '#9fb2bd'

/** Stable species→colour map: colours are assigned by sorted scientific name so a species
 * keeps the same colour regardless of fetch order. */
export function buildSpeciesColors(names: string[]): Record<string, string> {
  const map: Record<string, string> = {}
  ;[...new Set(names)]
    .sort()
    .forEach((name, i) => {
      map[name] = SPECIES_PALETTE[i % SPECIES_PALETTE.length]
    })
  return map
}

export function speciesColor(colors: Record<string, string>, name: string | null | undefined): string {
  return (name && colors[name]) || FALLBACK
}
