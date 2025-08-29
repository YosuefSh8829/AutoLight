import React, { useContext, useEffect, useState } from "react";
import { IoTContext } from "./context/IoTContext";
import axios from "axios";

export default function Dashboard() {
  const [cards, setCards] = useState([]);
  const [sensorData, setSensorData] = useState({});

  // Fetch sensor readings from FastAPI
  useEffect(() => {
    const fetchSensorData = async () => {
      try {
        const res = await axios.get("http://localhost:8000/latest-readings");
        setSensorData(res.data);
      } catch (err) {
        console.error("Error fetching sensor data:", err);
      }
    };

    fetchSensorData();
    const interval = setInterval(fetchSensorData, 5000); // Refresh every 5s
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    setCards([
  
      { title: "IR1", value: sensorData.ir1 ?? "N/A" },
      { title: "IR2", value: sensorData.ir2 ?? "N/A" },
      { title: "LDR", value: sensorData.ldr ?? "N/A" },
      { title: "Fire Sensor", value: sensorData.fire === 1 ? "🔥 FIRE DETECTED!" : "✅ No Fire" },
    ]);
  }, [sensorData]);

  return (
    <div className="dashboard">
      <h1>IoT Dashboard</h1>
      <div className="cards">
        {cards.map((card, index) => (
          <div
            key={index}
            className={`card ${card.active ? "active" : ""} ${card.alert ? "alert" : ""} animate-card`}
          >
            <h2>{card.title}</h2>
            <p>{card.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
