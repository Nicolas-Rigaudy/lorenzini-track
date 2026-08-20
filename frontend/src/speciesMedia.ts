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

const U = 'https://upload.wikimedia.org/wikipedia/commons/thumb'

export const SPECIES_MEDIA: Record<string, SpeciesMedia> = {
  // Real size-comparison diagrams (silhouette vs human/diver) sourced from Wikimedia Commons.
  // Only a few species have one; the rest fall back to the to-scale bar chart.
  'Rhincodon typus': {
    sizeDiagram: `${U}/3/33/Whale-Shark-Scale-Chart-SVG-Steveoc86.svg/500px-Whale-Shark-Scale-Chart-SVG-Steveoc86.svg.png`,
  },
  'Cetorhinus maximus': {
    sizeDiagram: `${U}/2/20/Basking-Shark-Scale-Chart-SVG-Steveoc86-001.svg/500px-Basking-Shark-Scale-Chart-SVG-Steveoc86-001.svg.png`,
  },
  'Carcharhinus leucas': {
    // Wikipedia's lead image is the size diagram, so override the hero with a real photo.
    photo: `${U}/3/3b/Requin_bouledogue_%28Carcharhinus_leucas%29_%28Ifremer_00813-92510_-_53590%29.jpg/500px-Requin_bouledogue_%28Carcharhinus_leucas%29_%28Ifremer_00813-92510_-_53590%29.jpg`,
    sizeDiagram: `${U}/a/a1/Bull_shark_size.svg/500px-Bull_shark_size.svg.png`,
  },
}

export function speciesPhoto(name: string, fallback?: string | null): string | null {
  return SPECIES_MEDIA[name]?.photo ?? fallback ?? null
}

export function speciesSizeDiagram(name: string): string | null {
  return SPECIES_MEDIA[name]?.sizeDiagram ?? null
}
