import React, { useContext, useState } from "react";
import { IoTContext } from "./context/IoTContext";

export default function ControlSystem() {
  const { lightsOn, setLightsOn, buzzerOn, setBuzzerOn } = useContext(IoTContext);
  const [messages, setMessages] = useState([
    { from: "bot", text: "Hello 👋, I am your IoT assistant! Ask me anything." },
  ]);
  const [input, setInput] = useState("");

  const toggleLights = async () => {
    const newState = !lightsOn;
    try {
      await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: `Control LEDs ${newState ? "ON" : "OFF"}` }),
      });
      setLightsOn(newState);
    } catch (err) {
      console.error(err);
    }
  };

  const toggleBuzzer = async () => {
    const newState = !buzzerOn;
    try {
      await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: `Control Buzzer ${newState ? "ON" : "OFF"}` }),
      });
      setBuzzerOn(newState);
    } catch (err) {
      console.error(err);
    }
  };

  const moveServo = async (angle) => {
    try {
      await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: `Move Servo ${angle}` }),
      });
    } catch (err) {
      console.error(err);
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = { from: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: userMsg.text }),
      });
      const data = await res.json();
      const botMsg = { from: "bot", text: data.reply };
      setMessages((prev) => [...prev, botMsg]);
    } catch (error) {
      const errorMsg = { from: "bot", text: "⚠️ Backend not reachable!" };
      setMessages((prev) => [...prev, errorMsg]);
    }
  };

  return (
    <div className="control-system">
      <h1>IoT Control System</h1>
      <div className="system-grid">
        {/* Manual Controls */}
        <div className="control-panel">
          <h2>Manual Controls</h2>

          <button
            onClick={toggleLights}
            className={`btn ${lightsOn ? "danger" : ""}`}
          >
            {lightsOn ? "Turn Lights OFF" : "Turn Lights ON"}
          </button>

          <button
            onClick={toggleBuzzer}
            className={`btn ${buzzerOn ? "danger" : ""}`}
          >
            {buzzerOn ? "Turn Buzzer OFF" : "Turn Buzzer ON"}
          </button>

          <button
            onClick={() => moveServo(0)}
            className="btn"
          >
            Servo Left
          </button>
          <button
            onClick={() => moveServo(90)}
            className="btn"
          >
            Servo Right
          </button>
        </div>

        {/* Chatbot Assistant */}
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
              placeholder="Ask me about sensors or controls..."
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            />
            <button onClick={sendMessage}>Send</button>
          </div>
        </div>
      </div>
    </div>
  );
}
