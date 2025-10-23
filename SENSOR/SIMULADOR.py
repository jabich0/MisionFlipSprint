#!/usr/bin/env python3
"""
💊 GreenDelivery Pharmaceutical IoT Sensor Simulator v2.0
========================================================
Simulador de sensor IoT para transporte de medicamentos con:
- Monitoreo de cadena de frío (2-8°C)
- GPS tracking
- Detección de impactos
- Integración con Google Cloud
- Alertas farmacéuticas automáticas
"""

import requests
import json
import time
import random
import threading
from datetime import datetime, timezone

# Verificar dependencias
try:
    import requests
    print("✅ Usando librería requests")
except ImportError:
    print("❌ Error: requests no instalado")
    print("💡 Instalar con: pip install requests")
    exit(1)

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
        self.endpoint_url = endpoint_url or "hhttps://greendelivery-pharma-gateway-587952111457.europe-west1.run.app"
        
        # Ubicación inicial (por defecto Madrid, España - Centro de Distribución Farmacéutica)
        if ubicacion_inicio:
            self.latitud, self.longitud = ubicacion_inicio
        else:
            self.latitud = 40.4168 + random.uniform(-0.02, 0.02)  # Madrid con variación
            self.longitud = -3.7038 + random.uniform(-0.02, 0.02)
        
        # Parámetros base del envío farmacéutico
        self.temperatura_base = random.uniform(3.0, 6.0)  # Temperatura refrigeración farmacéutica (2-8°C)
        self.humedad_base = random.uniform(70, 85)        # Humedad típica para medicamentos
        self.velocidad_movimiento = random.uniform(0.0003, 0.0008)  # Velocidad GPS para medicamentos
        
    def generar_datos_sensor(self):
        """
        Genera datos realistas del sensor IoT farmacéutico
        
        Returns:
            dict: Datos del sensor con validaciones farmacéuticas
        """
        
        # Simular variaciones realistas en cadena de frío
        variacion_temp = random.uniform(-1.5, 2.5)
        if random.random() < 0.15:  # 15% probabilidad de alerta térmica
            variacion_temp += random.uniform(3.0, 8.0)  # Ruptura cadena de frío
            
        temperatura = max(0, self.temperatura_base + variacion_temp)
        
        # Humedad crítica para medicamentos
        humedad = max(30, min(95, self.humedad_base + random.uniform(-10, 15)))
        
        # Simulación de movimiento (rutas de distribución farmacéutica)
        self.latitud += random.uniform(-self.velocidad_movimiento, self.velocidad_movimiento)
        self.longitud += random.uniform(-self.velocidad_movimiento, self.velocidad_movimiento)
        
        # Acelerómetro (detección de impactos críticos para viales/ampollas)
        aceleracion_base = random.uniform(0.8, 1.5)
        if random.random() < 0.08:  # 8% probabilidad de impacto fuerte
            aceleracion_base += random.uniform(2.0, 6.0)  # Impacto que podría dañar medicamentos
            
        sensor_data = {
            "ID_envio": self.envio_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "temperatura": round(temperatura, 2),
            "humedad": round(humedad, 1),
            "latitud": round(self.latitud, 6),
            "longitud": round(self.longitud, 6),
            "acelerometro_ejeZ": round(aceleracion_base, 2),
            "estado_sensor": "ACTIVO",
            "bateria": round(random.uniform(85, 100), 1),
            "tipo_carga": "MEDICAMENTOS",
            "temperatura_objetivo": "2-8°C"
        }
        
        return sensor_data
    
    def detectar_alertas_farmaceuticas(self, datos):
        """
        Detecta alertas críticas para medicamentos
        
        Args:
            datos (dict): Datos del sensor
            
        Returns:
            list: Lista de alertas detectadas
        """
        alertas = []
        
        # Alerta crítica: Cadena de frío rota
        if datos["temperatura"] > 8.0:
            alertas.append({
                "tipo": "CADENA_FRIO_ROTA",
                "severidad": "CRITICA",
                "temperatura": datos["temperatura"],
                "descripcion": f"Temperatura {datos['temperatura']}°C > 8°C - Medicamentos en riesgo",
                "impacto": "Pérdida potencial de eficacia medicamentos"
            })
        
        # Alerta alta: Impacto fuerte (riesgo viales/ampollas)
        if datos["acelerometro_ejeZ"] > 3.0:
            alertas.append({
                "tipo": "IMPACTO_DETECTADO",
                "severidad": "ALTA", 
                "aceleracion": datos["acelerometro_ejeZ"],
                "descripcion": f"Impacto {datos['acelerometro_ejeZ']}G > 3G - Posible daño a medicamentos",
                "impacto": "Riesgo de rotura de viales/ampollas"
            })
            
        # Alerta media: Humedad excesiva
        if datos["humedad"] > 90:
            alertas.append({
                "tipo": "HUMEDAD_EXCESIVA",
                "severidad": "MEDIA",
                "humedad": datos["humedad"],
                "descripcion": f"Humedad {datos['humedad']}% > 90% - Riesgo degradación",
                "impacto": "Posible degradación de principios activos"
            })
            
        return alertas
    
    def enviar_datos(self, datos):
        """
        Envía datos al endpoint en la nube con manejo de errores
        
        Args:
            datos (dict): Datos del sensor a enviar
            
        Returns:
            bool: True si el envío fue exitoso
        """
        try:
            response = requests.post(self.endpoint_url, json=datos, timeout=10)
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            if response.status_code == 200:
                print(f"✅ [{timestamp}] Datos enviados - Medicamentos: {self.envio_id}")
                
                # MOSTRAR RESPUESTA DE GOOGLE CLOUD
                try:
                    respuesta_google = response.json()
                    print(f"🚀 RESPUESTA GOOGLE CLOUD:")
                    print(f"   💊 {respuesta_google.get('message', '')}")
                    print(f"   📦 Envío: {respuesta_google.get('envio_id', '')}")
                    print(f"   🌡️ Temperatura: {respuesta_google.get('temperatura_actual', '')}")
                    print(f"   📊 Status: {respuesta_google.get('status', '')}")
                    print(f"   ✅ Cadena frío: {respuesta_google.get('cumple_cadena_frio', '')}")
                    print(f"   ⏰ Procesado: {respuesta_google.get('timestamp', '')}")
                    if respuesta_google.get('alertas') and len(respuesta_google.get('alertas', [])) > 0:
                        print(f"   🚨 Alertas detectadas: {len(respuesta_google.get('alertas', []))}")
                        for alerta in respuesta_google.get('alertas', []):
                            print(f"      ⚠️ {alerta.get('tipo', '')}: {alerta.get('impacto', '')}")
                    print(f"   🏗️ {respuesta_google.get('procesado_por', '')}")
                except Exception as e:
                    print(f"   📝 Respuesta raw: {response.text}")
                
                # Mostrar alertas locales también
                alertas = self.detectar_alertas_farmaceuticas(datos)
                for alerta in alertas:
                    if alerta["severidad"] == "CRITICA":
                        print(f"   🚨 ALERTA CRITICA: {alerta['tipo']}: {alerta['descripcion']}")
                        print(f"      🔍 Impacto: {alerta['impacto']}")
                    elif alerta["severidad"] == "ALTA":
                        print(f"   ⚠️ ALERTA ALTA: {alerta['tipo']}: {alerta['descripcion']}")
                        print(f"      🔍 Impacto: {alerta['impacto']}")
                
                # Formato térmico con emojis
                temp = datos["temperatura"]
                if temp > 8.0:
                    temp_status = "🔴"  # Fuera de rango
                elif temp < 2.0:
                    temp_status = "🔵"  # Muy frío
                else:
                    temp_status = "🟢"  # Correcto
                
                accel_status = "⚡" if datos["acelerometro_ejeZ"] > 3.0 else "📱"
                bateria_status = "🔋" if datos["bateria"] > 20 else "🪫"
                
                print(f"   {temp_status} {datos['temperatura']}°C | 💧 {datos['humedad']}% | {accel_status} {datos['acelerometro_ejeZ']}G | {bateria_status} {datos['bateria']}%")
                
                return True
                
            else:
                print(f"❌ [{timestamp}] Error HTTP {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            print(f"⏰ [{datetime.now().strftime('%H:%M:%S')}] Timeout - Endpoint no responde")
            return False
        except requests.exceptions.RequestException as e:
            print(f"📡 [{datetime.now().strftime('%H:%M:%S')}] Error conexión: {str(e)}")
            return False
        except Exception as e:
            print(f"💥 [{datetime.now().strftime('%H:%M:%S')}] Error inesperado: {str(e)}")
            return False
    
    def demo_rapida(self, duracion_segundos=30):
        """
        Demostración rápida del monitoreo farmacéutico
        
        Args:
            duracion_segundos (int): Duración de la demostración
        """
        print(f"🎬 MODO DEMOSTRACIÓN FARMACÉUTICA ACTIVADO")
        print(f"🚀 INICIANDO MONITOREO IoT FARMACÉUTICO")
        print(f"💊 Tipo de carga: MEDICAMENTOS (cadena de frío 2-8°C)")
        print(f"⏱️  Intervalo: 3 segundos")
        print(f"⏰ Duración: {duracion_segundos} segundos")
        print(f"🛑 Presiona Ctrl+C para detener")
        print("=" * 50)
        
        inicio = time.time()
        contador = 0
        exitosos = 0
        alertas_generadas = 0
        
        try:
            while (time.time() - inicio) < duracion_segundos:
                datos = self.generar_datos_sensor()
                alertas = self.detectar_alertas_farmaceuticas(datos)
                alertas_generadas += len(alertas)
                
                if self.enviar_datos(datos):
                    exitosos += 1
                
                contador += 1
                print()  # Línea en blanco para separar
                
                time.sleep(3)
                
        except KeyboardInterrupt:
            print(f"\n🛑 Monitoreo detenido por usuario")
        
        duracion_real = time.time() - inicio
        print(f"\n⏰ Monitoreo farmacéutico completado: {int(duracion_real)}s transcurridos")
        
        # Estadísticas finales
        print("\n" + "=" * 50)
        print("📊 ESTADÍSTICAS DEL MONITOREO FARMACÉUTICO")
        print("=" * 50)
        print(f"💊 Envío medicamentos monitoreado: {self.envio_id}")
        print(f"📡 Total de transmisiones: {contador}")
        print(f"✅ Transmisiones exitosas: {exitosos} ({(exitosos/contador*100):.1f}%)" if contador > 0 else "")
        print(f"🚨 Alertas farmacéuticas generadas: {alertas_generadas}")
        print(f"📍 Última ubicación: {self.latitud:.4f}, {self.longitud:.4f}")
        print(f"❄️  Rango temperatura objetivo: 2-8°C")
    
    def monitoreo_continuo(self):
        """
        Monitoreo continuo hasta que el usuario pare
        """
        print(f"🔄 MONITOREO CONTINUO FARMACÉUTICO")
        print(f"💊 Medicamentos: {self.envio_id}")
        print(f"❄️  Cadena de frío objetivo: 2-8°C")
        print(f"📡 Enviando cada 5 segundos")
        print(f"🛑 Presiona Ctrl+C para detener")
        print("=" * 50)
        
        contador = 0
        exitosos = 0
        
        try:
            while True:
                datos = self.generar_datos_sensor()
                
                if self.enviar_datos(datos):
                    exitosos += 1
                
                contador += 1
                print()
                
                time.sleep(5)
                
        except KeyboardInterrupt:
            print(f"\n🛑 Monitoreo detenido")
            print(f"📊 Total enviados: {contador}, Exitosos: {exitosos}")

def main():
    """Función principal del simulador"""
    print("✅ Usando librería requests")
    print("💊 GreenDelivery Pharmaceutical IoT Sensor Simulator v1.0")
    print("=" * 60)
    
    # Inicializar sensor
    sensor = GreenDeliveryPharmaIoTSensor(
        envio_id="GD-MEDS-2025-001",
        endpoint_url="https://greendelivery-ingesta-587952111457.europe-west1.run.app"
    )
    
    print("💊 Sensor IoT Farmacéutico inicializado")
    print(f"📦 Envío medicamentos: {sensor.envio_id}")
    print(f"📍 Ubicación inicial: {sensor.latitud:.4f}, {sensor.longitud:.4f}")
    print(f"🌐 Endpoint: {sensor.endpoint_url}")
    print()
    
    # Menú de opciones
    print("🎯 OPCIONES DE EJECUCIÓN:")
    print("1. Demostración rápida (30s) - Monitoreo farmacéutico")
    print("2. Monitoreo continuo - Cadena de frío medicamentos") 
    print("3. Generar solo un dato de prueba farmacéutica")
    print()
    
    try:
        opcion = input("Elige una opción (1-3): ").strip()
        
        if opcion == "1":
            sensor.demo_rapida(30)
            
        elif opcion == "2":
            sensor.monitoreo_continuo()
            
        elif opcion == "3":
            datos = sensor.generar_datos_sensor()
            print("\n📊 DATOS FARMACÉUTICOS DE EJEMPLO:")
            print(json.dumps(datos, indent=2, ensure_ascii=False))
            print(f"\n📤 Enviando a Google Cloud...")
            sensor.enviar_datos(datos)
            
        else:
            print("❌ Opción inválida")
            
    except KeyboardInterrupt:
        print(f"\n👋 Simulador terminado por usuario")
    except Exception as e:
        print(f"💥 Error inesperado: {e}")

if __name__ == "__main__":
    main()
