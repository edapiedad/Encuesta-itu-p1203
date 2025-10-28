import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
# ¡REEMPLAZA ESTO CON TUS CREDENCIALES DE PYTHONANYWHERE MYSQL!
DB_USERNAME = 'TU_USUARIO_AQUI'
DB_PASSWORD = 'TU_PASSWORD_MYSQL_AQUI'
DB_HOSTNAME = 'TU_HOSTNAME_MYSQL_AQUI.mysql.pythonanywhere-services.com'
DB_NAME = 'TU_USUARIO_AQUI$default'
# ----------------------------------------

# Inicialización de la App Flask
app = Flask(__name__)

# Configuración de la Conexión a la Base de Datos
try:
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOSTNAME}/{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = SQLAlchemy(app)

    # Definición del Modelo de la Base de Datos (la tabla)
    class Response(db.Model):
        __tablename__ = 'responses'
        id = db.Column(db.Integer, primary_key=True)
        mos_score = db.Column(db.Integer, nullable=False)
        submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

        def __repr__(self):
            return f'<Response {self.id}: MOS={self.mos_score}>'

except Exception as e:
    print(f"Error al configurar la base de datos: {e}")
    # Si hay un error de config, la app seguirá funcionando para mostrar la página,
    # pero el envío de datos fallará.
    db = None

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
    if not db:
        return jsonify({"success": False, "error": "Database not configured"}), 500

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

# --- Sección para crear la tabla si no existe (opcional, mejor hacerlo manual) ---
# Con el contexto de la aplicación, crea las tablas si no existen.
# Es mejor correr esto una vez localmente o correr el SQL manual en PythonAnywhere.
# @app.before_first_request
# def create_tables():
#     try:
#         db.create_all()
#     except Exception as e:
#         print(f"Error creating tables: {e}")

if __name__ == '__main__':
    # Esto es solo para pruebas locales, PythonAnywhere usa un servidor WSGI
    app.run(debug=True)
