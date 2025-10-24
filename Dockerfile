FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir requests paho-mqtt flask google-cloud-pubsub

ENV MQTT_HOST=mosquitto \
    MQTT_PORT=1883 \
    MQTT_TOPIC=greendelivery/trackers/telemetry

CMD ["python", "SENSOR/SIMULADOR.py"]
