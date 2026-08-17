export const HEADER_HEIGHT = 56

export function Header() {
  return (
    <header
      style={{
        height: HEADER_HEIGHT,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 16px',
        background: 'var(--color-brand)',
        color: '#ffffff',
        fontFamily: 'var(--font-sans)',
        zIndex: 2,
        position: 'relative',
        boxShadow: '0 1px 6px rgba(0,0,0,0.25)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 10 }}>
        <span style={{ fontSize: 20 }}>🦈</span>
        <span style={{ fontSize: 17, fontWeight: 700, letterSpacing: 0.2 }}>Poseidon</span>
        <span style={{ fontSize: 13, color: 'rgba(255,255,255,0.75)' }}>
          Marine Wildlife &amp; Telemetry Explorer
        </span>
      </div>
      <span style={{ fontSize: 12, color: 'rgba(255,255,255,0.6)' }}>Research preview</span>
    </header>
  )
}
