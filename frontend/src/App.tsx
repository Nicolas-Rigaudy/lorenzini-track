import { useEffect, useState } from 'react'
import { MapView } from './components/MapView'
import { Sidebar } from './components/Sidebar'
import { Header, HEADER_HEIGHT } from './components/Header'
import { Legend } from './components/Legend'
import { SpeciesDetail } from './components/SpeciesDetail'
import { API_BASE_URL } from './config'
import type { Study } from './types'

function App() {
  const [studies, setStudies] = useState<Study[]>([])
  const [studiesLoading, setStudiesLoading] = useState(true)
  const [selectedStudyId, setSelectedStudyId] = useState<number | null>(null)
  const [selectedSpeciesName, setSelectedSpeciesName] = useState<string | null>(null)

  useEffect(() => {
    fetch(`${API_BASE_URL}/studies`)
      .then((r) => r.json())
      .then((data) => {
        setStudies(data)
        setStudiesLoading(false)
      })
  }, [])

  // Selecting a species shows its whole profile; the map shows all of its occurrences.
  function selectSpecies(name: string | null) {
    setSelectedSpeciesName(name)
    setSelectedStudyId(null)
  }

  // Selecting a study (from the Studies list) opens the species profile it belongs to,
  // with that study focused on the map.
  function selectStudy(studyId: number | null) {
    setSelectedStudyId(studyId)
    const study = studies.find((s) => s.id === studyId)
    setSelectedSpeciesName(study?.species?.[0] ?? null)
  }

  // Focusing a study from within the species profile keeps the species selected.
  function focusStudy(studyId: number | null) {
    setSelectedStudyId(studyId)
  }

  return (
    <div style={{ height: '100%', width: '100%', display: 'flex', flexDirection: 'column' }}>
      <Header />
      <div style={{ position: 'relative', flex: 1, height: `calc(100% - ${HEADER_HEIGHT}px)` }}>
        <MapView selectedStudyId={selectedStudyId} selectedSpeciesName={selectedSpeciesName} />
        <Sidebar
          studies={studies}
          loading={studiesLoading}
          selectedStudyId={selectedStudyId}
          onSelectStudy={selectStudy}
          selectedSpeciesName={selectedSpeciesName}
          onSelectSpecies={selectSpecies}
        />
        <SpeciesDetail
          speciesName={selectedSpeciesName}
          studies={studies}
          selectedStudyId={selectedStudyId}
          onSelectStudy={focusStudy}
        />
        <Legend />
      </div>
    </div>
  )
}

export default App
