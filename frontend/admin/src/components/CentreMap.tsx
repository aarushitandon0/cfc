import { useNavigate } from "react-router-dom"
import type { CentrePayload, Centre } from "../types"
import { healthScoreColor } from "../utils/healthColor"

interface Props {
  centres: Centre[]
  centrePayloads: Map<string, CentrePayload>
}

const VIEWBOX_SIZE = 400
const PADDING = 30

export function CentreMap({ centres, centrePayloads }: Props) {
  const navigate = useNavigate()
  if (centres.length === 0) return null

  const lats = centres.map((c) => c.lat)
  const lngs = centres.map((c) => c.lng)
  const [minLat, maxLat] = [Math.min(...lats), Math.max(...lats)]
  const [minLng, maxLng] = [Math.min(...lngs), Math.max(...lngs)]

  const project = (lat: number, lng: number) => {
    const x = PADDING + ((lng - minLng) / (maxLng - minLng || 1)) * (VIEWBOX_SIZE - 2 * PADDING)
    // latitude increases northward; flip so north is up on screen
    const y =
      VIEWBOX_SIZE -
      PADDING -
      ((lat - minLat) / (maxLat - minLat || 1)) * (VIEWBOX_SIZE - 2 * PADDING)
    return { x, y }
  }

  return (
    <svg
      viewBox={`0 0 ${VIEWBOX_SIZE} ${VIEWBOX_SIZE}`}
      className="w-full h-auto bg-slate-50 rounded-lg border border-slate-200"
      role="img"
      aria-label="District centre map, colored by health score"
    >
      {centres.map((centre) => {
        const { x, y } = project(centre.lat, centre.lng)
        const score = centrePayloads.get(centre.centre_id)?.health_score ?? null
        const radius = centre.type === "CHC" ? 9 : 6
        return (
          <g
            key={centre.centre_id}
            transform={`translate(${x}, ${y})`}
            className="cursor-pointer"
            onClick={() => navigate(`/centres/${centre.centre_id}`)}
          >
            <circle
              r={radius}
              fill={healthScoreColor(score)}
              stroke="#fff"
              strokeWidth={1.5}
              opacity={0.9}
            />
            <text y={-radius - 4} textAnchor="middle" fontSize={9} fill="#374151">
              {centre.name.replace(/ (PHC|CHC)$/, "")}
            </text>
          </g>
        )
      })}
    </svg>
  )
}
