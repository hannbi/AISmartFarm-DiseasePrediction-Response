import { useNavigate } from "react-router-dom";
import { useState } from "react";
import startBg from "../assets/start.png";
import BigStrawberry from "../assets/BigStrawberry.png";
import BigTomato from "../assets/BigTomato.png";
import BigLettuce from "../assets/BigLettuce.png";
import BigCabbage from "../assets/BigCabbage.png";

export default function CropSelect() {
  const navigate = useNavigate();
  const [selectedCrop, setSelectedCrop] = useState(null);
  const [showCalendar, setShowCalendar] = useState(false);
  const [selectedDate, setSelectedDate] = useState(null);
  const [currentYear, setCurrentYear] = useState(2025);
  const [currentMonth, setCurrentMonth] = useState(12);

  const crops = [
    { id: 1, name: "딸기", image: BigStrawberry },
    { id: 2, name: "토마토", image: BigTomato },
    { id: 3, name: "상추", image: BigLettuce },
    { id: 4, name: "배추", image: BigCabbage },
  ];

  const handleCropClick = (cropId) => {
    setSelectedCrop(cropId);
    setShowCalendar(true);
  };

  const handleDateSelect = (day) => {
    setSelectedDate({ year: currentYear, month: currentMonth, day });
  };

  const handleConfirm = () => {
    if (selectedDate) {
      navigate(`/monitoring/${selectedCrop}`, {
        state: { selectedDate }
      });
    }
  };

  const handlePrevMonth = () => {
    if (currentMonth === 1) {
      setCurrentMonth(12);
      setCurrentYear(currentYear - 1);
    } else {
      setCurrentMonth(currentMonth - 1);
    }
    setSelectedDate(null);
  };

  const handleNextMonth = () => {
    if (currentMonth === 12) {
      setCurrentMonth(1);
      setCurrentYear(currentYear + 1);
    } else {
      setCurrentMonth(currentMonth + 1);
    }
    setSelectedDate(null);
  };

  const getDaysInMonth = () => {
    const firstDay = new Date(currentYear, currentMonth - 1, 1).getDay();
    const daysInMonth = new Date(currentYear, currentMonth, 0).getDate();

    const days = [];
    for (let i = 0; i < firstDay; i++) {
      days.push(null);
    }
    for (let i = 1; i <= daysInMonth; i++) {
      days.push(i);
    }
    return days;
  };

  const getMonthRange = () => {
    const lastDay = new Date(currentYear, currentMonth, 0).getDate();
    const firstDate = new Date(currentYear, currentMonth - 1, 1);
    const lastDate = new Date(currentYear, currentMonth - 1, lastDay);

    const dayNames = ['일', '월', '화', '수', '목', '금', '토'];

    return `${currentYear}. ${currentMonth}. 1 ~ ${currentYear}. ${currentMonth}. ${lastDay}`;
  };

  const days = getDaysInMonth();
  const weekDays = ["일", "월", "화", "수", "목", "금", "토"];

  return (
    <>
      <style>
        {`
    .crop-scroll::-webkit-scrollbar {
      height: 5px;
    }

    .crop-scroll::-webkit-scrollbar-track {
      background: #e0e0e0;
      border-radius: 10px;
      margin: 0 500px;
    }

    .crop-scroll::-webkit-scrollbar-thumb {
      background: #343333ff;
      border-radius: 10px;
    }

    .crop-scroll::-webkit-scrollbar-thumb:hover {
      background: #737272ff;
    }

    .crop-scroll {
      padding-bottom: 20px;
      margin-bottom: 20px;
    }
  `}
      </style>

      <div style={styles.container}>
        <div style={styles.overlay} />
        <div style={styles.card}>
          <h2 style={styles.subtitle}>스마트 재배를 위한 첫 단계</h2>
          <h1 style={styles.title}>재배할 작물을 선택하세요</h1>

          <div style={styles.cropsGrid} className="crop-scroll">
            {crops.map((crop) => (
              <div
                key={crop.id}
                style={styles.cropItem}
                onClick={() => handleCropClick(crop.id)}
              >
                <div style={styles.badge}>{crop.id}</div>
                <img src={crop.image} alt={crop.name} style={styles.cropImage} />
                <p style={styles.cropName}>{crop.name}</p>
              </div>
            ))}
          </div>
        </div>

        {showCalendar && (
          <>
            <div style={styles.modalOverlay} onClick={() => setShowCalendar(false)} />
            <div style={styles.calendarModal}>
              <button style={styles.closeBtn} onClick={() => setShowCalendar(false)}>
                ✕
              </button>

              <h2 style={styles.calendarTitle}>작물을 심을 날짜를 선택하세요</h2>

              <div style={styles.calendarHeader}>
                <div style={styles.dateBox}>
                  <button style={styles.navBtn} onClick={handlePrevMonth}>‹</button>
                  <span style={styles.dateRange}>{getMonthRange()}</span>
                  <button style={styles.navBtn} onClick={handleNextMonth}>›</button>
                </div>
              </div>

              <div style={styles.calendar}>
                <div style={styles.weekDays}>
                  {weekDays.map((day, idx) => (
                    <div
                      key={idx}
                      style={{
                        ...styles.weekDay,
                        ...(idx === 0 ? styles.weekDaySunday : {}),
                        ...(idx === 6 ? styles.weekDaySaturday : {})
                      }}
                    >
                      {day}
                    </div>
                  ))}
                </div>

                <div style={styles.daysGrid}>
                  {days.map((day, idx) => {
                    const isSelected = selectedDate &&
                      selectedDate.year === currentYear &&
                      selectedDate.month === currentMonth &&
                      selectedDate.day === day;
                    const isSunday = day && idx % 7 === 0;
                    const isSaturday = day && idx % 7 === 6;
                    
                    // Check if date is in the future
                    const dateObj = day ? new Date(currentYear, currentMonth - 1, day) : null;
                    const today = new Date();
                    today.setHours(0, 0, 0, 0);
                    const isFuture = dateObj && dateObj > today;
                    const isDisabled = isFuture;

                    return (
                      <div
                        key={idx}
                        style={{
                          ...styles.day,
                          ...(day ? styles.dayActive : {}),
                          ...(isSelected ? styles.daySelected : {}),
                          ...(isSelected ? {} : (isSunday ? styles.daySunday : {})),
                          ...(isSelected ? {} : (isSaturday ? styles.daySaturday : {})),
                          ...(isDisabled ? styles.dayDisabled : {}),
                        }}
                        onClick={() => day && !isDisabled && handleDateSelect(day)}
                      >
                        {day}
                      </div>
                    );
                  })}
                </div>
              </div>

              <div style={styles.buttonWrapper}>
                <button
                  style={{
                    ...styles.confirmBtn,
                    ...(selectedDate ? {} : styles.confirmBtnDisabled)
                  }}
                  onClick={handleConfirm}
                  disabled={!selectedDate}
                >
                  다음 단계
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </>
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
    backgroundImage: `url(${startBg})`,
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
    background: "rgba(0, 0, 0, 0.3)",
  },
  card: {
    position: "relative",
    zIndex: 1,
    background: "white",
    borderRadius: "20px",
    padding: "50px 80px",
    maxWidth: "1300px",
    width: "90%",
    minHeight: "300px",
  },
  subtitle: {
    fontSize: "45px",
    fontWeight: "500",
    color: "#666",
    margin: "0 0 10px 0",
  },
  title: {
    fontSize: "40px",
    fontWeight: "700",
    color: "#000",
    margin: "0 0 80px 0",
  },
  cropsGrid: {
    display: "flex",
    gap: "60px",
    overflowX: "auto",
    paddingBottom: "50px",
    scrollSnapType: "x mandatory",
    marginBottom: "5px",
  },
  cropItem: {
    flex: "0 0 auto",
    width: "300px",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    cursor: "pointer",
    position: "relative",
    transition: "transform 0.2s",
    scrollSnapAlign: "center",
  },
  badge: {
    position: "absolute",
    top: "0",
    left: "10px",
    width: "35px",
    height: "35px",
    background: "#000",
    color: "white",
    borderRadius: "6px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "20px",
    fontWeight: "500",
    zIndex: 2,
  },
  cropImage: {
    width: "250px",
    height: "250px",
    objectFit: "contain",
    marginBottom: "20px",
  },
  cropName: {
    fontSize: "25px",
    fontWeight: "600",
    color: "#000",
    margin: 0,
  },
  modalOverlay: {
    position: "fixed",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: "rgba(0, 0, 0, 0.5)",
    zIndex: 10,
  },
  calendarModal: {
    position: "fixed",
    top: "50%",
    left: "50%",
    transform: "translate(-50%, -50%)",
    background: "white",
    borderRadius: "16px",
    padding: "40px",
    zIndex: 11,
    width: "450px",
    boxShadow: "0 10px 40px rgba(0, 0, 0, 0.3)",
  },
  closeBtn: {
    position: "absolute",
    top: "20px",
    right: "20px",
    background: "none",
    border: "none",
    fontSize: "24px",
    cursor: "pointer",
    color: "#666",
    marginTop: "-10px",
  },
  calendarTitle: {
    fontSize: "22px",
    fontWeight: "600",
    textAlign: "center",
    marginBottom: "30px",
    marginTop: "25px",
    color: "#000",
  },
  calendarHeader: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: "20px",
    padding: "0 10px",
  },
  navBtn: {
  background: "none",
  border: "none",
  fontSize: "24px",
  cursor: "pointer",
  padding: "0",  
  color: "#333",
},
  dateRange: {
    fontSize: "16px",
    color: "#333",
    fontWeight: "600",
  },
  calendar: {
    marginBottom: "30px",
  },
  weekDays: {
    display: "grid",
    gridTemplateColumns: "repeat(7, 1fr)",
    gap: "5px",
    marginBottom: "10px",
  },
  weekDay: {
    textAlign: "center",
    fontSize: "14px",
    color: "#666",
    padding: "10px 0",
    fontWeight: "600",
  },
  weekDaySunday: {
    color: "#ff0000",
  },
  weekDaySaturday: {
    color: "#0066ff",
  },
  daysGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(7, 1fr)",
    gap: "5px",
  },
  day: {
    textAlign: "center",
    padding: "12px 0",
    fontSize: "14px",
    color: "#ccc",
    borderRadius: "8px",
  },
  dayActive: {
    color: "#000",
    cursor: "pointer",
  },
  daySelected: {
    background: "#000",
    color: "white",
    fontWeight: "600",
  },
  daySunday: {
    color: "#ff0000",
  },
  daySaturday: {
    color: "#0066ff",
  },
  dayDisabled: {
    color: "#ddd",
    cursor: "not-allowed",
    opacity: 0.5,
  },
  confirmBtn: {
    width: "40%",
    padding: "14px",
    background: "#000",
    color: "white",
    border: "none",
    borderRadius: "50px",
    fontSize: "16px",
    fontWeight: "600",

    cursor: "pointer",
  },
  confirmBtnDisabled: {
    background: "#ccc",
    cursor: "not-allowed",
  },
  dateBox: {
    border: "2px solid #efebebff",
    borderRadius: "25px",
    padding: "5px 24px",
    backgroundColor: "#efebebff",
    display: "flex",
    alignItems: "center",
    gap: "80px",  
  },

  buttonWrapper: {
    display: "flex",
    justifyContent: "center",
  },
  confirmBtn: {
    width: "40%",
    padding: "14px",
    background: "#000",
    color: "white",
    border: "none",
    borderRadius: "50px",
    fontSize: "16px",
    fontWeight: "600",
    cursor: "pointer",
  },
};