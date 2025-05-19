from flask import Flask, jsonify, request
from flask_cors import CORS
from model_train import entrenar_modelo
from model import predecir_desde_cv2
import numpy as np
import cv2

app = Flask(__name__)
CORS(app)

@app.route('/entrenar_modelo')
def entrenar():
    resultado = entrenar_modelo()
    return jsonify({"mensaje": resultado})

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
