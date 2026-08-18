interface Bar {
  label: string
  value: number
}

interface BarChartProps {
  bars: Bar[]
  height?: number
}

/** A compact labelled bar chart (e.g. records per year). Labels sit under each bar. */
export function BarChart({ bars, height = 68 }: BarChartProps) {
  const max = Math.max(1, ...bars.map((b) => b.value))
  if (bars.length === 0) {
    return (
      <div style={{ fontSize: 12, color: 'var(--color-ink-faint)' }}>No dated detections to chart.</div>
    )
  }
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'flex-end', gap: 6, height }}>
        {bars.map((b) => (
          <div
            key={b.label}
            title={`${b.label}: ${b.value.toLocaleString()}`}
            style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', height: '100%' }}
          >
            <div
              style={{
                height: `${(b.value / max) * 100}%`,
                minHeight: b.value > 0 ? 3 : 0,
                background: 'linear-gradient(to top, var(--color-brand-light), #5bb0cd)',
                borderRadius: '3px 3px 0 0',
              }}
            />
          </div>
        ))}
      </div>
      <div style={{ display: 'flex', gap: 6, marginTop: 4 }}>
        {bars.map((b) => (
          <div
            key={b.label}
            className="tnum"
            style={{ flex: 1, textAlign: 'center', fontSize: 9, color: 'var(--color-ink-faint)' }}
          >
            {b.label}
          </div>
        ))}
      </div>
    </div>
  )
}
