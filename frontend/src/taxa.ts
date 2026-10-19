import type { SpeciesListItem } from './speciesApi'
import type { Study } from './types'

// Sharks lead (decision 0008): the app opens on them, and the other taxon families stay one
// filter away. Group keys come from the API's `taxon_group`.
export const DEFAULT_TAXON_GROUP = 'shark'
export const ALL_TAXA = 'all'

const GROUP_ORDER = ['shark', 'ray', 'turtle', 'pinniped', 'sirenian', 'seabird', 'other']

const GROUP_LABEL: Record<string, string> = {
  shark: 'Sharks',
  ray: 'Rays',
  turtle: 'Turtles',
  pinniped: 'Seals',
  sirenian: 'Manatees',
  seabird: 'Seabirds',
  other: 'Other',
}

export interface TaxonOption {
  key: string
  label: string
  count: number
}

/** Filter options for the families present in the data, sharks first, then "All". */
export function taxonOptions(species: SpeciesListItem[]): TaxonOption[] {
  const counts = new Map<string, number>()
  for (const s of species) counts.set(s.taxon_group, (counts.get(s.taxon_group) ?? 0) + 1)
  const rank = (g: string) => (GROUP_ORDER.includes(g) ? GROUP_ORDER.indexOf(g) : GROUP_ORDER.length)
  const groups = [...counts.keys()].sort((a, b) => rank(a) - rank(b) || a.localeCompare(b))
  return [
    ...groups.map((g) => ({ key: g, label: GROUP_LABEL[g] ?? g, count: counts.get(g)! })),
    { key: ALL_TAXA, label: 'All', count: species.length },
  ]
}

export function speciesInGroup(species: SpeciesListItem[], group: string): SpeciesListItem[] {
  return group === ALL_TAXA ? species : species.filter((s) => s.taxon_group === group)
}

/** Studies that track at least one species of the group. */
export function studiesInGroup(studies: Study[], species: SpeciesListItem[], group: string): Study[] {
  if (group === ALL_TAXA) return studies
  const names = new Set(speciesInGroup(species, group).map((s) => s.scientific_name))
  return studies.filter((study) => study.species.some((name) => names.has(name)))
}
