import { useNavigate } from "react-router-dom";
import startBg from "../assets/start.png";

export default function StartPage() {
  const navigate = useNavigate();

  return (
    <div style={styles.container}>
      <div style={styles.overlay} />
      
      <div style={styles.content}>
        <h1 style={styles.mainTitle}>
          작물의 건강을 한눈에,<br />
          병해 예측까지 자동으로
        </h1>
        
        <p style={styles.description}>
          실시간 환경 모니터링, 스트레스 감지, 병해 위험도 분석을 기반으로<br />
          재배에 필요한 의사결정을 스마트하게 돕고, 즉시 대응 솔루션까지 제공합니다.
        </p>
        
        <button
          style={styles.startButton}
          onClick={() => navigate("/crop")}
          onMouseEnter={(e) => {
           e.currentTarget.style.background = "#d0d0d0ff";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = "#ffffff";
          }}
        >
          작물 선택하고 시작하기
          <span style={styles.arrow}>→</span>
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: {
    position: "relative",
    height: "100vh",
    width: "100vw",
    backgroundImage: `url(${startBg})`,
    backgroundSize: "cover",
    backgroundPosition: "center",
    display: "flex",
    alignItems: "center",
    overflow: "hidden",
    fontFamily: "'Pretendard', sans-serif",
  },

  content: {
    position: "relative",
    zIndex: 1,
    marginLeft: "8%",
    maxWidth: "600px",
  },
  mainTitle: {
    fontSize: "48px",
    fontWeight: "700",
    color: "white",
    lineHeight: "1.3",
    marginBottom: "24px",
    textShadow: "0 2px 10px rgba(0, 0, 0, 0.3)",
  },
  description: {
    fontSize: "16px",
    color: "rgba(255, 255, 255, 0.9)",
    lineHeight: "1.6",
    marginBottom: "40px",
    textShadow: "0 1px 5px rgba(0, 0, 0, 0.3)",
  },
  startButton: {
    display: "inline-flex",
    alignItems: "center",
    gap: "12px",
    padding: "16px 32px",
    fontSize: "17px",
    fontWeight: "600",
    color: "black",
    background: "#ffffff",
    border: "1px solid #e0e0e0",
    borderRadius: "50px",
    cursor: "pointer",
    transition: "all 0.3s ease",
    backdropFilter: "blur(10px)",
    boxShadow: "0 4px 15px rgba(0, 0, 0, 0.2)",
  },
  arrow: {
    fontSize: "20px",
    transition: "transform 0.3s ease",
  },
};