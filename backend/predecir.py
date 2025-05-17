import cv2
import numpy as np
import mediapipe as mp
import joblib

# Inicializar MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1)

# Cargar modelo y etiquetas
modelo = joblib.load("backend/modelo_svm.pkl")
label_encoder = joblib.load("backend/labels.pkl")

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
    puntos = procesar_imagen_opencv(imagen)
    if puntos is None:
        return {"error": "No se detectó ninguna mano en la imagen."}

    pred = modelo.predict(puntos)[0]
    proba = modelo.predict_proba(puntos)[0]
    etiqueta = label_encoder.inverse_transform([pred])[0]
    confianza = np.max(proba)

    explicacion = (
        f"Se detectaron {len(puntos[0]) // 3} puntos clave (x, y, z) usando MediaPipe.\n"
        f"Estos landmarks fueron ingresados al modelo SVM previamente entrenado.\n"
        f"El modelo predijo la letra **{etiqueta}** con una confianza del {confianza:.2%}."
    )

    return {
        "prediccion": etiqueta,
        "confianza": float(confianza),
        "explicacion": explicacion
    }
