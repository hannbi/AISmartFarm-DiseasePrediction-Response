import { useState } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import startBg from "../assets/start.png";
import Bg from "../assets/background.png";


export default function Monitoring() {
  const { id } = useParams();
  const location = useLocation();
  const [selected, setSelected] = useState(new Set());
  const selectedDate = location.state?.selectedDate || null;

  const toggle = (key) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  const navigate = useNavigate();

  const handleResult = () => {
    const list = Array.from(selected);
    // navigate to dashboard and pass selected items and date in state
    navigate(`/dashboard/${id}`, { 
      state: { 
        selected: list,
        selectedDate: selectedDate
      } 
    });
  };

  const groups = [
    { title: "🌡 온도 제어", items: ["난방기", "냉방기", "보온 커튼", "쿨링패드"] },
    { title: "💧 습도 제어", items: ["가습기", "제습기"] },
    { title: "🌀 환기 및 순환", items: ["환풍기"] },
    { title: "💡 광 제어", items: ["생장 LED"] },
    { title: "🪴 기타", items: ["CO₂ 발생기", "자동 관수 시스템"] },
  ];

  return (
    <div style={styles.container}>
      <div style={styles.overlay} />

      <div style={styles.card}>
        <h2 style={styles.header}>작물 분석을 위한 초기 설정</h2>
        <h3 style={styles.subheader}>사용 중인 장비를 선택하세요</h3>

        <div style={styles.grid}>
          {groups.map((g) => (
            <div key={g.title} style={styles.group}>
              <div style={styles.groupTitle}>{g.title}</div>
              <div style={styles.row}>
                {g.items.map((it) => (
                  <button
                    key={it}
                    onClick={() => toggle(it)}
                    style={{
                      ...styles.tag,
                      ...(selected.has(it) ? styles.tagActive : {}),
                    }}
                  >
                    {it}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div style={styles.center}>
          <button style={styles.resultBtn} onClick={handleResult}>
            결과 보기
          </button>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    position: "fixed",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    width: "100%",
    height: "100%",
    backgroundImage: `url(${Bg})`,
    backgroundSize: "cover",
    backgroundPosition: "center",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    overflow: "hidden",
    margin: 0,
    padding: 0,
    fontFamily: "'Pretendard', sans-serif",
  },
  overlay: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: "rgba(0,0,0,0.45)",
  },
  card: {
    position: "relative",
    zIndex: 1,
    width: "90%",
    maxWidth: "1100px",
    background: "white",
    borderRadius: "20px",
    padding: "40px 60px",
    boxShadow: "0 10px 40px rgba(0,0,0,0.25)",
  },
  header: {
    margin: 0,
    fontSize: "20px",
    fontWeight: 500,
    color: "#111",
  },
  subheader: {
    marginTop: "8px",
    marginBottom: "24px",
    fontSize: "20px",
    fontWeight: 700,
    color: "#111",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "18px 40px",
  },
  group: {},
  groupTitle: {
    fontWeight: 700,
    fontSize: "18px",
    marginBottom: "10px",
    color: "#111",
  },
  row: {
    display: "flex",
    gap: "12px",
    flexWrap: "wrap",
  },
  tag: {
    padding: "10px 18px",
    borderRadius: "24px",
    border: "1px solid #000",
    background: "transparent",
    cursor: "pointer",
    fontWeight: 600,
    color: "#111",
    transition: "all 160ms ease",
  },
  tagActive: {
    background: "#000",
    border: "1px solid #000",
    color: "#fff",
  },
  center: {
    display: "flex",
    justifyContent: "center",
    marginTop: "26px",
  },
  resultBtn: {
    padding: "12px 28px",
    borderRadius: "24px",
    background: "#000",
    color: "#fff",
    border: "none",
    fontWeight: 700,
    cursor: "pointer",
  },
};
