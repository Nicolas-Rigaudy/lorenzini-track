import { useEffect, useState } from 'react'
import { API_BASE_URL } from '../config'
import { fetchSpeciesSummary, statusColor, type SpeciesSummary } from '../species'

interface SpeciesPanelProps {
  selectedStudyId: number | null
}

export function SpeciesPanel({ selectedStudyId }: SpeciesPanelProps) {
  const [scientificName, setScientificName] = useState<string | null>(null)
  const [summary, setSummary] = useState<SpeciesSummary | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!selectedStudyId) {
      setScientificName(null)
      setSummary(null)
      return
    }

    fetch(`${API_BASE_URL}/studies/${selectedStudyId}`)
      .then((r) => r.json())
      .then((study) => setScientificName(study.species?.[0] ?? null))
  }, [selectedStudyId])

  useEffect(() => {
    if (!scientificName) {
      setSummary(null)
      return
    }

    setLoading(true)
    fetchSpeciesSummary(scientificName).then((result) => {
      setSummary(result)
      setLoading(false)
    })
  }, [scientificName])

  if (!scientificName) return null

  return (
    <div
      style={{
        position: 'absolute',
        top: 16,
        right: 16,
        bottom: 16,
        width: 300,
        background: 'var(--color-surface)',
        borderRadius: 10,
        boxShadow: '0 2px 12px rgba(15,36,54,0.25)',
        fontFamily: 'var(--font-sans)',
        overflowY: 'auto',
        zIndex: 1,
      }}
    >
      {loading && (
        <div style={{ padding: 16, fontSize: 13, color: 'var(--color-ink-faint)' }}>
          Loading species info…
        </div>
      )}

      {!loading && !summary && (
        <div style={{ padding: 16, fontSize: 13, color: 'var(--color-ink-faint)' }}>
          No Wikipedia entry found for <em>{scientificName}</em>.
        </div>
      )}

      {!loading && summary && (
        <>
          {summary.thumbnailUrl && (
            <img
              src={summary.thumbnailUrl}
              alt={summary.title}
              style={{ width: '100%', height: 160, objectFit: 'cover', display: 'block' }}
            />
          )}
          <div style={{ padding: '12px 16px' }}>
            <div style={{ fontSize: 16, fontWeight: 700, color: 'var(--color-ink)' }}>
              {summary.title}
            </div>
            <div
              style={{
                fontSize: 12,
                fontStyle: 'italic',
                color: 'var(--color-ink-faint)',
                marginTop: 2,
              }}
            >
              {scientificName}
            </div>

            {summary.conservationStatus && (
              <div
                style={{
                  display: 'inline-block',
                  marginTop: 8,
                  padding: '3px 10px',
                  borderRadius: 12,
                  background: statusColor(summary.conservationStatus),
                  color: '#fff',
                  fontSize: 11,
                  fontWeight: 700,
                  textTransform: 'uppercase',
                  letterSpacing: 0.3,
                }}
              >
                IUCN: {summary.conservationStatus}
              </div>
            )}

            <div
              style={{
                fontWeight: 700,
                fontSize: 11,
                textTransform: 'uppercase',
                letterSpacing: 0.4,
                color: 'var(--color-brand-light)',
                marginTop: 14,
              }}
            >
              About
            </div>
            {summary.extract && (
              <p
                style={{
                  fontSize: 13,
                  color: 'var(--color-ink-soft)',
                  lineHeight: 1.5,
                  marginTop: 6,
                  marginBottom: 0,
                }}
              >
                {summary.extract}
              </p>
            )}

            {summary.pageUrl && (
              <a
                href={summary.pageUrl}
                target="_blank"
                rel="noreferrer"
                style={{
                  display: 'inline-block',
                  marginTop: 12,
                  fontSize: 12,
                  fontWeight: 600,
                  color: 'var(--color-brand-light)',
                }}
              >
                Read more on Wikipedia →
              </a>
            )}
          </div>
        </>
      )}
    </div>
  )
}
