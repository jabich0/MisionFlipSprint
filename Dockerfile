FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir requests paho-mqtt

CMD ["python", "greendelivery_iot_sensor.py"]
