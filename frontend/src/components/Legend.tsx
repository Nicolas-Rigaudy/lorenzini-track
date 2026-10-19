import { useState } from 'react'
import type { SpeciesListItem } from '../speciesApi'
import { Icon } from './Icon'
import { byLegendName } from '../speciesColors'

interface LegendProps {
  species: SpeciesListItem[]
  speciesColors: Record<string, string>
}

export function Legend({ species, speciesColors }: LegendProps) {
  const [open, setOpen] = useState(false)
  const sorted = [...species].sort(byLegendName)

  // Anchored over the map, clear of the left studies panel and above the time filter.
  const base = { position: 'absolute' as const, left: 358, zIndex: 1, fontFamily: 'var(--font-sans)' }

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        style={{
          ...base,
          bottom: 28,
          display: 'inline-flex',
          alignItems: 'center',
          gap: 7,
          padding: '8px 12px',
          background: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: 999,
          boxShadow: 'var(--shadow-panel)',
          cursor: 'pointer',
          fontSize: 12.5,
          fontWeight: 600,
          color: 'var(--color-ink)',
        }}
      >
        <Icon name="layers" size={15} style={{ color: 'var(--color-brand-light)' }} />
        Legend
      </button>
    )
  }

  return (
    <div
      style={{
        ...base,
        bottom: 28,
        width: 210,
        maxHeight: 'calc(100% - 56px)',
        display: 'flex',
        flexDirection: 'column',
        background: 'var(--color-surface)',
        borderRadius: 10,
        boxShadow: 'var(--shadow-panel)',
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '8px 10px 8px 12px',
          background: 'var(--color-surface-alt)',
          borderBottom: '1px solid var(--color-border)',
        }}
      >
        <span style={{ fontSize: 10.5, fontWeight: 800, letterSpacing: 0.5, textTransform: 'uppercase', color: 'var(--color-brand-light)' }}>
          Species · {sorted.length}
        </span>
        <button
          onClick={() => setOpen(false)}
          aria-label="Collapse legend"
          style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-ink-faint)', fontSize: 15, lineHeight: 1, padding: 2 }}
        >
          ×
        </button>
      </div>

      <div style={{ overflowY: 'auto', padding: '8px 12px', fontSize: 12, color: 'var(--color-ink-soft)' }}>
        {sorted.map((s) => (
          <div key={s.scientific_name} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 5 }}>
            <span
              style={{
                width: 10,
                height: 10,
                borderRadius: '50%',
                background: speciesColors[s.scientific_name] ?? '#9fb2bd',
                border: '1px solid #fff',
                flexShrink: 0,
              }}
            />
            <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {s.common_name ?? s.scientific_name}
            </span>
          </div>
        ))}
        <div style={{ marginTop: 8, paddingTop: 8, borderTop: '1px solid var(--color-border)', display: 'flex', flexDirection: 'column', gap: 6 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ width: 16, height: 3, borderRadius: 2, background: 'linear-gradient(90deg,#ffd166,#06d6a0,#4cc9f0)', flexShrink: 0 }} />
            Tracked path (per individual)
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ width: 10, display: 'inline-flex', justifyContent: 'center', fontStyle: 'italic', color: 'var(--color-ink-faint)', fontSize: 12 }}>Aa</span>
            Named undersea feature
          </div>
        </div>
      </div>
    </div>
  )
}
