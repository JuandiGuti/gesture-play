from flask import Flask, jsonify
from flask_cors import CORS
from model import detectar_gesto
from model_train import entrenar_modelo
from flask import request
from model import predecir_desde_cv2
import cv2
import numpy as np

app = Flask(__name__)
CORS(app)

@app.route("/get_gesto")
def get_gesto():
    return jsonify({"gesto": detectar_gesto()})

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

if __name__ == "__main__":
    app.run(port=5000, debug=True)
