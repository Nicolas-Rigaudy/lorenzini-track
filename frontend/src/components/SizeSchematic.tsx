interface SizeSchematicProps {
  maxLengthM: number
  label: string
  color?: string
}

const HUMAN_M = 1.8

/**
 * A clean, to-scale size comparison: a human bar and the animal's bar share one scale, so the
 * human reads as the right fraction of the animal's length. No illustrations — just bars.
 */
export function SizeSchematic({ maxLengthM, label, color = 'var(--color-brand-light)' }: SizeSchematicProps) {
  const rows = [
    { name: 'Human', m: HUMAN_M, fill: '#9fb2bd' },
    { name: label, m: maxLengthM, fill: color },
  ]
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      {rows.map((row) => (
        <div key={row.name} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{ width: 92, fontSize: 11.5, color: 'var(--color-ink-soft)', flexShrink: 0, textAlign: 'right' }}>
            {row.name}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div
              style={{
                width: `${Math.max(2, (row.m / maxLengthM) * 100)}%`,
                height: 12,
                background: row.fill,
                borderRadius: 3,
              }}
            />
          </div>
          <div style={{ width: 54, fontSize: 11.5, fontWeight: 700, color: 'var(--color-ink)', flexShrink: 0 }}>
            {row.m} m
          </div>
        </div>
      ))}
    </div>
  )
}
