from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'secret'  # Necesario para mostrar mensajes flash

UPLOAD_FOLDER = os.path.join('static', 'videos')
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Verifica que el archivo tenga una extensión válida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'video' not in request.files:
            flash('No se envió ningún archivo')
            return redirect(request.url)

        file = request.files['video']
        if file.filename == '':
            flash('Nombre de archivo vacío')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            flash('Video subido exitosamente')
            return redirect(url_for('index'))

    videos = os.listdir(UPLOAD_FOLDER)
    return render_template('index.html', videos=videos)

@app.route('/video/<filename>')
def video(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
