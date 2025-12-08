import { useLocation, useParams, useNavigate } from "react-router-dom";
import startBg from "../assets/start.png";
import { useMemo } from "react";

export default function Dashboard() {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const selected = (location.state && location.state.selected) || [];

  const cropMap = useMemo(() => ({ 1: "딸기", 2: "토마토", 3: "상추", 4: "배추" }), []);
  const cropName = cropMap[id] || "작물";

  // sample metrics (static placeholders matching attached design)
  const metrics = {
    temp: "23.4°C",
    humid: "87%",
    lux: "4,000lux",
    soil: "40%",
    stress: 72,
    risk: 78,
  };

  const handleSolution = () => {
    // placeholder: navigate to a solution page later
    alert("솔루션 확인: 선택 장비 - " + (selected.join(", ") || "없음"));
  };

  return (
    <div style={styles.container}>
      <div style={styles.overlay} />

      <div style={styles.card}>
        <div style={styles.topRow}>
          <div style={styles.meta}>🍓 품종: <strong>{cropName}</strong></div>
          <div style={styles.meta}>🌱 정식 후 34일차</div>
          <div style={styles.meta}>📍 현재 단계: 생육기 (15-60일)</div>
          <div style={styles.meta}>⏳ 다음 단계까지 26일 남음</div>
        </div>

        <div style={styles.metricsRow}>
          <div style={styles.leftArea}>
            <div style={styles.smallCard}><div style={styles.label}>온도</div><div style={styles.valueBlue}>{metrics.temp}</div></div>
            <div style={styles.smallCard}><div style={styles.label}>습도</div><div style={styles.valueOrange}>{metrics.humid}</div></div>
            <div style={styles.smallCard}><div style={styles.label}>조도</div><div style={styles.valueRed}>{metrics.lux}</div></div>
            <div style={styles.smallCard}><div style={styles.label}>토양 수분</div><div style={styles.valueOrange}>{metrics.soil}</div></div>
          </div>

          <div style={{ ...styles.centerCard, gridRow: "1 / span 2" }}>
            <div style={styles.cardTitle}>스트레스 지수 <span style={styles.warnIcon}>⚠️</span></div>
            <div style={styles.donutWrap}>
              {(() => {
                // Gauge: 220 degrees, open at bottom, starting from left
                // 180 degrees extended by 20 degrees on each side (left and right)
                const radius = 85; // Increased chart size
                const strokeW = 12; // Thinner stroke width
                const fullArcDeg = 220; // 220 degrees (180 + 20 left + 20 right)
                const C = 2 * Math.PI * radius;
                // Full arc for 220 degrees
                const fullArc = C * (fullArcDeg / 360);
                // To create 220-degree arc opening downward, centered:
                // 1. Place circle center at top (y = radius)
                // 2. Rotate -200 degrees to start from left (7 o'clock position, 20 degrees before 8 o'clock)
                // 3. This creates a 220-degree arc from 7 o'clock to 1 o'clock (20 degrees left + 180 degrees center + 20 degrees right)
                // Start from the leftmost point
                const startOffset = 0; // No offset needed, rotation handles the positioning
                // Calculate filled length based on stress value (0-100)
                const stressLen = (metrics.stress / 100) * fullArc;
                const bgDash = `${fullArc} ${C}`;
                const fgDash = `${stressLen} ${C}`;
                // Center Y: place circle center at top (y = radius) so semi-circle opens downward
                const centerY = radius;
                // SVG dimensions: adjust to accommodate larger chart
                const svgWidth = 260;
                const svgHeight = 150;
                // Text Y: position above the chart (on top of the arc)
                // Position it above the circle center to be above the semi-circle
                const textY = -radius * 0.1;

                return (
                  <svg width={svgWidth} height={svgHeight} viewBox={`0 0 ${svgWidth} ${svgHeight}`} style={{ overflow: 'visible' }}>
                    <g transform={`translate(${svgWidth / 2}, ${centerY})`}>
                      {/* Background arc (cream color) - semi-circle open at bottom */}
                      <circle 
                        r={radius} 
                        cx={0} 
                        cy={0} 
                        stroke="#fff6e9" 
                        strokeWidth={strokeW} 
                        fill="none" 
                        strokeLinecap="round"
                        strokeDasharray={bgDash} 
                        strokeDashoffset={startOffset}
                        transform="rotate(-200)"
                      />
                      {/* Foreground arc (orange, filled portion) - dynamically changes based on stress value */}
                      <circle 
                        r={radius} 
                        cx={0} 
                        cy={0} 
                        stroke="#f29d3a" 
                        strokeWidth={strokeW} 
                        fill="none" 
                        strokeLinecap="round"
                        strokeDasharray={fgDash} 
                        strokeDashoffset={startOffset}
                        transform="rotate(-200)"
                      />
                      {/* Center text: large number - positioned inside the chart's open space */}
                      <text 
                        x={0} 
                        y={textY} 
                        textAnchor="middle" 
                        fontSize="40" 
                        fontWeight={800} 
                        fill="#f29d3a"
                      >
                        {metrics.stress}
                      </text>
                      {/* Center text: /100 */}
                      <text 
                        x={0} 
                        y={textY + 24} 
                        textAnchor="middle" 
                        fontSize="15" 
                        fill="#999"
                      >
                        /100
                      </text>
                    </g>
                  </svg>
                );
              })()}
            </div>
          </div>

          <div style={{ ...styles.rightCard, gridRow: "1 / span 2" }}>
            <div style={styles.cardTitle}>병해 위험도</div>
            <div style={styles.riskValue}>{metrics.risk}</div>
            <svg width="220" height="90" viewBox="0 0 220 90">
              <path d="M0 70 C50 40 120 30 220 50 L220 90 L0 90 Z" fill="#ffd7d7" stroke="#f06060" strokeWidth="2" />
            </svg>
          </div>
        </div>

        <div style={styles.toolsBox}>
          <div style={styles.toolsTitle}>사용 중인 장비</div>
          <div style={styles.toolsRow}>
            {selected.length ? selected.map((s) => (
              <div key={s} style={styles.toolBadge}>{s}</div>
            )) : <div style={styles.toolsEmpty}>선택된 장비가 없습니다</div>}
          </div>
        </div>

        <div style={styles.bottomRight}>
          <button style={styles.solutionBtn} onClick={handleSolution}>솔루션 확인하기 →</button>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    position: "fixed",
    inset: 0,
    backgroundImage: `url(${startBg})`,
    backgroundSize: "cover",
    backgroundPosition: "center",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontFamily: "'Pretendard', system-ui, Avenir, Helvetica, Arial, sans-serif",
  },
  overlay: {
    position: "absolute",
    inset: 0,
    background: "rgba(0,0,0,0.45)",
  },
  card: {
    position: "relative",
    zIndex: 1,
    width: "92%",
    maxWidth: "1200px",
    background: "white",
    borderRadius: "20px",
    padding: "28px 36px",
    boxShadow: "0 10px 40px rgba(0,0,0,0.25)",
  },
  topRow: {
    display: "flex",
    gap: "18px",
    alignItems: "center",
    paddingBottom: "18px",
    borderBottom: "1px solid #eee",
    marginBottom: "18px",
  },
  meta: { padding: "6px 12px", color: "#333" },
  leftArea: { display: "grid", gridTemplateColumns: "1fr 1fr", gridTemplateRows: "1fr 1fr", gap: "18px", gridRow: "1 / span 2" },
  metricsRow: { display: "grid", gridTemplateColumns: "2fr 1fr 1fr", gridTemplateRows: "1fr 1fr", gap: "18px", alignItems: "stretch" },
  smallCard: { border: "1px solid #ddd", borderRadius: "12px", padding: "18px", textAlign: "center", minHeight: "120px", display: "flex", flexDirection: "column", justifyContent: "center" },
  label: { color: "#666", fontWeight: 600, marginBottom: "6px" },
  valueBlue: { color: "#2b7aff", fontSize: "20px", fontWeight: 800 },
  valueOrange: { color: "#ff9a2a", fontSize: "20px", fontWeight: 800 },
  valueRed: { color: "#ff4d4f", fontSize: "20px", fontWeight: 800 },
  centerCard: { border: "1px solid #ddd", borderRadius: "12px", padding: "18px", textAlign: "center", minHeight: "240px", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center" },
  rightCard: { border: "1px solid #ddd", borderRadius: "12px", padding: "18px", textAlign: "center", minHeight: "240px", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center" },
  // centerNote removed as per design
  warnIcon: { marginLeft: "8px", fontSize: "18px" },
  rightNote: { color: "#7a1a1a", background: "#fff0f0", padding: "10px", borderRadius: "8px", margin: "8px auto", maxWidth: "280px", fontSize: "13px" },
  cardTitle: { color: "#000", fontWeight: 700, marginBottom: "18px" },
  donutWrap: { display: "flex", justifyContent: "center", alignItems: "center", marginTop: "24px" },
  riskValue: { color: "#ff4d4f", fontWeight: 800, fontSize: "24px", marginBottom: "6px" },
  toolsBox: { marginTop: "26px", border: "1px solid #ddd", borderRadius: "12px", padding: "20px" },
  toolsTitle: { color: "#000", textAlign: "center", fontWeight: 700, marginBottom: "12px" },
  toolsRow: { display: "flex", gap: "12px", justifyContent: "center", flexWrap: "wrap" },
  toolBadge: { padding: "10px 18px", borderRadius: "24px", background: "#000", color: "#fff", fontWeight: 700 },
  toolsEmpty: { color: "#888" },
  bottomRight: { display: "flex", justifyContent: "flex-end", marginTop: "18px" },
  solutionBtn: { padding: "12px 26px", borderRadius: "28px", background: "#000", color: "#fff", border: "none", fontWeight: 700, cursor: "pointer" },
};
