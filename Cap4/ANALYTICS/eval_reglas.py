#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix

"""
Expected CSV schema (labels.csv):
id_envio, timestamp, temperatura, acelerometro_ejeZ, etiqueta_incidente (0/1)

Regla evaluada:
- Alerta si temperatura > 8.0 o acelerometro_ejeZ > 2.5G sostenido por N eventos consecutivos
- N es configurable
"""

def detectar_alertas_stateful(df, n_consecutivos=3, umbral_temp=8.0, umbral_g=2.5):
    df = df.sort_values(["id_envio", "timestamp"]).copy()
    df["pred_alerta"] = 0
    cont_g = {}
    cont_t = {}
    rows = []
    for row in df.itertuples(index=False):
        envio = row.id_envio
        g = float(getattr(row, "acelerometro_ejeZ"))
        temp = float(getattr(row, "temperatura"))
        cont_g[envio] = cont_g.get(envio, 0) + 1 if g > umbral_g else 0
        cont_t[envio] = cont_t.get(envio, 0) + 1 if temp > umbral_temp else 0
        pred = 1 if (cont_g[envio] >= n_consecutivos or cont_t[envio] >= n_consecutivos) else 0
        rows.append(pred)
    df["pred_alerta"] = rows
    return df

def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--csv", default="labels.csv")
    p.add_argument("--n", type=int, default=3)
    p.add_argument("--umbral-temp", type=float, default=8.0)
    p.add_argument("--umbral-g", type=float, default=2.5)
    args = p.parse_args()

    df = pd.read_csv(args.csv)
    if "etiqueta_incidente" not in df.columns:
        raise SystemExit("labels.csv debe contener la columna 'etiqueta_incidente' (0/1)." )

    df_eval = detectar_alertas_stateful(df, n_consecutivos=args.n,
                                        umbral_temp=args.umbral_temp,
                                        umbral_g=args.umbral_g)
    y_true = df_eval["etiqueta_incidente"].astype(int).values
    y_pred = df_eval["pred_alerta"].astype(int).values

    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    cm = confusion_matrix(y_true, y_pred)

    print("Resultados evaluación regla stateful")
    print(f"N consecutivos = {args.n}, umbral_temp = {args.umbral_temp}, umbral_g = {args.umbral_g}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1-score:  {f1:.4f}")
    print("Matriz de confusión [ [TN FP] [FN TP] ]:")
    print(cm)

    out = {
        "n_consecutivos": args.n,
        "umbral_temp": args.umbral_temp,
        "umbral_g": args.umbral_g,
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "confusion_matrix": cm.tolist()
    }
    with open("resultado_eval.json", "w", encoding="utf-8") as f:
        import json
        json.dump(out, f, indent=2, ensure_ascii=False)
    print("\nResumen guardado en resultado_eval.json")

if __name__ == "__main__":
    main()
