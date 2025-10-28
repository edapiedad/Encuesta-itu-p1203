import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import atexit

# --- CONFIGURACIÓN DE LA BASE DE DATOS (SQLite) ---
# Esto es mucho más simple. Usará un archivo llamado 'project.db'
# que se creará en tu directorio de PythonAnywhere.
app = Flask(__name__)
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'project.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# -------------------------------------------------

# Definición del Modelo de la Base de Datos (la tabla)
class Response(db.Model):
    __tablename__ = 'responses'
    id = db.Column(db.Integer, primary_key=True)
    mos_score = db.Column(db.Integer, nullable=False)
    # Cambiado a datetime.now para compatibilidad con SQLite
    submitted_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<Response {self.id}: MOS={self.mos_score}>'

@app.route('/')
def index():
    """Sirve la página principal de la encuesta."""
    try:
        return render_template('survey.html')
    except Exception as e:
        return f"Error al cargar la plantilla: {e}", 500

@app.route('/submit', methods=['POST'])
def submit_response():
    """Recibe los datos del formulario (vía JSON) y los guarda en la DB."""
    try:
        # Recibimos datos JSON del fetch() de JavaScript
        data = request.json
        
        if 'mos' not in data:
            return jsonify({"success": False, "error": "Falta el valor 'mos'"}), 400

        # Obtenemos la puntuación
        mos_score = int(data.get('mos'))

        # Creamos una nueva entrada para la base de datos
        new_response = Response(mos_score=mos_score)

        # Añadimos y guardamos en la base de datos
        db.session.add(new_response)
        db.session.commit()

        # Enviamos una respuesta exitosa al frontend
        return jsonify({"success": True, "message": "Respuesta guardada"}), 201

    except Exception as e:
        db.session.rollback() # Revertir cambios si hay un error
        print(f"Error en /submit: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# Función para crear la base de datos y la tabla si no existen
def create_db_tables():
    with app.app_context():
        print("Creando tablas de la base de datos si no existen...")
        db.create_all()
        print("Tablas listas.")

# --- Creación de la DB ---
# Llama a la función para crear las tablas al iniciar la app.
# El archivo WSGI también llamará a esto para asegurarse.
create_db_tables()

if __name__ == '__main__':
    # Esto es solo para pruebas locales, PythonAnywhere usa un servidor WSGI
    app.run(debug=True)

