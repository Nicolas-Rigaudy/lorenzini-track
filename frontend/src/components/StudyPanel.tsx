import { useEffect, useState } from 'react'
import { API_BASE_URL } from '../config'

interface Study {
  id: number
  title: string
  abstract: string | null
  source_url: string | null
  license: string | null
  rights_holder: string | null
  published_date: string | null
  record_count: number
  date_range: { start: string | null; end: string | null }
  species: string[]
}

interface StudyPanelProps {
  selectedStudyId: number | null
  onSelect: (studyId: number | null) => void
}

export function StudyPanel({ selectedStudyId, onSelect }: StudyPanelProps) {
  const [studies, setStudies] = useState<Study[]>([])

  useEffect(() => {
    fetch(`${API_BASE_URL}/studies`)
      .then((r) => r.json())
      .then(setStudies)
  }, [])

  return (
    <div
      style={{
        position: 'absolute',
        top: 12,
        left: 12,
        width: 320,
        maxHeight: 'calc(100% - 24px)',
        overflowY: 'auto',
        background: 'rgba(255,255,255,0.95)',
        borderRadius: 6,
        boxShadow: '0 1px 4px rgba(0,0,0,0.3)',
        fontFamily: 'system-ui, sans-serif',
        fontSize: 13,
        zIndex: 1,
      }}
    >
      <div style={{ padding: '10px 12px', fontWeight: 600, borderBottom: '1px solid #ddd' }}>
        Studies ({studies.length})
      </div>

      {studies.map((study) => {
        const isSelected = study.id === selectedStudyId
        return (
          <div
            key={study.id}
            onClick={() => onSelect(isSelected ? null : study.id)}
            style={{
              padding: '10px 12px',
              borderBottom: '1px solid #eee',
              cursor: 'pointer',
              background: isSelected ? '#fef1e8' : 'transparent',
            }}
          >
            <div style={{ fontWeight: 600 }}>{study.title}</div>
            <div style={{ color: '#555', marginTop: 2 }}>
              {study.species.join(', ')} &middot; {study.record_count} records
            </div>
            <div style={{ color: '#888', fontSize: 12 }}>
              {study.date_range.start?.slice(0, 10)} &ndash; {study.date_range.end?.slice(0, 10)}
            </div>

            {isSelected && (
              <div style={{ marginTop: 8, color: '#333' }}>
                {study.abstract && <p style={{ margin: '0 0 8px' }}>{study.abstract}</p>}
                <div>
                  <strong>Licence:</strong> {study.license ?? 'Not specified'}
                </div>
                {study.rights_holder && (
                  <div>
                    <strong>Rights holder:</strong> {study.rights_holder}
                  </div>
                )}
                {study.source_url && (
                  <div style={{ marginTop: 4 }}>
                    <a href={study.source_url} target="_blank" rel="noreferrer">
                      View source dataset
                    </a>
                  </div>
                )}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
