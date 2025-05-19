import os
import cv2
import numpy as np
import mediapipe as mp
import matplotlib.pyplot as plt
import seaborn as sns
import json

from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import StratifiedKFold

DATASET_PATH = "asl_alphabet_train"
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1)


def extraer_landmarks(imagen):
    try:
        imagen = cv2.resize(imagen, (224, 224))
        gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        mejorado = clahe.apply(gris)
        imagen_final = cv2.cvtColor(mejorado, cv2.COLOR_GRAY2BGR)

        img_rgb = cv2.cvtColor(imagen_final, cv2.COLOR_BGR2RGB)
        resultado = hands.process(img_rgb)

        if resultado and resultado.multi_hand_landmarks:
            puntos = []
            for lm in resultado.multi_hand_landmarks[0].landmark:
                puntos.extend([lm.x, lm.y, lm.z])
            return puntos
    except:
        pass
    return None


def cargar_datos():
    X, y = [], []
    for letra in sorted(os.listdir(DATASET_PATH)):
        ruta_clase = os.path.join(DATASET_PATH, letra)
        if not os.path.isdir(ruta_clase):
            continue
        for img_nombre in os.listdir(ruta_clase):
            img_path = os.path.join(ruta_clase, img_nombre)
            imagen = cv2.imread(img_path)
            if imagen is None:
                continue
            puntos = extraer_landmarks(imagen)
            if puntos:
                X.append(puntos)
                y.append(letra)
    return np.array(X), np.array(y)


def evaluar_kfold(k=5):
    print("[INFO] Cargando datos...")
    X, y = cargar_datos()
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    skf = StratifiedKFold(n_splits=k, shuffle=True, random_state=42)

    precisiones, recalls, f1s = [], [], []
    matriz_total = np.zeros((len(le.classes_), len(le.classes_)))
    metricas_por_clase = np.zeros((len(le.classes_), 3))  # P, R, F1

    for fold, (train_idx, test_idx) in enumerate(skf.split(X, y_encoded), 1):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y_encoded[train_idx], y_encoded[test_idx]

        modelo = SVC(kernel='rbf', C=10, gamma='scale')
        modelo.fit(X_train, y_train)

        y_pred = modelo.predict(X_test)

        p, r, f, _ = precision_recall_fscore_support(y_test, y_pred, average='macro', zero_division=0)
        precisiones.append(p)
        recalls.append(r)
        f1s.append(f)

        cm = confusion_matrix(y_test, y_pred, labels=range(len(le.classes_)))
        matriz_total += cm

        clase_p, clase_r, clase_f, _ = precision_recall_fscore_support(y_test, y_pred, labels=range(len(le.classes_)), zero_division=0)
        metricas_por_clase += np.stack([clase_p, clase_r, clase_f], axis=1)

        print(f"Fold {fold}: Precision={p:.3f}, Recall={r:.3f}, F1={f:.3f}")

    prom = {
        "precision": round(np.mean(precisiones), 3),
        "recall": round(np.mean(recalls), 3),
        "f1_score": round(np.mean(f1s), 3),
        "folds": k
    }
    print("\nPromedios:", prom)

    with open("resultados_kfold.json", "w") as f:
        json.dump(prom, f, indent=4)

    matriz_total /= k
    plt.figure(figsize=(10, 8))
    sns.heatmap(matriz_total, xticklabels=le.classes_, yticklabels=le.classes_, annot=True, fmt=".0f", cmap="Blues")
    plt.title("Matriz de Confusión Promediada (K-Fold)")
    plt.xlabel("Predicho")
    plt.ylabel("Real")
    plt.tight_layout()
    plt.savefig("conf_matrix_avg.png")

    # Métricas por clase
    metricas_prom = metricas_por_clase / k
    etiquetas = le.classes_
    plt.figure(figsize=(10, 6))
    ancho = 0.25
    x = np.arange(len(etiquetas))
    plt.bar(x - ancho, metricas_prom[:, 0], width=ancho, label='Precisión')
    plt.bar(x,         metricas_prom[:, 1], width=ancho, label='Recall')
    plt.bar(x + ancho, metricas_prom[:, 2], width=ancho, label='F1-Score')
    plt.xticks(x, etiquetas)
    plt.ylabel("Valor")
    plt.title("Métricas por clase (promedio K-Fold)")
    plt.legend()
    plt.tight_layout()
    plt.savefig("metricas_clases.png")
    print("[INFO] Resultados guardados como resultados_kfold.json, conf_matrix_avg.png y metricas_clases.png")


if __name__ == "__main__":
    evaluar_kfold(k=5)
