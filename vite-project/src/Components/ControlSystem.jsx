import React, { useContext, useState } from "react";
import { IoTContext } from "./context/IoTContext";

export default function ControlSystem() {
  const { lightsOn, setLightsOn, flameDetected, setFlameDetected, carDetected, setCarDetected } = useContext(IoTContext);

  const [messages, setMessages] = useState([
    { from: "bot", text: "Hello 👋, I am your IoT assistant!" },
  ]);
  const [input, setInput] = useState("");

  const toggleLights = () => setLightsOn(!lightsOn);

  const handleSend = () => {
    if (!input.trim()) return;
    const userMsg = { from: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);

    let botReply = "I didn't understand 🤖";
    if (input.toLowerCase().includes("light on")) {
      setLightsOn(true);
      botReply = "✅ Lights turned ON!";
    } else if (input.toLowerCase().includes("light off")) {
      setLightsOn(false);
      botReply = "✅ Lights turned OFF!";
    } else if (input.toLowerCase().includes("flame")) {
      botReply = flameDetected ? "🔥 Flame detected!" : "No flame right now.";
    } else if (input.toLowerCase().includes("car")) {
      setCarDetected(true);
      botReply = "🚗 Car detected!";
    }

    setMessages((prev) => [...prev, { from: "bot", text: botReply }]);
    setInput("");
  };

  return (
    <div className="control-system">
      <h1>IoT Control System</h1>
      <div className="system-grid">
        <div className="control-panel">
          <h2>Manual Controls</h2>
          <button onClick={toggleLights} className="btn">
            {lightsOn ? "Turn Lights OFF" : "Turn Lights ON"}
          </button>
          <button onClick={() => setFlameDetected(false)} className="btn danger">
            Reset Flame Alert
          </button>
          <button onClick={() => setCarDetected(false)} className="btn">
            Reset Car Sensor
          </button>
        </div>

        <div className="chatbot">
          <h2>Chatbot Assistant 🤖</h2>
          <div className="chat-box">
            {messages.map((msg, i) => (
              <div key={i} className={`msg ${msg.from}`}>
                {msg.text}
              </div>
            ))}
          </div>
          <div className="chat-input">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask me something..."
            />
            <button onClick={handleSend}>Send</button>
          </div>
        </div>
      </div>
    </div>
  );
}
