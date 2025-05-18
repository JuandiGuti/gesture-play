import os
import cv2
import numpy as np
import mediapipe as mp

MODELO_PATH = "modelo_svm.pkl"
LABELS_PATH = "labels.pkl"

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1)

modelo = None
label_encoder = None

try:
    import joblib
    if os.path.exists(MODELO_PATH) and os.path.exists(LABELS_PATH):
        modelo = joblib.load(MODELO_PATH)
        label_encoder = joblib.load(LABELS_PATH)
        print("[INFO] Modelo y etiquetas cargados correctamente.")
    else:
        print("[ADVERTENCIA] El modelo o las etiquetas aún no existen. Ejecuta /entrenar_modelo.")
except Exception as e:
    print(f"[ERROR] Fallo al cargar el modelo: {e}")

def procesar_imagen_opencv(imagen):
    img_rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
    resultado = hands.process(img_rgb)

    if resultado.multi_hand_landmarks:
        landmarks = resultado.multi_hand_landmarks[0]
        puntos = []
        for lm in landmarks.landmark:
            puntos.extend([lm.x, lm.y, lm.z])
        return np.array(puntos).reshape(1, -1)
    return None

def predecir_desde_cv2(imagen):
    if modelo is None or label_encoder is None:
        return {
            "error": "El modelo aún no ha sido entrenado. Por favor, accede a /entrenar_modelo primero."
        }

    puntos = procesar_imagen_opencv(imagen)
    if puntos is None:
        return {
            "error": "No se detectó ninguna mano en la imagen."
        }

    pred = modelo.predict(puntos)[0]
    proba = modelo.predict_proba(puntos)[0]
    etiqueta = label_encoder.inverse_transform([pred])[0]
    confianza = np.max(proba)

    explicacion = (
        f"Se detectaron {len(puntos[0]) // 3} puntos clave (x, y, z) usando MediaPipe.\n"
        f"Estos landmarks fueron usados como entrada del modelo SVM previamente entrenado.\n"
        f"Resultado: letra **{etiqueta}** con confianza del {confianza:.2%}."
    )

    return {
        "prediccion": etiqueta,
        "confianza": float(confianza),
        "explicacion": explicacion
    }
