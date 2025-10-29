import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS  # Importar CORS
from datetime import datetime

# --- CONFIGURACIÓN ---
app = Flask(__name__)
# Habilitar CORS para permitir peticiones desde cualquier origen (*)
# Esto es VITAL para que GitHub Pages pueda hablar con PythonAnywhere
CORS(app)

# --- BASE DE DATOS (SQLite local) ---
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'project.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# ------------------------

# --- MODELO DE LA DB ---
# Definimos una tabla simple para guardar solo la puntuación MOS
class Response(db.Model):
    __tablename__ = 'responses'
    id = db.Column(db.Integer, primary_key=True)
    mos_score = db.Column(db.Integer, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<Response {self.id}: MOS={self.mos_score}>'
# ---------------------

# --- RUTAS DE LA API ---

@app.route('/')
def home():
    """Ruta simple para verificar que la API está funcionando."""
    return "API de Encuesta QoE está en línea. Use la ruta /submit para enviar datos."

@app.route('/submit', methods=['POST'])
def submit_response():
    """Recibe la puntuación MOS en JSON y la guarda en la DB."""
    try:
        data = request.json
        
        if 'mos' not in data:
            return jsonify({"success": False, "error": "Falta el valor 'mos'"}), 400

        mos_score = int(data.get('mos'))
        
        # Validar que el score esté en el rango
        if not (1 <= mos_score <= 5):
            return jsonify({"success": False, "error": "Valor MOS fuera de rango"}), 400

        new_response = Response(mos_score=mos_score)
        db.session.add(new_response)
        db.session.commit()

        return jsonify({"success": True, "message": "Respuesta guardada"}), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error en /submit: {e}") # Para el log de errores de PythonAnywhere
        return jsonify({"success": False, "error": str(e)}), 500

# Función para crear la base de datos y la tabla si no existen
def create_db_tables():
    with app.app_context():
        print("Creando tablas de la base de datos si no existen...")
        db.create_all()
        print("Tablas listas.")

# --- INICIO ---
# Llama a la función para crear las tablas al iniciar la app.
create_db_tables()

if __name__ == '__main__':
    # Esto no se usa en PythonAnywhere, pero es útil para pruebas locales
    app.run(debug=True)

