interface SizeSchematicProps {
  maxLengthM: number
  bodyPlan: 'shark' | 'ray' | null
  label: string
}

const HUMAN_M = 1.8
const VB_W = 320
const VB_H = 96
const BASE_Y = 74 // baseline the silhouettes stand/swim on
const ANIMAL_PX = 232 // the animal always fills this width; human is scaled to the same px/m

/**
 * A to-scale size comparison: a 1.8 m human silhouette next to the animal, both drawn at the
 * same pixels-per-metre so the human reads as the right fraction of the animal's length.
 */
export function SizeSchematic({ maxLengthM, bodyPlan, label }: SizeSchematicProps) {
  const pxPerM = ANIMAL_PX / maxLengthM
  const humanH = Math.max(10, HUMAN_M * pxPerM)
  const humanW = humanH * 0.3
  const humanX = 8

  const animalX0 = humanX + humanW + 18
  const fill = '#17607f'

  return (
    <svg viewBox={`0 0 ${VB_W} ${VB_H}`} width="100%" role="img" aria-label={`Size comparison: a 1.8 metre human next to a ${label} up to ${maxLengthM} metres`}>
      <line x1="4" y1={BASE_Y + 4} x2={VB_W - 4} y2={BASE_Y + 4} stroke="#c3d5dd" strokeWidth="1.5" />

      {/* human */}
      <g fill="#0f4c66">
        <circle cx={humanX + humanW / 2} cy={BASE_Y - humanH + humanW * 0.4} r={humanW * 0.4} />
        <rect
          x={humanX + humanW * 0.2}
          y={BASE_Y - humanH + humanW * 0.9}
          width={humanW * 0.6}
          height={humanH - humanW * 0.9}
          rx={humanW * 0.25}
        />
      </g>
      <text x={humanX + humanW / 2} y={VB_H - 4} fontSize="8" fill="#6b8496" textAnchor="middle">
        1.8 m
      </text>

      {/* animal */}
      {bodyPlan === 'ray' ? (
        <RaySilhouette x0={animalX0} widthPx={ANIMAL_PX} baseY={BASE_Y} fill={fill} />
      ) : (
        <SharkSilhouette x0={animalX0} widthPx={ANIMAL_PX} baseY={BASE_Y} fill={fill} />
      )}
      <text x={animalX0 + ANIMAL_PX / 2} y={VB_H - 4} fontSize="8" fill="#6b8496" textAnchor="middle">
        up to {maxLengthM} m
      </text>
    </svg>
  )
}

function SharkSilhouette({ x0, widthPx, baseY, fill }: { x0: number; widthPx: number; baseY: number; fill: string }) {
  const h = widthPx * 0.26
  const cy = baseY - h / 2
  const bodyRx = widthPx * 0.42
  const bodyCx = x0 + bodyRx
  const tailX = x0 + widthPx
  return (
    <g fill={fill}>
      <ellipse cx={bodyCx} cy={cy} rx={bodyRx} ry={h / 2} />
      <polygon
        points={`${tailX - widthPx * 0.1},${cy} ${tailX},${cy - h * 0.7} ${tailX - widthPx * 0.03},${cy} ${tailX},${cy + h * 0.7}`}
      />
      {/* dorsal fin */}
      <polygon points={`${bodyCx - h * 0.2},${cy - h / 2} ${bodyCx + h * 0.6},${cy - h / 2} ${bodyCx - h * 0.5},${cy - h * 1.25}`} />
      {/* pectoral fin */}
      <polygon points={`${bodyCx - bodyRx * 0.3},${cy + h * 0.3} ${bodyCx + h * 0.1},${cy + h * 0.3} ${bodyCx - bodyRx * 0.35},${cy + h * 1.1}`} />
    </g>
  )
}

function RaySilhouette({ x0, widthPx, baseY, fill }: { x0: number; widthPx: number; baseY: number; fill: string }) {
  // For rays we treat the length dimension as disc width (wingspan); draw a manta-like diamond.
  const h = widthPx * 0.42
  const cy = baseY - h / 2
  const cx = x0 + widthPx / 2
  const tailX = x0 + widthPx / 2
  return (
    <g fill={fill}>
      <polygon
        points={`${x0},${cy} ${cx},${cy - h / 2} ${x0 + widthPx},${cy} ${cx + widthPx * 0.06},${cy + h * 0.18} ${cx},${cy + h / 2} ${cx - widthPx * 0.06},${cy + h * 0.18}`}
      />
      {/* cephalic fins */}
      <rect x={cx - widthPx * 0.02} y={cy - h / 2 - h * 0.18} width={widthPx * 0.02} height={h * 0.2} rx="1" />
      {/* tail */}
      <rect x={tailX - 1} y={cy + h / 2} width="2" height={h * 0.5} />
    </g>
  )
}
