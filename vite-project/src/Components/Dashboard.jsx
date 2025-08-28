import React, { useContext, useEffect, useState } from "react";
import { IoTContext } from "./context/IoTContext";

export default function Dashboard() {
  const { carDetected, flameDetected, lightsOn } = useContext(IoTContext);

  const [cards, setCards] = useState([]);

  
  useEffect(() => {
    setCards([
      { title: "Car Sensor", value: carDetected ? "🚗 Car Detected" : "No Car", active: carDetected },
      { title: "Flame Sensor", value: flameDetected ? "🔥 Flame Detected!" : "No Flame", alert: flameDetected },
      { title: "LRDS Lights", value: lightsOn ? "💡 Lights ON" : "Lights OFF", active: lightsOn },
    ]);
  }, [carDetected, flameDetected, lightsOn]);

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
