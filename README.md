# Capítulo 3: De Dato a Decisión - Informe de Resultados

Este informe documenta la implementación y evaluación de la lógica de detección de incidentes para GreenDelivery.

## 1. La Lógica Implementada (Paso 1)

* **Lógica:** Se implementó una lógica "stateful" (con memoria) en el flujo de Node-RED (ver `flows.json`).
* **Elección de N:** Elegimos **N=3** eventos consecutivos.
* **Justificación:** Un solo evento (`N=1`) puede ser un bache (Falso Positivo). Pero 3 eventos seguidos (6 segundos) de anomalía indican un problema sostenido que requiere intervención.

## 2. La Métrica de Negocio (Paso 2)

* **Métrica Elegida:** **Exhaustividad (Recall)**.
* **Justificación:** Se determinó que un **Falso Negativo** (no detectar un incidente real) es **catastrófico** (pérdida de miles de euros). Un **Falso Positivo** (falsa alarma) es un coste menor. Por lo tanto, el sistema debe priorizar "atrapar" todos los incidentes reales.

## 3. Los Resultados Cuantificados (Paso 3)

Se ejecutó el script `evaluacion.py` contra el "examen" (`analytics/labels.csv`) para probar nuestra lógica de N=3.

* **Matriz de Confusión:**

    | | Predijimos 'Normal' | Predijimos 'Alerta' |
    | :--- | :---: | :---: |
    | **Realidad 'Normal'** | 188 (VN) | 0 (FP) |
    | **Realidad 'Alerta'** | 16 (FN) | 6 (VP) |

* **Métricas de Rendimiento:**

    * **Precisión (Precision): 100.00%**
    * **Exhaustividad (Recall): 27.27%**
    * **Puntuación F1 (F1-Score): 42.86%**

## 4. Conclusión

Nuestro Recall (la métrica clave que elegimos) es del **27.27%**. Este resultado es bajo y **no cumple** el objetivo de negocio, que era priorizar "atrapar" todos los incidentes reales.

Nuestra lógica de `N=3` es **demasiado estricta**. Ha conseguido una Precisión perfecta del 100% (cero Falsos Positivos), pero a costa de "dejar pasar" 16 incidentes reales (Falsos Negativos).

**Siguiente Paso (Mejora):** para mejorar este Recall, deberíamos hacer nuestra regla más sensible, por ejemplo, bajando el contador a **N=2** (o incluso N=1), y volver a medir. Esto aumentaría el Recall, aunque probablemente bajaría la Precisión (aceptaríamos más Falsos Positivos a cambio de no perder incidentes reales).