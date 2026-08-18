import { useEffect, useState } from 'react'
import { formatDate, type Study } from '../types'
import { fetchSpeciesSummary, statusColor, type SpeciesSummary } from '../species'
import { fetchSpeciesDetail, type SpeciesDetail } from '../speciesApi'
import { SizeSchematic } from './SizeSchematic'
import { Histogram } from './Histogram'
import { BarChart } from './BarChart'
import { Icon } from './Icon'

function cardKeyProps(onActivate: () => void) {
  return {
    role: 'button',
    tabIndex: 0,
    onClick: onActivate,
    onKeyDown: (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault()
        onActivate()
      }
    },
  }
}

interface SpeciesProfileProps {
  scientificName: string
  studies: Study[]
  selectedStudyId: number | null
  onSelectStudy: (studyId: number | null) => void
  onBack: () => void
  color: string
}

const label = {
  fontWeight: 800,
  fontSize: 11,
  textTransform: 'uppercase' as const,
  letterSpacing: 0.5,
  color: 'var(--color-brand-light)',
}

export function SpeciesProfile({
  scientificName,
  studies,
  selectedStudyId,
  onSelectStudy,
  onBack,
  color,
}: SpeciesProfileProps) {
  const [detail, setDetail] = useState<SpeciesDetail | null>(null)
  const [summary, setSummary] = useState<SpeciesSummary | null>(null)

  useEffect(() => {
    setDetail(null)
    setSummary(null)
    fetchSpeciesDetail(scientificName).then(setDetail)
    fetchSpeciesSummary(scientificName).then(setSummary)
  }, [scientificName])

  const facts = detail?.facts
  const studiesForSpecies = studies.filter((s) => s.species.includes(scientificName))
  const yearRange = detail
    ? `${formatDate(detail.date_range.start).slice(0, 4)}–${formatDate(detail.date_range.end).slice(0, 4)}`
    : '…'

  return (
    <div style={{ display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0 }}>
      <div
        style={{
          padding: '11px 14px',
          background: 'var(--color-surface-alt)',
          borderBottom: '1px solid var(--color-border)',
        }}
      >
        <button
          onClick={onBack}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 6,
            cursor: 'pointer',
            background: 'none',
            border: 'none',
            padding: 0,
            ...label,
          }}
        >
          <Icon name="back" size={14} />
          All species
        </button>
      </div>

      <div style={{ overflowY: 'auto', flex: 1, minHeight: 0 }}>
        {/* Hero */}
        <div
          role="img"
          aria-label={`Photograph of ${facts?.common_name ?? scientificName}`}
          style={{
            position: 'relative',
            height: 172,
            background: summary?.thumbnailUrl
              ? `center / cover no-repeat url(${summary.thumbnailUrl})`
              : 'linear-gradient(135deg, #2f6d8c, #123a52)',
          }}
        >
          <div
            style={{
              position: 'absolute',
              inset: 0,
              background:
                'linear-gradient(to top, rgba(8,28,42,.9), rgba(8,28,42,.05) 55%, transparent)',
            }}
          />
          {summary?.conservationStatus && (
            <span
              style={{
                position: 'absolute',
                top: 12,
                right: 12,
                padding: '2px 8px',
                borderRadius: 8,
                background: statusColor(summary.conservationStatus),
                color: '#fff',
                fontSize: 10,
                fontWeight: 800,
                textTransform: 'uppercase',
                letterSpacing: 0.3,
              }}
            >
              {summary.conservationStatus}
            </span>
          )}
          <div style={{ position: 'absolute', left: 16, bottom: 11, color: '#fff' }}>
            <div style={{ fontSize: 22, fontWeight: 800, textShadow: '0 1px 6px rgba(0,0,0,.55)' }}>
              {facts?.common_name ?? summary?.title ?? scientificName}
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 2 }}>
              <span
                title="Colour used for this species on the map"
                style={{ width: 10, height: 10, borderRadius: '50%', background: color, border: '1.5px solid rgba(255,255,255,.85)', flexShrink: 0 }}
              />
              <span style={{ fontSize: 12.5, fontStyle: 'italic', color: '#d7e6ee' }}>{scientificName}</span>
            </div>
          </div>
        </div>

        <div style={{ padding: '14px 16px' }}>
          {/* Stats */}
          {(() => {
            const tiles = [
              { v: detail ? detail.record_count.toLocaleString() : '…', l: 'records' },
              { v: detail ? String(detail.study_count) : '…', l: detail?.study_count === 1 ? 'study' : 'studies' },
              detail && detail.tag_count > 0
                ? { v: String(detail.tag_count), l: detail.tag_count === 1 ? 'individual' : 'individuals' }
                : null,
              { v: yearRange, l: 'tracked' },
            ].filter(Boolean) as { v: string; l: string }[]
            return (
              <div style={{ display: 'grid', gridTemplateColumns: `repeat(${tiles.length}, 1fr)`, gap: 8 }}>
                {tiles.map((t) => (
                  <Tile key={t.l} value={t.v} label={t.l} />
                ))}
              </div>
            )
          })()}

          {/* Size */}
          {facts?.max_length_m && (
            <Section icon="ruler" title="Size">
              <div style={{ background: 'var(--color-surface-alt)', borderRadius: 10, padding: '12px 12px 6px' }}>
                <SizeSchematic
                  maxLengthM={facts.max_length_m}
                  label={facts.common_name ?? scientificName}
                  color={color}
                />
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11.5, marginTop: 6 }}>
                  <span style={{ color: 'var(--color-ink-faint)' }}>Length</span>
                  <span style={{ fontWeight: 700 }}>
                    up to {facts.max_length_m} m
                    {facts.max_weight_kg ? ` · ${formatWeight(facts.max_weight_kg)}` : ''}
                  </span>
                </div>
              </div>
            </Section>
          )}

          {/* Habitat */}
          {facts && (facts.depth_max_m || facts.diet || facts.distribution) && (
            <Section icon="globe" title="Habitat & biology">
              <FactRow k="Depth" v={depthText(facts.depth_min_m, facts.depth_max_m)} />
              <FactRow k="Water" v={tempText(facts.temp_min_c, facts.temp_max_c)} />
              <FactRow k="Diet" v={joinDiet(facts.diet, facts.feeding)} />
              <FactRow k="Range" v={facts.distribution} />
              <FactRow k="Lifespan" v={facts.lifespan_years ? `up to ${facts.lifespan_years} years` : null} />
            </Section>
          )}

          {/* Taxonomy */}
          {facts && (facts.taxon_family || facts.taxon_order) && (
            <Section icon="taxonomy" title="Taxonomy">
              <FactRow k="Class" v={facts.taxon_class} />
              <FactRow k="Order" v={facts.taxon_order} />
              <FactRow k="Family" v={facts.taxon_family} />
            </Section>
          )}

          {/* About */}
          {summary?.extract && (
            <Section icon="book" title="About">
              <p style={{ margin: 0, fontSize: 13, color: 'var(--color-ink-soft)', lineHeight: 1.55 }}>
                {summary.extract}
              </p>
              {summary.pageUrl && (
                <a
                  href={summary.pageUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="po-link"
                  style={{ display: 'inline-flex', alignItems: 'center', gap: 4, marginTop: 8, fontSize: 12.5 }}
                >
                  Read more on Wikipedia
                  <Icon name="external" size={13} />
                </a>
              )}
            </Section>
          )}

          {/* Movement & seasonality */}
          {detail && (
            <Section icon="activity" title="Movement & seasonality">
              <div style={{ fontSize: 11, color: 'var(--color-ink-faint)', marginBottom: 4 }}>
                Detections by month
              </div>
              <Histogram values={detail.monthly_histogram} />
              {detail.yearly_histogram.length > 0 && (
                <>
                  <div style={{ fontSize: 11, color: 'var(--color-ink-faint)', margin: '14px 0 4px' }}>
                    Records by year
                  </div>
                  <BarChart
                    bars={detail.yearly_histogram.map((y) => ({ label: String(y.year), value: y.count }))}
                  />
                </>
              )}
            </Section>
          )}

          {/* Studies */}
          <Section icon="flask" title={`Tracking studies · ${studiesForSpecies.length}`}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {studiesForSpecies.map((study) => {
                const active = study.id === selectedStudyId
                return (
                  <div
                    key={study.id}
                    className="po-card"
                    aria-pressed={active}
                    aria-label={`${study.title}. ${active ? 'Showing on map' : 'Focus map on this study'}`}
                    {...cardKeyProps(() => onSelectStudy(active ? null : study.id))}
                    style={{
                      display: 'flex',
                      gap: 10,
                      alignItems: 'center',
                      border: '1px solid var(--color-border)',
                      borderLeft: active ? '3px solid var(--color-brand-light)' : '3px solid var(--color-border)',
                      borderRadius: 10,
                      padding: 8,
                      background: active ? 'var(--color-accent-soft)' : 'var(--color-surface)',
                    }}
                  >
                    <div
                      role="img"
                      aria-label=""
                      style={{
                        width: 52,
                        height: 42,
                        borderRadius: 6,
                        flexShrink: 0,
                        background: summary?.thumbnailUrl
                          ? `center / cover no-repeat url(${summary.thumbnailUrl})`
                          : 'var(--color-surface-alt)',
                      }}
                    />
                    <div style={{ minWidth: 0 }}>
                      <div style={{ fontSize: 12.5, fontWeight: 700, color: 'var(--color-ink)', lineHeight: 1.2 }}>
                        {study.title}
                      </div>
                      <div style={{ fontSize: 11.5, color: 'var(--color-ink-faint)', marginTop: 3 }}>
                        {study.record_count} records · {formatDate(study.date_range.start)} –{' '}
                        {formatDate(study.date_range.end)}
                        {active ? '' : ' · focus map'}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </Section>
        </div>
      </div>
    </div>
  )
}

function Tile({ value, label: l }: { value: string; label: string }) {
  return (
    <div style={{ background: 'var(--color-surface-alt)', borderRadius: 10, padding: '9px 4px', textAlign: 'center' }}>
      <div className="tnum" style={{ fontSize: 15, fontWeight: 700, color: 'var(--color-brand)' }}>{value}</div>
      <div style={{ fontSize: 10, color: 'var(--color-ink-faint)', marginTop: 2 }}>{l}</div>
    </div>
  )
}

function Section({ icon, title, children }: { icon?: string; title: string; children: React.ReactNode }) {
  return (
    <div style={{ marginTop: 18 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, ...label }}>
        {icon && <Icon name={icon} size={13} />}
        {title}
      </div>
      <div style={{ marginTop: 8 }}>{children}</div>
    </div>
  )
}

function FactRow({ icon, k, v }: { icon?: string; k: string; v: string | null | undefined }) {
  if (!v) return null
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'flex-start',
        gap: 10,
        padding: '7px 0',
        borderBottom: '1px dashed var(--color-border)',
        fontSize: 13,
      }}
    >
      {icon && <span style={{ width: 20, textAlign: 'center', flexShrink: 0 }}>{icon}</span>}
      <span style={{ color: 'var(--color-ink-faint)', width: 74, flexShrink: 0 }}>{k}</span>
      <span style={{ fontWeight: 600, color: 'var(--color-ink)' }}>{v}</span>
    </div>
  )
}

function formatWeight(kg: number): string {
  return kg >= 1000 ? `${(kg / 1000).toFixed(kg % 1000 === 0 ? 0 : 1)} t` : `${kg} kg`
}
function depthText(min: number | null, max: number | null): string | null {
  if (max == null) return null
  return `${min ?? 0} – ${max.toLocaleString()} m`
}
function tempText(min: number | null, max: number | null): string | null {
  if (min == null && max == null) return null
  return `${min ?? '?'}–${max ?? '?'} °C`
}
function joinDiet(diet: string | null, feeding: string | null): string | null {
  if (!diet && !feeding) return null
  return [diet, feeding && `(${feeding.toLowerCase()})`].filter(Boolean).join(' ')
}
