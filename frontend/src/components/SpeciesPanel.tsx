import { useState } from 'react'
import type { Study } from '../types'
import type { SpeciesListItem } from '../speciesApi'
import { speciesColor } from '../speciesColors'
import { SpeciesGallery } from './SpeciesGallery'
import { SpeciesProfile } from './SpeciesProfile'
import { Icon } from './Icon'

interface SpeciesPanelProps {
  speciesList: SpeciesListItem[]
  speciesColors: Record<string, string>
  selectedSpeciesName: string | null
  onSelectSpecies: (name: string | null) => void
  studies: Study[]
  selectedStudyId: number | null
  onSelectStudy: (studyId: number | null) => void
}

export function SpeciesPanel({
  speciesList,
  speciesColors,
  selectedSpeciesName,
  onSelectSpecies,
  studies,
  selectedStudyId,
  onSelectStudy,
}: SpeciesPanelProps) {
  const [search, setSearch] = useState('')

  return (
    <div
      style={{
        position: 'absolute',
        top: 16,
        right: 16,
        bottom: 16,
        width: 372,
        display: 'flex',
        flexDirection: 'column',
        background: 'var(--color-surface)',
        borderRadius: 12,
        boxShadow: '0 2px 14px rgba(15,36,54,0.28)',
        fontFamily: 'var(--font-sans)',
        overflow: 'hidden',
        zIndex: 1,
      }}
    >
      {selectedSpeciesName ? (
        <SpeciesProfile
          scientificName={selectedSpeciesName}
          studies={studies}
          selectedStudyId={selectedStudyId}
          onSelectStudy={onSelectStudy}
          onBack={() => onSelectSpecies(null)}
          color={speciesColor(speciesColors, selectedSpeciesName)}
        />
      ) : (
        <>
          <div style={{ padding: '12px 14px', background: 'var(--color-surface-alt)', borderBottom: '1px solid var(--color-border)' }}>
            <div style={{ fontSize: 12, fontWeight: 800, letterSpacing: 0.6, textTransform: 'uppercase', color: 'var(--color-brand-light)' }}>
              Species · {speciesList.length}
            </div>
            <div className="po-searchwrap" style={{ marginTop: 9 }}>
              <Icon name="search" size={15} />
              <input
                className="po-input"
                type="search"
                aria-label="Search species"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search species…"
              />
            </div>
          </div>
          <SpeciesGallery
            species={speciesList}
            speciesColors={speciesColors}
            search={search}
            onSelect={onSelectSpecies}
          />
        </>
      )}
    </div>
  )
}
