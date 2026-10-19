import type { TaxonOption } from '../taxa'

interface TaxonFilterProps {
  options: TaxonOption[]
  value: string
  onChange: (group: string) => void
}

/** Taxon-family chips in the header; the choice narrows every panel and the map overview. */
export function TaxonFilter({ options, value, onChange }: TaxonFilterProps) {
  if (options.length <= 2) return null // one family plus "All": nothing to choose

  return (
    <div role="group" aria-label="Show taxon family" style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
      {options.map((o) => {
        const active = o.key === value
        return (
          <button
            key={o.key}
            onClick={() => onChange(o.key)}
            aria-pressed={active}
            title={`${o.count} species`}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              padding: '5px 11px',
              borderRadius: 999,
              cursor: 'pointer',
              fontSize: 12.5,
              fontWeight: active ? 700 : 500,
              color: active ? 'var(--color-brand)' : 'rgba(255,255,255,0.86)',
              background: active ? '#ffffff' : 'rgba(255,255,255,0.08)',
              border: `1px solid ${active ? '#ffffff' : 'rgba(255,255,255,0.2)'}`,
            }}
          >
            {o.label}
            <span className="tnum" style={{ fontSize: 11, opacity: 0.7 }}>
              {o.count}
            </span>
          </button>
        )
      })}
    </div>
  )
}
