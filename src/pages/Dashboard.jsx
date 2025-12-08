import { useLocation, useParams, useNavigate } from "react-router-dom";
import startBg from "../assets/start.png";
import chatbotImg from "../assets/chatbot.png";
import { useMemo, useState } from "react";

export default function Dashboard() {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const selected = (location.state && location.state.selected) || [];

  const cropMap = useMemo(() => ({ 1: "딸기", 2: "토마토", 3: "상추", 4: "배추" }), []);
  const cropIconMap = useMemo(() => ({ 1: "🍓", 2: "🍅", 3: "🥬", 4: "🥬" }), []);
  const cropName = cropMap[id] || "작물";
  const cropIcon = cropIconMap[id] || "🌱";
  
  // Get selected date from location state
  const selectedDate = location.state?.selectedDate || null;
  
  // Calculate days since transplanting
  const daysSinceTransplant = useMemo(() => {
    if (!selectedDate) return 34; // Default value
    
    const transplantDate = new Date(selectedDate.year, selectedDate.month - 1, selectedDate.day);
    const today = new Date();
    const diffTime = today - transplantDate;
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    return diffDays >= 0 ? diffDays : 0;
  }, [selectedDate]);

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

  // Hover state for warning tooltips
  const [showTooltip, setShowTooltip] = useState(false);
  const [showRiskTooltip, setShowRiskTooltip] = useState(false);
  
  // Show warning icon only if stress is 70 or above
  const showWarning = metrics.stress >= 70;
  // Show warning icon only if risk is 70 or above
  const showRiskWarning = metrics.risk >= 70;

  return (
    <div style={styles.container}>
      <div style={styles.overlay} />

      <div style={styles.card}>
        <div style={styles.topRow}>
          <div style={styles.meta}>
            {cropIcon} 품종: <strong>{cropName}</strong>
          </div>
          <div style={styles.metaDivider}></div>
          <div style={styles.meta}>
            🌱 정식 후 {daysSinceTransplant}일차
          </div>
          <div style={styles.metaDivider}></div>
          <div style={styles.meta}>
            📍 현재 단계: 생육기 (15-60일)
          </div>
          <div style={styles.metaDivider}></div>
          <div style={styles.meta}>
            ⏳ 다음 단계까지 {Math.max(0, 60 - daysSinceTransplant)}일 남음
          </div>
        </div>

        <div style={styles.metricsRow}>
          <div style={styles.leftArea}>
            <div style={styles.smallCard}><div style={styles.label}>온도</div><div style={styles.valueBlue}>{metrics.temp}</div></div>
            <div style={styles.smallCard}><div style={styles.label}>습도</div><div style={styles.valueOrange}>{metrics.humid}</div></div>
            <div style={styles.smallCard}><div style={styles.label}>조도</div><div style={styles.valueRed}>{metrics.lux}</div></div>
            <div style={styles.smallCard}><div style={styles.label}>토양 수분</div><div style={styles.valueOrange}>{metrics.soil}</div></div>
          </div>

          <div style={{ ...styles.centerCard, gridRow: "1 / span 2" }}>
            <div style={styles.cardTitle}>
              스트레스 지수{" "}
              {showWarning && (
                <span
                  style={styles.warnIcon}
                  onMouseEnter={() => setShowTooltip(true)}
                  onMouseLeave={() => setShowTooltip(false)}
                >
                  ⚠️
                  {showTooltip && (
                    <div style={styles.tooltip}>
                      <div style={styles.tooltipHeader}>
                        ⚠️ 스트레스 지수 경고
                      </div>
                      <div style={styles.tooltipContent}>
                        고습과 광량 부족으로 스트레스
                        <br />
                        지수가 상승했습니다.
                      </div>
                    </div>
                  )}
                </span>
              )}
            </div>
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
            <div style={styles.cardTitle}>
              병해 위험도{" "}
              {showRiskWarning && (
                <span
                  style={styles.warnIcon}
                  onMouseEnter={() => setShowRiskTooltip(true)}
                  onMouseLeave={() => setShowRiskTooltip(false)}
                >
                  ⚠️
                  {showRiskTooltip && (
                    <div style={{...styles.tooltip, background: "rgba(255, 235, 235, 0.6)", border: "2px solid #ff6b6b"}}>
                      <div style={styles.tooltipHeader}>
                        ⚠️ 병해 위험도 주의
                      </div>
                      <div style={styles.tooltipContent}>
                        현재 환경은 병해가
                        <br />
                        발생하기 쉬운 조건입니다.
                      </div>
                    </div>
                  )}
                </span>
              )}
            </div>
            <div style={styles.riskBarContainer}>
              <div style={styles.riskValue}>{metrics.risk}</div>
              <div style={styles.progressBarWrapper}>
                <div style={styles.progressBarBackground}>
                  <div 
                    style={{
                      ...styles.progressBarFill,
                      width: `${metrics.risk}%`
                    }}
                  />
                </div>
              </div>
            </div>
            <svg width="220" height="90" viewBox="0 0 220 90" style={{ marginTop: "16px" }}>
              <path d="M0 70 C50 40 120 30 220 50 L220 90 L0 90 Z" fill="#ffd7d7" stroke="#f06060" strokeWidth="2" />
            </svg>
          </div>
          
          <div style={{...styles.legend, gridColumn: "3"}}>
            <div style={styles.legendItem}>
              <div style={{...styles.legendDot, backgroundColor: "#2b7aff"}}></div>
              <span style={{...styles.legendText, color: "#2b7aff"}}>적정</span>
            </div>
            <div style={styles.legendItem}>
              <div style={{...styles.legendDot, backgroundColor: "#ff9a2a"}}></div>
              <span style={{...styles.legendText, color: "#ff9a2a"}}>경고</span>
            </div>
            <div style={styles.legendItem}>
              <div style={{...styles.legendDot, backgroundColor: "#ff4d4f"}}></div>
              <span style={{...styles.legendText, color: "#ff4d4f"}}>주의</span>
            </div>
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
        
        <button style={styles.chatbotButton}>
          <img src={chatbotImg} alt="Chatbot" style={styles.chatbotImage} />
        </button>
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
    fontFamily: "'Pretendard', sans-serif",
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
    minHeight: "600px",
  },
  topRow: {
    display: "flex",
    gap: "0",
    alignItems: "center",
    justifyContent: "center",
    paddingBottom: "18px",
    borderBottom: "1px solid #eee",
    marginBottom: "18px",
  },
  meta: { padding: "6px 18px", color: "#333" },
  metaDivider: {
    width: "1px",
    height: "20px",
    backgroundColor: "#ddd",
  },
  leftArea: { display: "grid", gridTemplateColumns: "1fr 1fr", gridTemplateRows: "1fr 1fr", gap: "18px", gridRow: "1 / span 2" },
  metricsRow: { display: "grid", gridTemplateColumns: "2fr 1fr 1fr", gridTemplateRows: "1fr 1fr", gap: "18px", alignItems: "stretch" },
  smallCard: { border: "1px solid #ddd", borderRadius: "12px", padding: "18px 16px", textAlign: "center", minHeight: "120px", display: "flex", flexDirection: "column", justifyContent: "center" },
  label: { color: "black",fontSize: "20px", fontWeight: 800, marginBottom: "6px" },
  valueBlue: { color: "#2b7aff", fontSize: "32px", fontWeight: 800 },
  valueOrange: { color: "#ff9a2a", fontSize: "32px", fontWeight: 800 },
  valueRed: { color: "#ff4d4f", fontSize: "32px", fontWeight: 800 },
  centerCard: { border: "1px solid #ddd", borderRadius: "12px", padding: "32px 16px 18px 16px", textAlign: "center", minHeight: "240px", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center" },
  rightCard: { border: "1px solid #ddd", borderRadius: "12px", padding: "8px 16px 18px 16px", textAlign: "center", minHeight: "240px", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center" },
  // centerNote removed as per design
  warnIcon: { marginLeft: "8px", fontSize: "18px", cursor: "pointer", position: "relative", display: "inline-block" },
  tooltip: {
    position: "absolute",
    top: "100%",
    right: 0,
    marginTop: "8px",
    padding: "12px 16px",
    background: "rgba(255, 248, 225, 0.6)",
    border: "2px solid #f29d3a",
    borderRadius: "8px",
    boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
    zIndex: 1000,
    minWidth: "240px",
    textAlign: "left",
  },
  tooltipHeader: {
    fontWeight: 700,
    fontSize: "14px",
    color: "#000",
    marginBottom: "8px",
    display: "flex",
    alignItems: "center",
    gap: "6px",
  },
  tooltipContent: {
    fontSize: "13px",
    color: "#333",
    lineHeight: "1.5",
  },
  rightNote: { color: "#7a1a1a", background: "#fff0f0", padding: "10px", borderRadius: "8px", margin: "8px auto", maxWidth: "280px", fontSize: "13px" },
  cardTitle: { color: "#000",fontSize: "22px", fontWeight: 700, marginBottom: "18px", marginTop: "0" },
  donutWrap: { display: "flex", justifyContent: "center", alignItems: "center", marginTop: "24px" },
  riskBarContainer: { display: "flex", alignItems: "center", gap: "12px", marginTop: "16px", width: "100%", maxWidth: "200px" },
  riskValue: { color: "#ff4d4f", fontWeight: 800, fontSize: "24px", minWidth: "45px", textAlign: "left" },
  progressBarWrapper: { flex: 1, display: "flex", alignItems: "center", minWidth: 0 },
  progressBarBackground: {
    width: "100%",
    height: "24px",
    backgroundColor: "#e0e0e0",
    borderRadius: "12px",
    overflow: "hidden",
    position: "relative",
  },
  progressBarFill: {
    height: "100%",
    backgroundColor: "#ff4d4f",
    borderRadius: "12px",
    transition: "width 0.3s ease",
    minWidth: "2px",
  },
  toolsBox: { marginTop: "26px", border: "1px solid #ddd", borderRadius: "12px", padding: "20px",marginTop: "16px", marginBottom: "24px" },
  toolsTitle: { color: "#000", textAlign: "center",fontSize: "22px", fontWeight: 700, marginBottom: "12px" },
  toolsRow: { display: "flex", gap: "12px", justifyContent: "center", flexWrap: "wrap" },
  toolBadge: { padding: "10px 18px", borderRadius: "24px", background: "#000", color: "#fff", fontWeight: 700 },
  toolsEmpty: { color: "#888" },
  bottomRight: { display: "flex", justifyContent: "flex-end", marginTop: "18px" },
  solutionBtn: { padding: "12px 26px", borderRadius: "28px", background: "#000", color: "#fff", border: "none", fontWeight: 700, cursor: "pointer" },
  chatbotButton: {
    position: "absolute",
    bottom: "20px",
    left: "28px",
    width: "60px",
    height: "60px",
    borderRadius: "50%",
    background: "#ffffff",
    border: "none",
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    boxShadow: "2px 2px 20.2px rgba(0,0,0,0.15)",
    zIndex: 1000,
    transition: "transform 0.2s ease",
  },
  chatbotImage: {
    width: "40px",
    height: "40px",
    objectFit: "contain",
  },
  legend: {
    display: "flex",
    justifyContent: "right",
    alignItems: "center",
    gap: "10px",
    marginTop: "2px",
  },
  legendItem: {
    display: "flex",
    alignItems: "center",
    gap: "4px",
  },
  legendDot: {
    width: "10px",
    height: "10px",
    borderRadius: "50%",
  },
  legendText: {
    fontSize: "13px",
    color: "#333",
  },
};
