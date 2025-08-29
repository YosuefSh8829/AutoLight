from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import paho.mqtt.client as mqtt
from langchain.agents import initialize_agent, AgentType, Tool
from langchain_google_genai import ChatGoogleGenerativeAI
import uvicorn

# --- MQTT Setup ---
BROKER = "e10ae8e9b2d54a6d96198879f7d83758.s1.eu.hivemq.cloud"
PORT = 8883
MQTT_USER = "hivemq.webclient.1756145271255"
MQTT_PASS = "1KTtGo38;2$pMw:Ze>Fd"

# ✅ Match ESP32 topics
TOPIC_IR1 = "home/ir1"
TOPIC_IR2 = "home/ir2"
TOPIC_SERVO = "home/servo"
TOPIC_LDR = "home/ldr"
TOPIC_FIRE = "home/fire"
TOPIC_BUZZER = "home/buzzer"   # ✅ new
TOPIC_LEDS = "home/leds"       # ✅ new

mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
mqtt_client.tls_set()   # 🔥 Enable TLS for HiveMQ Cloud

latest_ir1 = None
latest_ir2 = None
latest_ldr = None
latest_fire = None

# --- MQTT Callbacks ---
def on_connect(client, userdata, flags, rc):
    print("Connected with result code", rc)
    client.subscribe(TOPIC_IR1)
    client.subscribe(TOPIC_IR2)
    client.subscribe(TOPIC_LDR)
    client.subscribe(TOPIC_FIRE)

def on_message(client, userdata, msg):
    global latest_ir1, latest_ir2, latest_ldr, latest_fire
    try:
        if msg.topic == TOPIC_IR1:
            latest_ir1 = int(msg.payload.decode())
        elif msg.topic == TOPIC_IR2:
            latest_ir2 = int(msg.payload.decode())
        elif msg.topic == TOPIC_LDR:
            latest_ldr = int(msg.payload.decode())
        elif msg.topic == TOPIC_FIRE:
            latest_fire = int(msg.payload.decode())
    except ValueError:
        pass

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(BROKER, PORT, 60)
mqtt_client.loop_start()

# --- Tool Functions ---
def get_ir1_reading(_=None):
    return str(latest_ir1) if latest_ir1 is not None else "IR1 reading not available"

def get_ir2_reading(_=None):
    return str(latest_ir2) if latest_ir2 is not None else "IR2 reading not available"

def get_ldr_reading(_=None):
    return str(latest_ldr) if latest_ldr is not None else "LDR reading not available"

def get_fire_status(_=None):
    if latest_fire is None:
        return "Fire sensor reading not available"
    return "FIRE DETECTED!" if latest_fire == 1 else "No fire detected"

def move_servo(angle: str):
    try:
        angle_int = int(angle)
        if angle_int not in [0, 90]:
            return "Invalid angle. Must be 0 or 90."
    except ValueError:
        return "Invalid angle. Provide a 0 or 90 degree angle."
    mqtt_client.publish(TOPIC_SERVO, str(angle_int))
    return f"Servo moved to {angle_int}°"

def control_buzzer(state: str):
    state = state.upper()
    if state not in ["ON", "OFF"]:
        return "Invalid buzzer state. Must be ON or OFF."
    mqtt_client.publish(TOPIC_BUZZER, state)
    return f"Buzzer turned {state}"

def control_leds(state: str):
    state = state.upper()
    if state not in ["ON", "OFF"]:
        return "Invalid LED state. Must be ON or OFF."
    mqtt_client.publish(TOPIC_LEDS, state)
    return f"LEDs turned {state}"

# --- LangChain Agent ---
tools = [
    Tool(name="Get IR1 Reading", func=get_ir1_reading, description="Get the latest IR1 sensor reading."),
    Tool(name="Get IR2 Reading", func=get_ir2_reading, description="Get the latest IR2 sensor reading."),
    Tool(name="Get LDR Reading", func=get_ldr_reading, description="Get the latest LDR sensor reading."),
    Tool(name="Get Fire Status", func=get_fire_status, description="Check if fire is detected."),
    Tool(name="Move Servo", func=move_servo, description="Move servo to a specified angle."),
    Tool(name="Control Buzzer", func=control_buzzer, description="Turn buzzer ON or OFF."),  # ✅ new
    Tool(name="Control LEDs", func=control_leds, description="Turn all LEDs ON or OFF."),   # ✅ new
]

system_prompt = """
You are an IoT smart road analyst assistant.

Available tools:
- Get IR1 Reading → returns latest IR1 sensor value.
- Get IR2 Reading → returns latest IR2 sensor value.
- Get LDR Reading → returns latest LDR sensor value.
- Get Fire Status → returns fire detection status.
- Move Servo → moves the servo motor to a specified angle (0–90).
- Control Buzzer → turn the buzzer ON or OFF.
- Control LEDs → turn all LEDs ON or OFF.

Rules:
1. ALWAYS use the tools — do not explain, just call the tool.
2. For sensors: if none, respond exactly “reading not available”.
3. Servo: input must be 0 or 90.
4. Buzzer: input must be ON or OFF.
5. LEDs: input must be ON or OFF.
6. If impossible, reply with: “I cannot do that.”
"""

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key="AIzaSyAJyXzk6ZGyae-N6oQ_r49x5hGPi098gb8"
)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
    return_only_outputs=True
)

# --- Pydantic Request Model ---
class ChatRequest(BaseModel):
    text: str

# --- FastAPI App ---
app = FastAPI()

@app.post("/chat")
async def chat(request: ChatRequest):
    user_input = request.text
    try:
        reply = agent.invoke({
            "input": user_input,
            "chat_history": [{"role": "system", "content": system_prompt}]
        })
        return JSONResponse({"reply": reply.get("output", "")})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run("bot:app", host="0.0.0.0", port=8000, reload=True)



# from fastapi import FastAPI, Request
# from fastapi.responses import JSONResponse
# import paho.mqtt.client as mqtt
# from langchain.agents import initialize_agent, AgentType, Tool
# from langchain_google_genai import ChatGoogleGenerativeAI
# import uvicorn

# # --- MQTT Setup ---
# BROKER = "Insert Broker"
# PORT = "Insert Port"
# TOPIC_IR1 = "home/ir1"
# TOPIC_IR2 = "home/ir2"
# TOPIC_SERVO = "home/servo"
# TOPIC_LDR = "home/ldr"
# TOPIC_FIRE = "home/fire"

# mqtt_client = mqtt.Client()
# latest_ir1 = None
# latest_ir2 = None
# latest_ldr = None
# latest_fire = None
# led_state = "off"

# def on_connect(client, userdata, flags, rc):
#     print("Connected with result code", rc)
#     client.subscribe(TOPIC_IR1)
#     client.subscribe(TOPIC_IR2)
#     client.subscribe(TOPIC_LDR)
#     client.subscribe(TOPIC_FIRE)

#     # Handle messages for each sensor
# def on_message(client, userdata, msg):
#     global latest_ir1, latest_ir2, latest_ldr, latest_fire
#     try:
#         if msg.topic == TOPIC_IR1:
#             latest_ir1 = int(msg.payload.decode())
#         elif msg.topic == TOPIC_IR2:
#             latest_ir2 = int(msg.payload.decode())
#         elif msg.topic == TOPIC_LDR:
#             latest_ldr = int(msg.payload.decode())
#         elif msg.topic == TOPIC_FIRE:
#             latest_fire = int(msg.payload.decode())
#     except ValueError:
#         pass

# mqtt_client.on_connect = on_connect
# mqtt_client.on_message = on_message
# mqtt_client.connect(BROKER, PORT, 60)
# mqtt_client.loop_start()

# # --- Tool Functions ---
# def get_ir1_reading(_=None):
#     return str(latest_ir1) if latest_ir1 is not None else "IR1 reading not available"

# def get_ir2_reading(_=None):
#     return str(latest_ir2) if latest_ir2 is not None else "IR2 reading not available"

# def get_ldr_reading(_=None):
#     return str(latest_ldr) if latest_ldr is not None else "LDR reading not available"

# def get_fire_status(_=None):
#     if latest_fire is None:
#         return "Fire sensor reading not available"
#     return "FIRE DETECTED!" if latest_fire == 1 else "No fire detected"


# def move_servo(angle: str):
#     try:
#         angle_int = int(angle)
#         if angle_int != 0 or angle_int != 90:
#             return "Invalid angle. Must be 0 or 90."
#     except ValueError:
#         return "Invalid angle. Provide a 0 or 90 degree angle."
#     mqtt_client.publish(TOPIC_SERVO, str(angle_int))
#     return f"Servo moved to {angle_int}°"

# # --- LangChain Agent ---
# tools = [
#     Tool(name="Get IR1 Reading", func=get_ir1_reading, description="Get the latest IR1 sensor reading."),
#     Tool(name="Get IR2 Reading", func=get_ir2_reading, description="Get the latest IR2 sensor reading."),
#     Tool(name="Get LDR Reading", func=get_ldr_reading, description="Get the latest LDR sensor reading."),
#     Tool(name="Get Fire Status", func=get_fire_status, description="Check if fire is detected."),
#     Tool(name="Move Servo", func=move_servo, description="Move servo to a specified angle."),
# ]


# system_prompt = """
# You are an IoT smart road analyst assistant...

# Available tools:
# - Get IR1 Reading → returns latest IR1 sensor value.
# - Get IR2 Reading → returns latest IR2 sensor value.
# - Get LDR Reading → returns latest LDR sensor value.
# - Get Fire Status → returns fire detection status.
# - Move Servo → moves the servo motor to a specified angle (0–90).

# Rules:
# 1. ALWAYS use the tools — do not explain, just call the tool.
# 2. For sensors: if none, respond exactly “reading not available”.
# 3. Servo: input must be 0–90.
# 4. If impossible, reply with: “I cannot do that.”
# """


# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash",
#     google_api_key="AIzaSyAJyXzk6ZGyae-N6oQ_r49x5hGPi098gb8"
# )
 
# agent = initialize_agent(
#     tools=tools,
#     llm=llm,
#     agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
#     verbose=True,
#     handle_parsing_errors=True,
#     return_only_outputs=True
# )

# # --- FastAPI App ---
# app = FastAPI()

# @app.post("/chat")
# async def chat(request: Request):
#     data = await request.json()
#     user_input = data.get("text", "")
#     try:
#         reply = agent.invoke({
#             "input": user_input,
#             "chat_history": [{"role": "system", "content": system_prompt}]
#         })
#         return JSONResponse({"reply": reply.get("output", "")})
#     except Exception as e:
#         return JSONResponse({"error": str(e)}, status_code=500)

# if __name__ == "__main__":
#     uvicorn.run("bot:app", host="0.0.0.0", port=8000, reload=True)