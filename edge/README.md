# Simulador IoT (Edge)

## Ejecución
```bash
pip install -r requirements.txt
# Ajusta docker/.env (MQTT_HOST/MQTT_PORT)
python simulator.py
```
Publica mensajes JSON cada 2 segundos en el tópico configurado (por defecto `greendelivery/trackers/telemetry`).
