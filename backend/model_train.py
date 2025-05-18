import os
import cv2
import numpy as np
import mediapipe as mp
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

DATASET_PATH = "asl_alphabet_train"
LETRAS_USADAS = ["A", "B", "D", "P", "U"]
MAX_IMGS_POR_CLASE = 300
MODEL_OUT_PATH = "modelo_svm.pkl"
LABELS_OUT_PATH = "labels.pkl"

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1)

def extraer_landmarks(imagen):
    try:
        # Redimensionar
        imagen = cv2.resize(imagen, (224, 224))

        # Escala de grises
        gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

        # CLAHE suave para mejorar contraste sin distorsionar
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        mejorado = clahe.apply(gris)

        # Convertir a 3 canales para MediaPipe
        imagen_final = cv2.cvtColor(mejorado, cv2.COLOR_GRAY2BGR)

        # Detección con MediaPipe
        img_rgb = cv2.cvtColor(imagen_final, cv2.COLOR_BGR2RGB)
        resultado = hands.process(img_rgb)

        if resultado and resultado.multi_hand_landmarks:
            puntos = []
            for lm in resultado.multi_hand_landmarks[0].landmark:
                puntos.extend([lm.x, lm.y, lm.z])
            return puntos
    except Exception as e:
        print("[ERROR preprocesamiento]:", e)

    return None

def cargar_datos():
    X = []
    y = []

    for letra in LETRAS_USADAS:
        ruta_clase = os.path.join(DATASET_PATH, letra)
        imagenes = os.listdir(ruta_clase)[:MAX_IMGS_POR_CLASE]
        contador_ok = 0

        for img_nombre in imagenes:
            img_path = os.path.join(ruta_clase, img_nombre)
            imagen = cv2.imread(img_path)
            if imagen is None:
                continue

            puntos = extraer_landmarks(imagen)
            if puntos:
                X.append(puntos)
                y.append(letra)
                contador_ok += 1

        print(f"[INFO] Clase '{letra}': {contador_ok} imágenes válidas")

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
    reporte = classification_report(
    y_test,
    y_pred,
    labels=label_encoder.transform(label_encoder.classes_),
    target_names=label_encoder.classes_,
    zero_division=0
)
    print(reporte)

    joblib.dump(modelo, MODEL_OUT_PATH)
    joblib.dump(label_encoder, LABELS_OUT_PATH)
    print(f"[INFO] Modelo guardado en: {MODEL_OUT_PATH}")
    print(f"[INFO] Etiquetas guardadas en: {LABELS_OUT_PATH}")

    return "Entrenamiento finalizado"
