export function Legend() {
  const rows: Array<{ swatch: React.ReactNode; label: string }> = [
    {
      swatch: (
        <span
          style={{
            width: 10,
            height: 10,
            borderRadius: '50%',
            background: '#e8702a',
            border: '1px solid #fff',
            display: 'inline-block',
          }}
        />
      ),
      label: 'Species occurrence (click for detail)',
    },
    {
      swatch: (
        <span style={{ fontStyle: 'italic', color: '#0d3a52', fontSize: 12 }}>Aa</span>
      ),
      label: 'Named undersea feature (ridge, seamount, canyon…)',
    },
  ]

  return (
    <div
      style={{
        position: 'absolute',
        bottom: 28,
        left: 16,
        background: 'var(--color-surface)',
        borderRadius: 8,
        boxShadow: '0 1px 6px rgba(15,36,54,0.25)',
        padding: '8px 12px',
        fontFamily: 'var(--font-sans)',
        fontSize: 12,
        color: 'var(--color-ink-soft)',
        zIndex: 1,
      }}
    >
      {rows.map((row, i) => (
        <div
          key={i}
          style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: i ? 4 : 0 }}
        >
          <span style={{ width: 16, display: 'inline-flex', justifyContent: 'center' }}>
            {row.swatch}
          </span>
          {row.label}
        </div>
      ))}
    </div>
  )
}
