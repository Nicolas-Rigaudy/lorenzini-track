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

/** Stable, distinct species→colour map. Colours are generated from the sorted scientific name
 * index using the golden-angle hue rotation, so every species gets a visually distinct hue
 * (even for 20+ species) and — crucially — the same species always keeps the same colour,
 * regardless of how many species are loaded or filtered. Used everywhere (map dots, legend,
 * gallery accents, profile) so accents always match the dots. */
export function buildSpeciesColors(names: string[]): Record<string, string> {
  const uniq = [...new Set(names)].sort()
  const map: Record<string, string> = {}
  uniq.forEach((name, i) => {
    const hue = Math.round((i * 137.508) % 360)
    map[name] = `hsl(${hue}, 68%, 52%)`
  })
  return map
}

export function speciesColor(colors: Record<string, string>, name: string | null | undefined): string {
  return (name && colors[name]) || FALLBACK
}
