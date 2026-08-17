import { useState } from 'react'
import { MapView } from './components/MapView'
import { StudyPanel } from './components/StudyPanel'

function App() {
  const [selectedStudyId, setSelectedStudyId] = useState<number | null>(null)

  return (
    <>
      <MapView selectedStudyId={selectedStudyId} />
      <StudyPanel selectedStudyId={selectedStudyId} onSelect={setSelectedStudyId} />
    </>
  )
}

export default App
