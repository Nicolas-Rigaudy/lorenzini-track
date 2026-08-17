import { useState } from 'react'
import { MapView } from './components/MapView'
import { StudyPanel } from './components/StudyPanel'
import { Header, HEADER_HEIGHT } from './components/Header'
import { Legend } from './components/Legend'

function App() {
  const [selectedStudyId, setSelectedStudyId] = useState<number | null>(null)

  return (
    <div style={{ height: '100%', width: '100%', display: 'flex', flexDirection: 'column' }}>
      <Header />
      <div style={{ position: 'relative', flex: 1, height: `calc(100% - ${HEADER_HEIGHT}px)` }}>
        <MapView selectedStudyId={selectedStudyId} />
        <StudyPanel selectedStudyId={selectedStudyId} onSelect={setSelectedStudyId} />
        <Legend />
      </div>
    </div>
  )
}

export default App
