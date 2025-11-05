#  Capítulo 2  Arquitectura con Propósito

El propósito de esta arquitectura es **procesar y visualizar datos de dispositivos IoT**.  
Este capítulo describe cómo los datos viajan desde el sensor hasta el panel de control, mostrando una arquitectura simple, funcional y aplicable al proyecto **GreenDelivery**.

---

##  Diagrama de la Arquitectura
[Diagrama de Arquitectura](diagrama_cap2.png)

---

##  Componentes Principales

### **1. Edge  Simulador IoT / Mosquitto**
En esta capa, ejecutamos un **simulador IoT** que genera datos de telemetría (temperatura, fuerza-G, ubicación).  
Los dispositivos publican los datos en el **broker Mosquitto** mediante el protocolo **MQTT**, simulando las condiciones reales de transporte.

### **2. Broker MQTT (Mosquitto)**
Mosquitto actúa como **punto central de comunicación**.  
Recibe los mensajes de los sensores (topics) y los reenvía a los consumidores interesados.  
Es eficiente, ligero y ampliamente usado en sistemas IoT reales.

### **3. Flujo de Ingesta (Node-RED / n8n)**
El flujo de ingesta es responsable de **recibir, procesar y transformar** los datos.  
Usamos **Node-RED** (o n8n) porque permite construir flujos visuales que conectan el broker con la base de datos.  
Aquí también se aplican **reglas de detección de alertas**, transformaciones y limpieza de datos.

### **4. Almacenamiento  PostgreSQL**
Los datos procesados se guardan en una base de datos **PostgreSQL**, elegida por su **confiabilidad y potencia analítica**.  
Aquí se almacenan eventos, métricas y registros históricos para su análisis posterior.

### **5. Visualización  Dashboard**
Para el análisis y comunicación con el área de operaciones, se utiliza un dashboard creado en **Looker Studio** o **Grafana**, mostrando los **KPIs clave** (SLA, MTTD, Falsos Positivos).  
Esto conecta la parte técnica con la toma de decisiones del negocio.

---

##  Justificación Arquitectónica

| Componente | Tecnología | Motivo de Elección |
|-------------|-------------|--------------------|
| **Broker** | Mosquitto | Ligero, soporta MQTT y es ideal para entornos IoT |
| **Flujo ETL** | Node-RED / n8n | Facilita la orquestación visual y el mantenimiento |
| **Base de Datos** | PostgreSQL | Robusto, open-source y compatible con analítica |
| **Dashboard** | Looker Studio / Grafana | Permite visualización dinámica de KPIs |
| **Edge** | Python (Simulador IoT) | Flexible para generar datos de prueba realistas |

---

##  Conclusión
El diseño final integra **fluidez, modularidad y trazabilidad de extremo a extremo**.  
Cada capa cumple un rol funcional, permitiendo que los datos fluyan desde la simulación hasta los indicadores de negocio de forma transparente y medible.

---

 *Actualizado: Noviembre 2025*  
 *Proyecto: GreenDelivery  Any2Cloud Team*
