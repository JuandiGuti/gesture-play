from flask import Flask, jsonify, request
from flask_cors import CORS
from model_train import entrenar_modelo
from model import predecir_desde_cv2
import numpy as np
import cv2
import threading

app = Flask(__name__)
CORS(app)

@app.route('/entrenar_modelo')
def entrenar():
    def ejecutar_entrenamiento():
        entrenar_modelo()
    threading.Thread(target=ejecutar_entrenamiento).start()
    return jsonify({"mensaje": "Entrenamiento iniciado en segundo plano"})

@app.route('/predecir', methods=['POST'])
def predecir():
    if 'imagen' not in request.files:
        return jsonify({"error": "No se encontró ninguna imagen."}), 400

    archivo = request.files['imagen']
    file_bytes = np.frombuffer(archivo.read(), np.uint8)
    imagen = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    resultado = predecir_desde_cv2(imagen)
    return jsonify(resultado)

if __name__ == '__main__':
    app.run(debug=True)
