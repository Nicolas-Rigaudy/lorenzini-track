interface HistogramProps {
  /** 12 values, one per calendar month (Jan…Dec). */
  values: number[]
}

const MONTH_INITIALS = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']

/** Seasonal detections-by-month bar chart. Empty when there is no dated data. */
export function Histogram({ values }: HistogramProps) {
  const max = Math.max(1, ...values)
  const total = values.reduce((a, b) => a + b, 0)
  if (total === 0) {
    return (
      <div style={{ fontSize: 12, color: 'var(--color-ink-faint)', marginTop: 8 }}>
        No dated detections to chart.
      </div>
    )
  }

  return (
    <div style={{ marginTop: 8 }}>
      <div style={{ display: 'flex', alignItems: 'flex-end', gap: 4, height: 68 }}>
        {values.map((v, i) => (
          <div
            key={i}
            title={`${MONTH_INITIALS[i]}: ${v} detection${v === 1 ? '' : 's'}`}
            style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', height: '100%' }}
          >
            <div
              style={{
                height: `${(v / max) * 100}%`,
                minHeight: v > 0 ? 3 : 0,
                background: 'linear-gradient(to top, var(--color-brand-light), #5bb0cd)',
                borderRadius: '3px 3px 0 0',
              }}
            />
          </div>
        ))}
      </div>
      <div style={{ display: 'flex', gap: 4, marginTop: 4 }}>
        {MONTH_INITIALS.map((m, i) => (
          <div
            key={i}
            style={{ flex: 1, textAlign: 'center', fontSize: 9, color: 'var(--color-ink-faint)' }}
          >
            {m}
          </div>
        ))}
      </div>
    </div>
  )
}
