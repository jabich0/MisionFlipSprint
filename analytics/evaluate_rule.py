import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix

df = pd.read_csv('analytics/labels.csv', parse_dates=['ts'])
y_true = df['is_incident'].astype(int)
y_pred = df['is_incident'].astype(int)  # TODO: reemplazar por tu lógica
print('precision', precision_score(y_true, y_pred, zero_division=0))
print('recall   ', recall_score(y_true, y_pred, zero_division=0))
print('f1       ', f1_score(y_true, y_pred, zero_division=0))
print('cm:\n', confusion_matrix(y_true, y_pred))
