import { useEffect, useState } from 'react'
import { formatDate, type Study } from '../types'
import {
  fetchSpeciesSummary,
  groupStudiesBySpecies,
  speciesStats,
  statusColor,
  type SpeciesSummary,
} from '../species'

interface SpeciesDetailProps {
  speciesName: string | null
  studies: Study[]
  selectedStudyId: number | null
  onSelectStudy: (studyId: number | null) => void
}

const sectionLabel = {
  fontWeight: 700,
  fontSize: 11,
  textTransform: 'uppercase' as const,
  letterSpacing: 0.4,
  color: 'var(--color-brand-light)',
}

export function SpeciesDetail({
  speciesName,
  studies,
  selectedStudyId,
  onSelectStudy,
}: SpeciesDetailProps) {
  const [summary, setSummary] = useState<SpeciesSummary | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!speciesName) {
      setSummary(null)
      return
    }
    setLoading(true)
    fetchSpeciesSummary(speciesName).then((result) => {
      setSummary(result)
      setLoading(false)
    })
  }, [speciesName])

  if (!speciesName) return null

  const studiesForSpecies = groupStudiesBySpecies(studies).get(speciesName) ?? []
  const stats = speciesStats(studiesForSpecies)

  return (
    <div
      style={{
        position: 'absolute',
        top: 16,
        right: 16,
        bottom: 16,
        width: 340,
        background: 'var(--color-surface)',
        borderRadius: 10,
        boxShadow: '0 2px 12px rgba(15,36,54,0.25)',
        fontFamily: 'var(--font-sans)',
        overflowY: 'auto',
        zIndex: 1,
      }}
    >
      {summary?.thumbnailUrl && (
        <img
          src={summary.thumbnailUrl}
          alt={summary.title}
          style={{ width: '100%', height: 170, objectFit: 'cover', display: 'block' }}
        />
      )}

      <div style={{ padding: '14px 16px' }}>
        <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--color-ink)' }}>
          {summary?.title ?? speciesName}
        </div>
        <div
          style={{ fontSize: 12, fontStyle: 'italic', color: 'var(--color-ink-faint)', marginTop: 2 }}
        >
          {speciesName}
        </div>

        {summary?.conservationStatus && (
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

        {/* Cross-study stats */}
        <div
          style={{
            display: 'flex',
            gap: 8,
            marginTop: 14,
          }}
        >
          <Stat value={String(stats.studyCount)} label={stats.studyCount === 1 ? 'study' : 'studies'} />
          <Stat value={String(stats.recordCount)} label="records" />
          <Stat
            value={formatDate(stats.dateStart).slice(0, 4)}
            label={`– ${formatDate(stats.dateEnd).slice(0, 4)}`}
          />
        </div>

        {loading && (
          <div style={{ marginTop: 14, fontSize: 13, color: 'var(--color-ink-faint)' }}>
            Loading species info…
          </div>
        )}

        {!loading && summary?.extract && (
          <>
            <div style={{ ...sectionLabel, marginTop: 16 }}>About</div>
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
          </>
        )}

        {!loading && !summary && (
          <div style={{ marginTop: 14, fontSize: 13, color: 'var(--color-ink-faint)' }}>
            No Wikipedia entry found for <em>{speciesName}</em>.
          </div>
        )}

        {summary?.pageUrl && (
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

        {/* Studies for this species, co-visible with the profile */}
        <div style={{ ...sectionLabel, marginTop: 20 }}>
          Tracking studies ({studiesForSpecies.length})
        </div>
        <div style={{ marginTop: 8, display: 'flex', flexDirection: 'column', gap: 8 }}>
          {studiesForSpecies.map((study) => (
            <StudyCard
              key={study.id}
              study={study}
              expanded={study.id === selectedStudyId}
              onToggle={() =>
                onSelectStudy(study.id === selectedStudyId ? null : study.id)
              }
            />
          ))}
        </div>
      </div>
    </div>
  )
}

function Stat({ value, label }: { value: string; label: string }) {
  return (
    <div
      style={{
        flex: 1,
        background: 'var(--color-surface-alt)',
        borderRadius: 8,
        padding: '8px 6px',
        textAlign: 'center',
      }}
    >
      <div style={{ fontSize: 16, fontWeight: 700, color: 'var(--color-brand)' }}>{value}</div>
      <div style={{ fontSize: 11, color: 'var(--color-ink-faint)', marginTop: 1 }}>{label}</div>
    </div>
  )
}

function StudyCard({
  study,
  expanded,
  onToggle,
}: {
  study: Study
  expanded: boolean
  onToggle: () => void
}) {
  return (
    <div
      onClick={onToggle}
      style={{
        border: '1px solid var(--color-border)',
        borderLeft: expanded
          ? '3px solid var(--color-brand-light)'
          : '3px solid var(--color-border)',
        borderRadius: 8,
        padding: '10px 12px',
        cursor: 'pointer',
        background: expanded ? 'var(--color-accent-soft)' : 'var(--color-surface)',
      }}
    >
      <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--color-ink)' }}>{study.title}</div>
      <div style={{ fontSize: 12, color: 'var(--color-ink-faint)', marginTop: 2 }}>
        {study.record_count} records &middot; {formatDate(study.date_range.start)} –{' '}
        {formatDate(study.date_range.end)}
        {expanded ? '' : ' · click to focus map'}
      </div>

      {expanded && (
        <div style={{ marginTop: 10, paddingTop: 10, borderTop: '1px solid var(--color-border)' }}>
          {study.abstract && (
            <p style={{ margin: '0 0 10px', fontSize: 13, color: 'var(--color-ink-soft)', lineHeight: 1.5 }}>
              {study.abstract}
            </p>
          )}
          <ul style={{ margin: 0, padding: '0 0 0 18px', lineHeight: 1.7, fontSize: 13 }}>
            {study.rights_holder && (
              <li>
                <strong>Conducted by:</strong> {study.rights_holder}
              </li>
            )}
            {study.data_provider && (
              <li>
                <strong>Tagging/data provider:</strong> {study.data_provider}
              </li>
            )}
            {study.published_date && (
              <li>
                <strong>Published:</strong> {formatDate(study.published_date)}
              </li>
            )}
            <li>
              <strong>Licence:</strong> {study.license ?? 'Not specified'}
            </li>
          </ul>
          {study.source_url && (
            <a
              href={study.source_url}
              target="_blank"
              rel="noreferrer"
              onClick={(e) => e.stopPropagation()}
              style={{
                display: 'inline-block',
                marginTop: 10,
                fontSize: 13,
                fontWeight: 600,
                color: 'var(--color-brand-light)',
              }}
            >
              View source dataset →
            </a>
          )}
        </div>
      )}
    </div>
  )
}
