import type { SpeciesListItem } from '../speciesApi'

interface LegendProps {
  species: SpeciesListItem[]
  speciesColors: Record<string, string>
}

export function Legend({ species, speciesColors }: LegendProps) {
  const sorted = [...species].sort((a, b) => a.scientific_name.localeCompare(b.scientific_name))

  return (
    <div
      style={{
        position: 'absolute',
        bottom: 28,
        left: 16,
        background: 'var(--color-surface)',
        borderRadius: 8,
        boxShadow: '0 1px 6px rgba(15,36,54,0.25)',
        padding: '10px 12px',
        fontFamily: 'var(--font-sans)',
        fontSize: 12,
        color: 'var(--color-ink-soft)',
        zIndex: 1,
        maxWidth: 240,
      }}
    >
      <div style={{ fontSize: 10.5, fontWeight: 800, letterSpacing: 0.5, textTransform: 'uppercase', color: 'var(--color-brand-light)', marginBottom: 6 }}>
        Species occurrences
      </div>
      {sorted.map((s) => (
        <div key={s.scientific_name} style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 4 }}>
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
          {s.common_name ?? s.scientific_name}
        </div>
      ))}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 8, paddingTop: 8, borderTop: '1px solid var(--color-border)' }}>
        <span style={{ width: 16, height: 3, borderRadius: 2, background: 'linear-gradient(90deg,#ffd166,#06d6a0,#4cc9f0)', flexShrink: 0 }} />
        Tracked path (per individual)
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 4 }}>
        <span style={{ width: 10, display: 'inline-flex', justifyContent: 'center', fontStyle: 'italic', color: 'var(--color-ink-faint)', fontSize: 12 }}>
          Aa
        </span>
        Named undersea feature
      </div>
    </div>
  )
}
