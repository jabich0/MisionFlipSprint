import base64
import json
import datetime
import functions_framework # <-- Importamos el framework correcto
from google.cloud import firestore

# --- Configuración de Firestore ---
try:
    db = firestore.Client(project="green-delivery-27c13")
    COLLECTION_NAME = 'envios_telemetria'
except Exception as e:
    print(f"Error CRÍTICO al iniciar Firestore: {e}")
    db = None

# Reglas de negocio
TEMP_MAXIMA = 8.0
ACELEROMETRO_MAXIMO = 3.0

# 🟢 ¡AQUÍ ESTÁ EL ARREGLO! 🟢
# Le decimos que es una función HTTP y que acepta el argumento "request"
@functions_framework.http
def procesar_alerta_y_guardar(request): 
    """
    Esta es la función que Pub/Sub llama.
    Ahora SÍ acepta el argumento "request".
    """

    if db is None:
        print("Error: La base de datos no está conectada.")
        return "Error interno", 500

    try:
        # 1. DECODIFICAR EL MENSAJE DE PUB/SUB
        envelope = request.get_json(silent=True)
        if not envelope or 'message' not in envelope:
            print("Error: Petición inválida, no es un sobre de Pub/Sub.")
            return "Petición inválida", 400

        data_str = base64.b64decode(envelope['message']['data']).decode('utf-8')
        datos = json.loads(data_str)

        id_envio = datos.get('ID_envio', 'ID_Desconocido')
        print(f"Mensaje recibido para el envío: {id_envio}")

    except Exception as e:
        print(f"Error al decodificar el mensaje: {e}")
        return "Error decodificando", 200

    # 2. GUARDAR SIEMPRE EN LA BASE DE DATOS
    try:
        datos['timestamp_procesado_utc'] = datetime.datetime.utcnow()
        db.collection(COLLECTION_NAME).add(datos)
        print(f"Datos guardados en Firestore (Colección: {COLLECTION_NAME})")

    except Exception as e:
        print(f"Error al guardar en Firestore: {e}")
        return "Error guardando en DB", 500 # Fallamos para que Pub/Sub reintente

    # 3. ANALIZAR REGLAS (¿Es una alerta?)
    try:
        temperatura = datos.get('temperatura')
        acelerometro_z = datos.get('acelerometro-ejeZ')
        es_alerta = False

        if temperatura is not None and temperatura > TEMP_MAXIMA:
            es_alerta = True
            print(f"¡ALERTA DE TEMPERATURA! Envío {id_envio} a {temperatura}°C")

        if acelerometro_z is not None and acelerometro_z > ACELEROMETRO_MAXIMO:
            es_alerta = True
            print(f"¡ALERTA DE IMPACTO! Envío {id_envio} con {acelerometro_z}G")

        if es_alerta:
            alerta_data = {
                "ID_envio": id_envio,
                "datos_del_incidente": datos,
                "timestamp_alerta_utc": datetime.datetime.utcnow(),
                "resuelta": False
            }
            db.collection('alertas_generadas').add(alerta_data)
            print("Alerta guardada en la colección 'alertas_generadas'")

    except Exception as e:
        print(f"Error al analizar las reglas: {e}")

    # 4. RESPONDER OK A PUB/SUB
    return "Procesado", 200