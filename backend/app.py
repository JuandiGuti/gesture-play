from flask import Flask, jsonify
from flask_cors import CORS
from model import detectar_gesto

app = Flask(__name__)
CORS(app)

@app.route("/get_gesto")
def get_gesto():
    return jsonify({"gesto": detectar_gesto()})

if __name__ == "__main__":
    app.run(port=5000, debug=True)
