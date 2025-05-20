import os
import cv2
import numpy as np
import mediapipe as mp
import base64

MODELO_PATH = "modelo_svm.pkl"
LABELS_PATH = "labels.pkl"

# Inicializar MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils

# Cargar modelo
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
    imagen = cv2.resize(imagen, (224, 224))
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    mejorado = clahe.apply(gris)
    imagen_final = cv2.cvtColor(mejorado, cv2.COLOR_GRAY2BGR)

    img_rgb = cv2.cvtColor(imagen_final, cv2.COLOR_BGR2RGB)
    resultado = hands.process(img_rgb)

    if resultado.multi_hand_landmarks:
        landmarks = resultado.multi_hand_landmarks[0]
        puntos = []
        for lm in landmarks.landmark:
            puntos.extend([lm.x, lm.y, lm.z])
        return np.array(puntos).reshape(1, -1), resultado
    return None, None

def predecir_desde_cv2(imagen):
    if modelo is None or label_encoder is None:
        return {
            "error": "El modelo aún no ha sido entrenado. Por favor, accede a /entrenar_modelo primero."
        }

    puntos, resultado = procesar_imagen_opencv(imagen)
    if puntos is None:
        return {"error": "No se detectó ninguna mano en la imagen."}

    # Debug: ver los valores del vector
    print("[DEBUG] Primeros valores del vector:", puntos[0][:10])
    print("[DEBUG] Magnitud total del vector:", np.linalg.norm(puntos))

    # Clasificación
    pred = modelo.predict(puntos)[0]
    proba = modelo.predict_proba(puntos)[0]
    etiqueta = label_encoder.inverse_transform([pred])[0]
    confianza = np.max(proba)

    # Dibujar puntos sobre la imagen original
    imagen_resultado = imagen.copy()
    if resultado and resultado.multi_hand_landmarks:
        mp_drawing.draw_landmarks(imagen_resultado, resultado.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS)

    _, buffer = cv2.imencode('.jpg', imagen_resultado)
    img_base64 = base64.b64encode(buffer).decode('utf-8')

    return {
        "prediccion": etiqueta,
        "confianza": float(confianza),
        "explicacion": f"Letra {etiqueta} con {confianza:.2%} de certeza.",
        "imagen_procesada": img_base64
    }
