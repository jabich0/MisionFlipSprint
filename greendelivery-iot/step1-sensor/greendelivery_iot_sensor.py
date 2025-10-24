#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GreenDelivery IoT Sensor Simulator - Pharmaceutical Edition
===========================================================
Simulador de sensor IoT para monitorear transporte de medicamentos y productos farmacéuticos críticos
Genera y envía datos de telemetría en tiempo real a un endpoint HTTPS con control de cadena de frío

Autor: Equipo de Ingeniería de Datos
Versión: 1.0 - Pharmaceutical
"""

import json
import time
import random
import datetime
import sys
import os

# Intentar importar requests, si no está disponible usar urllib
try:
    import requests
    USAR_REQUESTS = True
    print("✅ Usando librería requests")
except ImportError:
    import urllib.request
    import urllib.parse
    USAR_REQUESTS = False
    print("⚠️  Usando urllib (instala 'requests' para mejor experiencia)")
    
import paho.mqtt.client as mqtt

# Configuración MQTT opcional (si el broker está disponible)
MQTT_HOST = os.getenv("MQTT_HOST", None)
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "sensors/temperature")

mqtt_client = None
if MQTT_HOST:
    try:
        mqtt_client = mqtt.Client()
        mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
        print(f"📡 Conectado a broker MQTT: {MQTT_HOST}:{MQTT_PORT}")
    except Exception as e:
        print(f"⚠️ No se pudo conectar al broker MQTT: {e}")
        mqtt_client = None

class GreenDeliveryPharmaIoTSensor:
    """
    Simulador de sensor IoT para GreenDelivery - División Farmacéutica
    Monitorea temperatura, humedad, GPS y acelerómetro para transporte de medicamentos
    """
    
    def __init__(self, envio_id=None, endpoint_url=None, ubicacion_inicio=None):
        """
        Inicializa el sensor IoT farmacéutico
        
        Args:
            envio_id (str): ID único del envío farmacéutico (ej: "GD-MEDS-001")
            endpoint_url (str): URL del endpoint en la nube
            ubicacion_inicio (tuple): (latitud, longitud) de inicio
        """
        self.envio_id = envio_id or f"GD-MEDS-{random.randint(1000, 9999)}"
        self.endpoint_url = endpoint_url or "https://webhook.site/ddcd421e-bf7c-490a-9b49-613d06c7ed5c"  # ✅ WEBHOOK.SITE URL
        
        # Ubicación inicial (por defecto Madrid, España - Centro de Distribución Farmacéutica)
        if ubicacion_inicio:
            self.latitud, self.longitud = ubicacion_inicio
        else:
            self.latitud = 40.4168 + random.uniform(-0.02, 0.02)  # Madrid con variación
            self.longitud = -3.7038 + random.uniform(-0.02, 0.02)
        
        # Parámetros base del envío farmacéutico
        self.temperatura_base = random.uniform(3.0, 6.0)  # Temperatura refrigeración farmacéutica (2-8°C)
        self.humedad_base = random.uniform(70, 85)        # Humedad típica para medicamentos
        self.velocidad_movimiento = random.uniform(0.0003, 0.0008)  # Velocidad GPS
        
        # Estadísticas
        self.total_envios = 0
        self.envios_exitosos = 0
        self.alertas_generadas = 0
        
        print(f"💊 Sensor IoT Farmacéutico inicializado")
        print(f"📦 Envío medicamentos: {self.envio_id}")
        print(f"📍 Ubicación inicial: {self.latitud:.4f}, {self.longitud:.4f}")
        print(f"🌐 Endpoint: {self.endpoint_url}")
    
    def generar_datos_telemetria(self):
        """
        Genera datos de telemetría realistas para transporte farmacéutico
        
        Returns:
            dict: Datos del sensor con timestamp, temperatura, humedad, GPS, acelerómetro
        """
        # === TEMPERATURA ===
        # Variación natural ±2°C, con posibilidad de fallo en refrigeración
        variacion_temp = random.uniform(-2.0, 2.0)
        
        # 3% probabilidad de fallo en refrigeración (crítico para medicamentos)
        if random.random() < 0.03:
            variacion_temp += random.uniform(3.0, 7.0)  # Fallo de refrigeración farmacéutica
            
        temperatura = self.temperatura_base + variacion_temp
        
        # === HUMEDAD ===
        # Variación natural ±10% (crítica para estabilidad de medicamentos)
        humedad = self.humedad_base + random.uniform(-10, 10)
        humedad = max(0, min(100, humedad))  # Limitar entre 0-100%
        
        # === GPS (MOVIMIENTO) ===
        # Simular movimiento del vehículo farmacéutico
        self.latitud += random.uniform(-self.velocidad_movimiento, self.velocidad_movimiento)
        self.longitud += random.uniform(-self.velocidad_movimiento, self.velocidad_movimiento)
        
        # === ACELERÓMETRO ===
        # Condiciones normales: 0.8-1.2G
        # Impactos/golpes: 2.5-5.0G (5% probabilidad) - crítico para medicamentos frágiles
        if random.random() < 0.05:  # 5% probabilidad de impacto
            acelerometro_z = random.uniform(2.5, 5.0)
        else:
            acelerometro_z = random.uniform(0.8, 1.2)
        
        # === CREAR PAYLOAD JSON ===
        datos = {
            "ID_envio": self.envio_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "temperatura": round(temperatura, 2),
            "humedad": round(humedad, 1),
            "latitud": round(self.latitud, 6),
            "longitud": round(self.longitud, 6),
            "acelerometro_ejeZ": round(acelerometro_z, 2),
            "estado_sensor": "ACTIVO",
            "bateria": round(random.uniform(85, 100), 1),  # Nivel de batería
            "tipo_carga": "MEDICAMENTOS",
            "temperatura_objetivo": "2-8°C"
        }
        
        return datos
    
    def detectar_anomalias(self, datos):
        """
        Detecta anomalías críticas en el transporte farmacéutico
        
        Args:
            datos (dict): Datos de telemetría
            
        Returns:
            list: Lista de alertas detectadas
        """
        alertas = []
        
        # Regla 1: Temperatura excedida (cadena de frío farmacéutica rota)
        if datos['temperatura'] > 8.0:
            alertas.append({
                "tipo": "TEMPERATURA_CRITICA_FARMACEUTICA",
                "mensaje": f"CADENA DE FRÍO ROTA: {datos['temperatura']}°C > 8°C - Medicamentos en riesgo",
                "severidad": "CRITICA",
                "timestamp": datos['timestamp'],
                "impacto": "Pérdida potencial de eficacia medicamentos"
            })
        
        # Regla 2: Impacto detectado (medicamentos frágiles)
        if datos['acelerometro_ejeZ'] > 3.0:
            alertas.append({
                "tipo": "IMPACTO_MEDICAMENTOS", 
                "mensaje": f"IMPACTO DETECTADO: {datos['acelerometro_ejeZ']}G > 3G - Posible daño a medicamentos",
                "severidad": "ALTA",
                "timestamp": datos['timestamp'],
                "impacto": "Riesgo de rotura de viales/ampollas"
            })
        
        # Regla 3: Humedad muy baja (medicamentos se degradan)
        if datos['humedad'] < 50:
            alertas.append({
                "tipo": "HUMEDAD_CRITICA_FARMACEUTICA",
                "mensaje": f"HUMEDAD CRÍTICA: {datos['humedad']}% < 50% - Degradación medicamentos",
                "severidad": "MEDIA",
                "timestamp": datos['timestamp'],
                "impacto": "Pérdida de estabilidad farmacológica"
            })
        
        return alertas
    
    def enviar_con_requests(self, datos):
        """Envía datos usando la librería requests"""
        try:
            response = requests.post(
                self.endpoint_url,
                json=datos,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'GreenDelivery-Pharma-IoT/1.0'
                },
                timeout=15
            )
            return response.status_code == 200, response.status_code
        except Exception as e:
            return False, str(e)
    
    def enviar_con_urllib(self, datos):
        """Envía datos usando urllib (sin dependencias)"""
        try:
            json_data = json.dumps(datos).encode('utf-8')
            req = urllib.request.Request(
                self.endpoint_url,
                data=json_data,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'GreenDelivery-Pharma-IoT/1.0'
                }
            )
            
            with urllib.request.urlopen(req, timeout=15) as response:
                return response.status == 200, response.status
        except Exception as e:
            return False, str(e)
    
    def enviar_datos(self, datos):
        """
        Envía datos al endpoint configurado
        
        Args:
            datos (dict): Datos de telemetría a enviar
            
        Returns:
            bool: True si el envío fue exitoso
        """
        self.total_envios += 1
        
        # Elegir método de envío según disponibilidad
        if USAR_REQUESTS:
            exito, codigo = self.enviar_con_requests(datos)
        else:
            exito, codigo = self.enviar_con_urllib(datos)
        
        # Mostrar resultado
        timestamp = datos['timestamp'][11:19]  # Solo la hora
        if exito:
            self.envios_exitosos += 1
            print(f"✅ [{timestamp}] Datos enviados - Medicamentos: {datos['ID_envio']}")
            print(f"   🌡️  {datos['temperatura']}°C | 💧 {datos['humedad']}% | ⚡ {datos['acelerometro_ejeZ']}G | 🔋 {datos['bateria']}%")
        else:
            print(f"❌ [{timestamp}] Error en envío: {codigo}")
        
        # Detectar y mostrar alertas
        alertas = self.detectar_anomalias(datos)
        for alerta in alertas:
            self.alertas_generadas += 1
            severidad_emoji = {"CRITICA": "🚨", "ALTA": "⚠️", "MEDIA": "💡"}
            emoji = severidad_emoji.get(alerta['severidad'], "ℹ️")
            print(f"   {emoji} ALERTA {alerta['severidad']}: {alerta['mensaje']}")
            if alerta.get('impacto'):
                print(f"      🔍 Impacto: {alerta['impacto']}")
                
            if mqtt_client:
            try:
                mqtt_client.publish(MQTT_TOPIC, json.dumps(datos))
                print(f"📤 Datos publicados en MQTT ({MQTT_TOPIC})")
            except Exception as e:
                print(f"⚠️ Error publicando en MQTT: {e}")
        
        return exito
    
    def mostrar_estadisticas(self):
        """Muestra estadísticas del monitoreo farmacéutico"""
        exito_pct = (self.envios_exitosos / self.total_envios * 100) if self.total_envios > 0 else 0
        print("\n" + "="*50)
        print("📊 ESTADÍSTICAS DEL MONITOREO FARMACÉUTICO")
        print("="*50)
        print(f"💊 Envío medicamentos monitoreado: {self.envio_id}")
        print(f"📡 Total de transmisiones: {self.total_envios}")
        print(f"✅ Transmisiones exitosas: {self.envios_exitosos} ({exito_pct:.1f}%)")
        print(f"🚨 Alertas farmacéuticas generadas: {self.alertas_generadas}")
        print(f"📍 Última ubicación: {self.latitud:.4f}, {self.longitud:.4f}")
        print(f"❄️  Rango temperatura objetivo: 2-8°C")
    
    def iniciar_monitoreo(self, intervalo=5, duracion=None, modo_demo=False):
        """
        Inicia el monitoreo continuo del sensor farmacéutico
        
        Args:
            intervalo (int): Segundos entre transmisiones (por defecto 5)
            duracion (int): Duración total en segundos (None = infinito)
            modo_demo (bool): Si es True, hace una demostración corta
        """
        if modo_demo:
            print("🎬 MODO DEMOSTRACIÓN FARMACÉUTICA ACTIVADO")
            duracion = 30  # 30 segundos de demo
            intervalo = 3   # Cada 3 segundos
        
        print(f"🚀 INICIANDO MONITOREO IoT FARMACÉUTICO")
        print(f"💊 Tipo de carga: MEDICAMENTOS (cadena de frío 2-8°C)")
        print(f"⏱️  Intervalo: {intervalo} segundos")
        if duracion:
            print(f"⏰ Duración: {duracion} segundos")
        print("🛑 Presiona Ctrl+C para detener")
        print("="*50)
        
        inicio = time.time()
        
        try:
            while True:
                # Generar y enviar datos
                datos = self.generar_datos_telemetria()
                self.enviar_datos(datos)
                
                # Verificar duración máxima
                if duracion and (time.time() - inicio) >= duracion:
                    print(f"\n⏰ Monitoreo farmacéutico completado: {duracion}s transcurridos")
                    break
                
                print()  # Línea en blanco
                time.sleep(intervalo)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoreo farmacéutico detenido por el usuario")
        
        finally:
            self.mostrar_estadisticas()


def main():
    """Función principal del programa"""
    print("💊 GreenDelivery Pharmaceutical IoT Sensor Simulator v1.0")
    print("=" * 60)
    
    # Configuración del sensor farmacéutico
    sensor = GreenDeliveryPharmaIoTSensor(
        envio_id="GD-MEDS-2025-001",
        endpoint_url="https://webhook.site/ddcd421e-bf7c-490a-9b49-613d06c7ed5c",  # ✅ TU WEBHOOK.SITE
        ubicacion_inicio=(40.4168, -3.7038)  # Madrid, España - Centro de Distribución Farmacéutica
    )
    
    print("\n🎯 OPCIONES DE EJECUCIÓN:")
    print("1. Demostración rápida (30s) - Monitoreo farmacéutico")
    print("2. Monitoreo continuo - Cadena de frío medicamentos")
    print("3. Generar solo un dato de prueba farmacéutica")
    
    try:
        opcion = input("\nElige una opción (1-3): ").strip()
        
        if opcion == "1":
            sensor.iniciar_monitoreo(modo_demo=True)
        elif opcion == "2":
            print("\n⚙️ Configuración personalizada:")
            try:
                intervalo = int(input("Intervalo entre envíos en segundos (5): ") or 5)
                duracion_str = input("Duración total en segundos (Enter para infinito): ").strip()
                duracion = int(duracion_str) if duracion_str else None
            except ValueError:
                intervalo, duracion = 5, None
            
            sensor.iniciar_monitoreo(intervalo=intervalo, duracion=duracion)
        elif opcion == "3":
            datos = sensor.generar_datos_telemetria()
            print("\n📊 DATOS FARMACÉUTICOS DE EJEMPLO:")
            print(json.dumps(datos, indent=2, ensure_ascii=False))
            
            # Detectar alertas
            alertas = sensor.detectar_anomalias(datos)
            if alertas:
                print("\n🚨 ALERTAS FARMACÉUTICAS DETECTADAS:")
                for alerta in alertas:
                    print(f"- {alerta['severidad']}: {alerta['mensaje']}")
                    if alerta.get('impacto'):
                        print(f"  Impacto: {alerta['impacto']}")
        else:
            print("❌ Opción no válida")
    
    except KeyboardInterrupt:
        print("\n👋 Programa farmacéutico terminado por el usuario")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


if __name__ == "__main__":
    main()
