import pandas as pd
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score
import sys

# --- 1. DEFINE TU LÓGICA (La misma que en Node-RED) ---
# En el Paso 1 (Cap 3) elegimos N=3.
# En el Paso 2 (Cap 3) elegimos que la métrica clave es RECALL.
N_CONSECUTIVOS = 3
MAX_TEMP = 8.0
MAX_G_FORCE = 2.5

print(f"--- Iniciando Evaluación (N={N_CONSECUTIVOS}) ---")

def simular_logica_nodered(df):
    """
    Esta función simula tu flujo de Node-RED.
    Lee el dataframe fila por fila y aplica la lógica de "memoria".
    """
    
    # y_pred (Predicción) = La lista de alertas que NUESTRA regla genera.
    y_pred = [] 
    
    # "packageState" es la "memoria" (flow.context) que usamos en Node-RED.
    packageState = {} 

    print("Simulando lógica de Node-RED sobre los datos...")
    
    # Iteramos por cada fila (cada evento) del CSV
    for row in df.itertuples():
        
        # Leemos los datos de las columnas del CSV
        package_id = row.parcel_id
        temp = row.temp
        g_force = row.g_force
        
        is_alert = False # Por defecto, este evento no es una alerta

        # Inicializa la memoria para este paquete si es la primera vez que lo vemos
        if package_id not in packageState:
            packageState[package_id] = {
                'consecutiveTempAlerts': 0,
                'consecutiveForceAlerts': 0
            }
        
        # 1. APLICAR LA REGLA DE NEGOCIO (Igual que en Node-RED)
        if temp > MAX_TEMP or g_force > MAX_G_FORCE:
            # Si hay anomalía, incrementamos contadores
            if temp > MAX_TEMP:
                packageState[package_id]['consecutiveTempAlerts'] += 1
            if g_force > MAX_G_FORCE:
                packageState[package_id]['consecutiveForceAlerts'] += 1
        else:
            # Si el dato es NORMAL, reseteamos los contadores a 0
            packageState[package_id]['consecutiveTempAlerts'] = 0
            packageState[package_id]['consecutiveForceAlerts'] = 0

        # 2. DECIDIR SI ES UNA ALERTA (N=3)
        if (packageState[package_id]['consecutiveTempAlerts'] >= N_CONSECUTIVOS or
            packageState[package_id]['consecutiveForceAlerts'] >= N_CONSECUTIVOS):
            
            is_alert = True # ¡ALERTA!
            
            # Reseteamos contadores para no disparar 100 alertas seguidas
            packageState[package_id]['consecutiveTempAlerts'] = 0
            packageState[package_id]['consecutiveForceAlerts'] = 0
        
        # Añadimos nuestra predicción (True o False) a la lista
        y_pred.append(is_alert)
    
    print("Simulación completada.")
    return y_pred

# --- 2. CARGAR Y PREPARAR LOS DATOS ---
FILE_PATH = "analytics/labels.csv"
print(f"Cargando el fichero '{FILE_PATH}'...")

try:
    df = pd.read_csv(FILE_PATH)
except FileNotFoundError:
    print(f"--- ¡ERROR! ---")
    print(f"No se encontró el archivo en '{FILE_PATH}'.")
    print("Asegúrate de que la carpeta 'analytics' está en el mismo lugar que 'evaluacion.py'")
    sys.exit() # Detiene el script

# ¡Muy importante! Ordenamos los datos por paquete y luego por tiempo.
# La lógica de "N consecutivos" depende 100% de que los datos estén ordenados.
df = df.sort_values(by=['parcel_id', 'ts_utc'])

# --- 3. COMPARAR: VERDAD vs. PREDICCIÓN ---

# y_true (Verdad) = Las etiquetas reales del "examen" (el CSV).
# Convertimos 'NORMAL' a False y 'ALERT' a True.
y_true = (df['label'] == 'ALERT').values 

# y_pred (Predicción) = Las alertas que genera NUESTRA lógica
y_pred = simular_logica_nodered(df)

print("Calculando métricas de rendimiento...")

# --- 4. CALCULAR MÉTRICAS Y MATRIZ DE CONFUSIÓN ---

print("\n" + "="*30)
print("  ¡PRUEBA DE FUEGO COMPLETADA!")
print("="*30 + "\n")

# Matriz de Confusión
# tn = Verdadero Negativo (Bien: era normal, dijimos normal)
# fp = Falso Positivo (Mal: era normal, dijimos alerta) <- Opción A
# fn = Falso Negativo (Mal: era alerta, dijimos normal) <- Opción B
# tp = Verdadero Positivo (Bien: era alerta, dijimos alerta)
tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[False, True]).ravel()

print("--- Matriz de Confusión ---")
print(f"                 Predijimos 'Normal' | Predijimos 'Alerta'")
print(f"Realidad 'Normal' |    {tn:<17} (VN) |    {fp:<16} (FP) <-- ¡Opción A!")
print(f"Realidad 'Alerta' |    {fn:<17} (FN) <-- ¡Opción B! |    {tp:<16} (VP)")
print("-"*30)


# Métricas
precision = precision_score(y_true, y_pred, zero_division=0)
recall = recall_score(y_true, y_pred, zero_division=0)
f1 = f1_score(y_true, y_pred, zero_division=0)

print("--- Métricas de Rendimiento (con N=3) ---")
print(f"Precisión (Precision): {precision:.2%}")
print(f"Exhaustividad (Recall): {recall:.2%}")
print(f"Puntuación F1 (F1-Score): {f1:.2%}")
print("-"*30)

print(f"\nANÁLISIS (según Paso 2):")
print(f"Tu objetivo era minimizar los Falsos Negativos (Opción B), por eso elegiste RECALL.")
print(f"RESULTADO: Tu lógica tiene un RECALL del {recall:.2%}.")