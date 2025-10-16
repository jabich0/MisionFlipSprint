import json, os, time, random
from datetime import datetime, timezone
from dotenv import load_dotenv
import paho.mqtt.client as mqtt

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "docker", ".env"))

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
TOPIC = os.getenv("MQTT_TOPIC", "greendelivery/trackers/telemetry")
PARCEL = os.getenv("PARCEL_ID", "sample-parcel-001")

client = mqtt.Client(client_id=f"sim-{PARCEL}")
client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)

def sample_payload():
    base_temp = random.uniform(2.5, 7.5)
    if random.random() < 0.05:
        base_temp = random.uniform(8.2, 12.0)
    return {
        "parcel_id": PARCEL,
        "ts": datetime.now(timezone.utc).isoformat(),
        "temperature_c": round(base_temp, 2),
        "humidity_pct": round(random.uniform(30, 70), 2),
        "g_force": round(random.uniform(0.0, 3.5), 2),
        "lat": round(random.uniform(-90, 90), 6),
        "lon": round(random.uniform(-180, 180), 6),
    }

if __name__ == "__main__":
    print(f"Publishing to {MQTT_HOST}:{MQTT_PORT} topic {TOPIC}")
    while True:
        payload = sample_payload()
        client.publish(TOPIC, json.dumps(payload), qos=1)
        print("->", payload)
        time.sleep(2)
