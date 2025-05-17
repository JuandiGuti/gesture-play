import os
import cv2
import numpy as np
import mediapipe as mp
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

# Configuraciones
DATASET_PATH = "backend/asl_alphabet_train"
LETRAS_USADAS = ["A", "B", "D", "P", "U"]
MAX_IMGS_POR_CLASE = 300
MODEL_OUT_PATH = "backend/modelo_svm.pkl"
LABELS_OUT_PATH = "backend/labels.pkl"

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils

def extraer_landmarks(imagen):
    img_rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
    resultado = hands.process(img_rgb)

    if resultado.multi_hand_landmarks:
        landmarks = resultado.multi_hand_landmarks[0]
        puntos = []
        for lm in landmarks.landmark:
            puntos.extend([lm.x, lm.y, lm.z])
        return puntos
    return None

def cargar_datos():
    X = []
    y = []

    for letra in LETRAS_USADAS:
        ruta_clase = os.path.join(DATASET_PATH, letra)
        imagenes = os.listdir(ruta_clase)[:MAX_IMGS_POR_CLASE]

        for img_nombre in imagenes:
            img_path = os.path.join(ruta_clase, img_nombre)
            imagen = cv2.imread(img_path)

            if imagen is None:
                continue

            puntos = extraer_landmarks(imagen)
            if puntos:
                X.append(puntos)
                y.append(letra)

    return np.array(X), np.array(y)

def entrenar_modelo():
    print("[INFO] Cargando datos...")
    X, y = cargar_datos()
    print(f"[INFO] Total muestras: {len(X)}")

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

    print("[INFO] Entrenando SVM...")
    modelo = SVC(kernel='rbf', C=10, gamma='scale', probability=True)
    modelo.fit(X_train, y_train)

    print("[INFO] Evaluando modelo...")
    y_pred = modelo.predict(X_test)
    reporte = classification_report(y_test, y_pred, target_names=label_encoder.classes_)
    print(reporte)

    joblib.dump(modelo, MODEL_OUT_PATH)
    joblib.dump(label_encoder, LABELS_OUT_PATH)
    print(f"[INFO] Modelo guardado en: {MODEL_OUT_PATH}")
    print(f"[INFO] Etiquetas guardadas en: {LABELS_OUT_PATH}")

    return "Entrenamiento finalizado"

# Para usar desde Flask
if __name__ == "__main__":
    entrenar_modelo()
