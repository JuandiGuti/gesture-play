# Gesture-Play: Control Multimedia por Gestos con ASL

## Descripción del Proyecto

Este proyecto tiene como objetivo implementar un sistema de reconocimiento de gestos utilizando visión por computadora y aprendizaje automático. El sistema es capaz de identificar ciertas letras del alfabeto en lengua de señas americana (ASL) y utilizar estos gestos para controlar la reproducción de videos en una interfaz web.

## Tecnologías Utilizadas

* **Python 3.10** (requerido por MediaPipe)
* **Flask** para el backend
* **MediaPipe** para la detección de manos y extracción de puntos
* **OpenCV** para procesamiento de imágenes
* **Scikit-learn** para entrenamiento de modelos SVM
* **HTML/CSS/JS** para el frontend
* **YouTube IFrame API** para el reproductor

## Estructura del Proyecto

```
/
├── app.py                # Servidor Flask principal
├── model_train.py        # Entrenamiento del modelo SVM
├── model.py              # Lógica de predicción con MediaPipe
├── templates/
│   ├── index.html        # Interfaz principal
│   └── config.html       # Panel de configuración
├── static/
│   ├── style.css         # Estilos globales
│   └── src/main.js       # Lógica frontend
├── modelo_svm.pkl        # Modelo entrenado (se genera)
├── labels.pkl            # Etiquetas del modelo (se genera)
└── asl_alphabet_train/   # Dataset de entrenamiento (no incluido)
```

## Instrucciones de Ejecución

1. Instalar Python 3.10
2. Crear un entorno virtual:

```bash
python3.10 -m venv venv
```

3. Activar el entorno virtual:

* Windows:

```bash
venv\Scripts\activate
```

* Mac/Linux:

```bash
source venv/bin/activate
```

4. Instalar dependencias:

```bash
pip install -r requirements.txt
```

5. Ejecutar el backend:

```bash
python app.py
```

6. Acceder desde el navegador a:

```
http://localhost:8000
```

## Entrenamiento del Modelo

Desde la pestaña "Configuración" en la interfaz web:

* Presiona **"Entrenar Modelo"** para procesar el dataset y generar `modelo_svm.pkl` y `labels.pkl`
* El entrenamiento se ejecuta en segundo plano (gracias a hilos)

> Nota: se utiliza MediaPipe, por lo que se requiere buena iluminación y gestos claros para una detección confiable.

## Gestos Reconocidos

| Letra | Acción                  | Significado |
| ----- | ----------------------- | ----------- |
| **P** | Pausar / Reanudar video | Pause       |
| **U** | Subir volumen           | Up          |
| **D** | Bajar volumen           | Down        |
| **B** | Retroceder 10 segundos  | Before      |
| **A** | Avanzar 10 segundos     | After       |

## Notas Técnicas

* **Evita cerrar el CMD** inesperadamente: se usa `threading` para evitar que el servidor Flask se reinicie tras guardar archivos.
* **Modo solo reproductor:** disponible desde la página de configuración (toggle en localStorage).
* **Expansible:** se puede entrenar con más letras simplemente agregando nuevas carpetas al dataset y volviendo a entrenar.

---

Para cualquier duda técnica, revisar los comentarios en los scripts `model.py` y `main.js`.
