import { Icon } from './Icon'

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
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <span
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: 30,
            height: 30,
            borderRadius: 8,
            background: 'rgba(255,255,255,0.12)',
            color: '#7fd4ec',
          }}
        >
          <Icon name="waves" size={18} />
        </span>
        <span style={{ fontSize: 17, fontWeight: 700, letterSpacing: 0.3 }}>Poseidon</span>
        <span style={{ fontSize: 13, color: 'rgba(255,255,255,0.72)', fontWeight: 300 }}>
          Marine Wildlife &amp; Telemetry Explorer
        </span>
      </div>
      <span
        style={{
          fontSize: 11,
          fontWeight: 600,
          letterSpacing: 0.4,
          textTransform: 'uppercase',
          color: 'rgba(255,255,255,0.7)',
          border: '1px solid rgba(255,255,255,0.25)',
          borderRadius: 999,
          padding: '3px 10px',
        }}
      >
        Research preview
      </span>
    </header>
  )
}
