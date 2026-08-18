import { useEffect, useMemo, useState } from 'react'
import { MapView } from './components/MapView'
import { StudiesPanel } from './components/StudiesPanel'
import { SpeciesPanel } from './components/SpeciesPanel'
import { Header, HEADER_HEIGHT } from './components/Header'
import { Legend } from './components/Legend'
import { API_BASE_URL } from './config'
import type { Study } from './types'
import { fetchSpeciesList, type SpeciesListItem } from './speciesApi'
import { buildSpeciesColors } from './speciesColors'

function App() {
  const [studies, setStudies] = useState<Study[]>([])
  const [studiesLoading, setStudiesLoading] = useState(true)
  const [speciesList, setSpeciesList] = useState<SpeciesListItem[]>([])
  const [selectedStudyId, setSelectedStudyId] = useState<number | null>(null)
  const [selectedSpeciesName, setSelectedSpeciesName] = useState<string | null>(null)

  useEffect(() => {
    fetch(`${API_BASE_URL}/studies`)
      .then((r) => r.json())
      .then((data) => {
        setStudies(data)
        setStudiesLoading(false)
      })
    fetchSpeciesList().then(setSpeciesList)
  }, [])

  const speciesColors = useMemo(
    () => buildSpeciesColors(speciesList.map((s) => s.scientific_name)),
    [speciesList],
  )

  // Gallery → profile (and back). Selecting a species shows all of its occurrences on the map.
  function selectSpecies(name: string | null) {
    setSelectedSpeciesName(name)
    setSelectedStudyId(null)
  }

  // Selecting a study from the left list opens the species profile it belongs to, with that
  // study focused on the map.
  function selectStudy(studyId: number | null) {
    setSelectedStudyId(studyId)
    const study = studies.find((s) => s.id === studyId)
    setSelectedSpeciesName(study?.species?.[0] ?? selectedSpeciesName)
  }

  // Focusing a study from inside the species profile keeps the species selected.
  function focusStudy(studyId: number | null) {
    setSelectedStudyId(studyId)
  }

  return (
    <div style={{ height: '100%', width: '100%', display: 'flex', flexDirection: 'column' }}>
      <Header />
      <div style={{ position: 'relative', flex: 1, height: `calc(100% - ${HEADER_HEIGHT}px)` }}>
        <MapView
          selectedStudyId={selectedStudyId}
          selectedSpeciesName={selectedSpeciesName}
          speciesColors={speciesColors}
        />
        <StudiesPanel
          studies={studies}
          loading={studiesLoading}
          selectedStudyId={selectedStudyId}
          onSelectStudy={selectStudy}
        />
        <SpeciesPanel
          speciesList={speciesList}
          speciesColors={speciesColors}
          selectedSpeciesName={selectedSpeciesName}
          onSelectSpecies={selectSpecies}
          studies={studies}
          selectedStudyId={selectedStudyId}
          onSelectStudy={focusStudy}
        />
        <Legend species={speciesList} speciesColors={speciesColors} />
      </div>
    </div>
  )
}

export default App
