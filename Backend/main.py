from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import paho.mqtt.client as mqtt
from supabase import create_client, Client
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI
import uvicorn

# -------------------- SUPABASE CONFIG --------------------
SUPABASE_URL = "https://wczwmlhzsousesecnvnu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndjendtbGh6c291c2VzZWNudm51Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY0MTg0OTEsImV4cCI6MjA3MTk5NDQ5MX0.McW3rnjF6eY1WLO41Tqd7f8ePjazvLHkBhl5r2pMMq4"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------- FASTAPI APP --------------------
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- MQTT CONFIG --------------------
BROKER = "e10ae8e9b2d54a6d96198879f7d83758.s1.eu.hivemq.cloud"
PORT = 8883
MQTT_USER = "hivemq.webclient.1756145271255"
MQTT_PASS = "1KTtGo38;2$pMw:Ze>Fd"

TOPIC_IR1 = "home/ir1"
TOPIC_IR2 = "home/ir2"
TOPIC_SERVO = "home/servo"
TOPIC_LDR = "home/ldr"
TOPIC_FIRE = "home/fire"
TOPIC_BUZZER = "home/buzzer"
TOPIC_LEDS = "home/leds"

mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
mqtt_client.tls_set()

latest_ir1 = None
latest_ir2 = None
latest_ldr = None
latest_fire = None
latest_buzzer = None
latest_leds = None

def on_connect(client, userdata, flags, rc):
    print("Connected with result code", rc)
    client.subscribe([
        (TOPIC_IR1, 0),
        (TOPIC_IR2, 0),
        (TOPIC_LDR, 0),
        (TOPIC_FIRE, 0),
        (TOPIC_BUZZER, 0),
        (TOPIC_LEDS, 0)
    ])

def on_message(client, userdata, msg):
    global latest_ir1, latest_ir2, latest_ldr, latest_fire, latest_buzzer, latest_leds
    try:
        value = int(msg.payload.decode())
        sensor_name = None

        if msg.topic == TOPIC_IR1:
            latest_ir1 = value
            sensor_name = "ir1"
        elif msg.topic == TOPIC_IR2:
            latest_ir2 = value
            sensor_name = "ir2"
        elif msg.topic == TOPIC_LDR:
            latest_ldr = value
            sensor_name = "ldr"
        elif msg.topic == TOPIC_FIRE:
            latest_fire = value
            sensor_name = "fire"
        elif msg.topic == TOPIC_BUZZER:
            latest_buzzer = value
            sensor_name = "buzzer"
        elif msg.topic == TOPIC_LEDS:
            latest_leds = value
            sensor_name = "leds"

        if sensor_name:
            supabase.table("sensor_readings").insert({
                "sensor_name": sensor_name,
                "value": value
            }).execute()
            print(f"Inserted: {sensor_name} = {value}")

            if sensor_name == "fire" and value == 1:
                supabase.table("alerts").insert({"message": "🔥 Fire detected!"}).execute()

    except Exception as e:
        print("MQTT error:", e)

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(BROKER, PORT, 60)
mqtt_client.loop_start()

# -------------------- SENSOR TOOL FUNCTIONS --------------------
def get_ir1_reading(_=None):
    return str(latest_ir1) if latest_ir1 is not None else "IR1 reading not available"

def get_ir2_reading(_=None):
    return str(latest_ir2) if latest_ir2 is not None else "IR2 reading not available"

def get_ldr_reading(_=None):
    return str(latest_ldr) if latest_ldr is not None else "LDR reading not available"

def get_fire_status(_=None):
    if latest_fire is None:
        return "Fire sensor reading not available"
    return "🔥 FIRE DETECTED!" if latest_fire == 1 else "✅ No fire detected"

def move_servo(angle: str):
    try:
        angle_int = int(angle)
        if angle_int not in [0, 90]:
            return "Invalid angle. Must be 0 or 90."
    except ValueError:
        return "Invalid angle. Provide 0 or 90."
    mqtt_client.publish(TOPIC_SERVO, str(angle_int))
    supabase.table("access_logs").insert({"action": f"Servo moved to {angle_int}°"}).execute()
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

# -------------------- LANGCHAIN AGENT --------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key="AIzaSyAJyXzk6ZGyae-N6oQ_r49x5hGPi098gb8"
)

tools = [
    Tool(name="Get IR1 Reading", func=get_ir1_reading, description="Get latest IR1 sensor reading"),
    Tool(name="Get IR2 Reading", func=get_ir2_reading, description="Get latest IR2 sensor reading"),
    Tool(name="Get LDR Reading", func=get_ldr_reading, description="Get latest LDR sensor reading"),
    Tool(name="Get Fire Status", func=get_fire_status, description="Check fire detection status"),
    Tool(name="Move Servo", func=move_servo, description="Move servo to 0 or 90 degrees"),
    Tool(name="Control Buzzer", func=control_buzzer, description="Turn buzzer ON or OFF"),
    Tool(name="Control LEDs", func=control_leds, description="Turn all LEDs ON or OFF")
]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# -------------------- CHAT ROUTE --------------------
class ChatRequest(BaseModel):
    text: str

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        reply = agent.run(request.text)
        return JSONResponse({"reply": reply})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# -------------------- DATA ROUTES --------------------
@app.get("/latest-readings")
async def latest_readings():
    try:
        response = supabase.table("sensor_readings").select("*").order("id", desc=True).execute()
        latest_per_sensor = {}
        for record in response.data:
            if "sensor_name" in record and "value" in record:
                if record["sensor_name"] not in latest_per_sensor:
                    latest_per_sensor[record["sensor_name"]] = record["value"]
        return latest_per_sensor
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{sensor}")
async def get_history(sensor: str):
    try:
        response = supabase.table("sensor_readings").select("*")\
            .eq("sensor_name", sensor).order("id", desc=True).limit(20).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/alerts")
async def get_alerts():
    try:
        response = supabase.table("alerts").select("*").order("id", desc=True).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs")
async def get_logs():
    try:
        response = supabase.table("access_logs").select("*").order("id", desc=True).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------- RUN --------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
