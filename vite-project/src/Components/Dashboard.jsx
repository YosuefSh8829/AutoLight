import React, { useState, useEffect } from "react";

export default function Dashboard() {
  const [cards, setCards] = useState([
    { title: "Car Sensor", value: "No Car", active: false },
    { title: "Flame Sensor", value: "No Flame", alert: false },
    { title: "LRDS Lights", value: "Lights OFF", active: false },
  ]);

  // Simulate sensor updates (replace with real IoT/MQTT data)
  useEffect(() => {
    const interval = setInterval(() => {
      const carDetected = Math.random() < 0.5;
      const flameDetected = Math.random() < 0.1;

      setCards([
        { title: "Car Sensor", value: carDetected ? "Car Detected 🚗" : "No Car", active: carDetected },
        { title: "Flame Sensor", value: flameDetected ? "🔥 Flame Detected!" : "No Flame", alert: flameDetected },
        { title: "LRDS Lights", value: carDetected ? "💡 Lights ON" : "Lights OFF", active: carDetected },
      ]);
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="dashboard">
      <h1>IoT Dashboard</h1>
      <div className="cards">
        {cards.map((card, index) => (
          <div
            key={index}
            className={`card ${card.active ? "active" : ""} ${card.alert ? "alert" : ""}`}
          >
            <h2>{card.title}</h2>
            <p>{card.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
