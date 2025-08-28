import React, { useState } from "react";

export default function ControlSystem() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  // === Send chat message to FastAPI ===
  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg = { text: input, sender: "user" };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: input }),
      });

      const data = await res.json();
      const botMsg = { text: data.reply, sender: "bot" };
      setMessages((prev) => [...prev, botMsg]);
    } catch (error) {
      const errorMsg = { text: "⚠️ Backend not reachable!", sender: "bot" };
      setMessages((prev) => [...prev, errorMsg]);
    }

    setInput("");
  };

  // === Control button logic ===
  const handleControl = (action) => {
    console.log(`Action: ${action}`);
    // here you could also call FastAPI for manual control
  };

  return (
    <div className="control-system">
      <h1>IoT Control System</h1>
      <div className="system-grid">
        
        {/* Control Panel */}
        <div className="control-panel">
          <h2>Controls</h2>
          <button className="btn" onClick={() => handleControl("lights-on")}>
            Turn Lights On
          </button>
          <button className="btn danger" onClick={() => handleControl("lights-off")}>
            Turn Lights Off
          </button>
          <button className="btn" onClick={() => handleControl("servo-left")}>
            Servo Left
          </button>
          <button className="btn" onClick={() => handleControl("servo-right")}>
            Servo Right
          </button>
        </div>

        {/* Chatbot */}
        <div className="chatbot">
          <h2>IoT Chatbot Assistant</h2>
          <div className="chat-box">
            {messages.map((msg, idx) => (
              <div key={idx} className={`msg ${msg.sender}`}>
                {msg.text}
              </div>
            ))}
          </div>
          <div className="chat-input">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask me about sensors or control..."
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            />
            <button onClick={sendMessage}>Send</button>
          </div>
        </div>

      </div>
    </div>
  );
}
