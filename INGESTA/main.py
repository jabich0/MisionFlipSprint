import os
import json
from flask import Flask, jsonify, request
from google.cloud import pubsub_v1

# --- Configuración de Pub/Sub ---
# 🟢 ¡AQUÍ ESTÁ LA CORRECCIÓN! 🟢
# Usamos el ID de tu proyecto directamente como un texto.
PROJECT_ID = "green-delivery-27c13"
TOPIC_ID = "greendelivery-telemetry-events"

publisher = pubsub_v1.PublisherClient()
TOPIC_PATH = publisher.topic_path(PROJECT_ID, TOPIC_ID)

app = Flask(__name__)

@app.route('/', methods=['POST'])
def ingestar_telemetria():
    try:
        datos_telemetria = request.get_json(silent=True)

        # Validación simple de datos
        if not datos_telemetria or 'ID_envio' not in datos_telemetria:
            return jsonify({'message': 'Error: Datos faltantes o inválidos.'}), 400

        # Convertir los datos a bytes para enviarlos
        data_bytes = json.dumps(datos_telemetria).encode("utf-8")

        # Publicar el mensaje en el tema de Pub/Sub
        future = publisher.publish(TOPIC_PATH, data_bytes)
        message_id = future.result() # Espera a que se confirme la publicación

        print(f"Mensaje publicado en Pub/Sub con ID: {message_id}")

        # Respuesta de éxito para el sensor
        return jsonify({'message': 'Datos recibidos y en cola'}), 200

    except Exception as e:
        print(f"Error inesperado durante la publicación: {e}")
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=False, host="0.0.0.0", port=port)