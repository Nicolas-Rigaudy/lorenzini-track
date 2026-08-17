import { useEffect, useState } from 'react'
import { MapView } from './components/MapView'
import { Sidebar } from './components/Sidebar'
import { Header, HEADER_HEIGHT } from './components/Header'
import { Legend } from './components/Legend'
import { SpeciesPanel } from './components/SpeciesPanel'
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

  function selectStudy(studyId: number | null) {
    setSelectedStudyId(studyId)
    const study = studies.find((s) => s.id === studyId)
    setSelectedSpeciesName(study?.species?.[0] ?? null)
  }

  return (
    <div style={{ height: '100%', width: '100%', display: 'flex', flexDirection: 'column' }}>
      <Header />
      <div style={{ position: 'relative', flex: 1, height: `calc(100% - ${HEADER_HEIGHT}px)` }}>
        <MapView selectedStudyId={selectedStudyId} />
        <Sidebar
          studies={studies}
          loading={studiesLoading}
          selectedStudyId={selectedStudyId}
          onSelectStudy={selectStudy}
          selectedSpeciesName={selectedSpeciesName}
          onSelectSpecies={setSelectedSpeciesName}
        />
        <SpeciesPanel speciesName={selectedSpeciesName} />
        <Legend />
      </div>
    </div>
  )
}

export default App
