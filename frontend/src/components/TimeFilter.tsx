import { Icon } from './Icon'

interface TimeFilterProps {
  bounds: [number, number]
  value: [number, number]
  onChange: (range: [number, number]) => void
}

/** Bottom-centre dual-thumb year range that filters occurrences on the map by detection year. */
export function TimeFilter({ bounds, value, onChange }: TimeFilterProps) {
  const [min, max] = bounds
  const [from, to] = value
  const span = Math.max(1, max - min)
  const leftPct = ((from - min) / span) * 100
  const widthPct = ((to - from) / span) * 100
  const isFull = from === min && to === max

  return (
    <div
      style={{
        position: 'absolute',
        bottom: 28,
        left: '50%',
        transform: 'translateX(-50%)',
        width: 340,
        background: 'var(--color-surface)',
        borderRadius: 12,
        boxShadow: 'var(--shadow-panel)',
        padding: '10px 16px 12px',
        zIndex: 1,
        fontFamily: 'var(--font-sans)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, fontWeight: 800, letterSpacing: 0.5, textTransform: 'uppercase', color: 'var(--color-brand-light)' }}>
          <Icon name="activity" size={13} />
          Detection years
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span className="tnum" style={{ fontSize: 13, fontWeight: 700, color: 'var(--color-ink)' }}>
            {from} – {to}
          </span>
          {!isFull && (
            <button
              onClick={() => onChange(bounds)}
              className="po-link"
              style={{ background: 'none', border: 'none', fontSize: 12, padding: 0 }}
            >
              Reset
            </button>
          )}
        </div>
      </div>

      <div className="po-dual">
        <div className="track" />
        <div className="fill" style={{ left: `${leftPct}%`, width: `${widthPct}%` }} />
        <input
          type="range"
          min={min}
          max={max}
          value={from}
          aria-label="From year"
          onChange={(e) => onChange([Math.min(Number(e.target.value), to), to])}
        />
        <input
          type="range"
          min={min}
          max={max}
          value={to}
          aria-label="To year"
          onChange={(e) => onChange([from, Math.max(Number(e.target.value), from)])}
        />
      </div>
    </div>
  )
}
