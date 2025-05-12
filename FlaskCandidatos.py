from flask import Flask, redirect, render_template, request, session, url_for, flash
import threading
import joblib
import os
from FlaskLocal import db, Candidato, Educacion, Tecnologia, Habilidad  # Importamos los modelos
import sys
import webbrowser
import re

app = Flask(__name__)
app.secret_key = "MiraQueSéQueMeVes"  # Necesario para sesiones

# Configura la URI de la base de datos aquí
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///erp_rrhh.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  # Vincula db con la instancia actual de Flask

def abrir_navegador():
    webbrowser.open("http://127.0.0.1:5001/")  # URL de Flask

# 🔹 Obtener la ruta correcta dentro del ejecutable
def get_path(relative_path):
    """Obtiene la ruta absoluta, considerando si se ejecuta como .exe"""
    if getattr(sys, 'frozen', False):
        # Si se ejecuta como ejecutable de PyInstaller
        base_path = sys._MEIPASS
    else:
        # Si se ejecuta como script Python normal
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Página principal
@app.route("/")
def home():
    # Las opciones ya están en la base de datos, no necesitamos encoders aquí
    opciones_educacion = [educacion.nombre for educacion in Educacion.query.all()]
    opciones_tecnologias = [tecnologia.nombre for tecnologia in Tecnologia.query.all()]
    opciones_habilidades = [habilidad.nombre for habilidad in Habilidad.query.all()]

    session["opciones_educacion"] = opciones_educacion
    session["opciones_tecnologias"] = opciones_tecnologias
    session["opciones_habilidades"] = opciones_habilidades

    return render_template(
        "postulacion.html",
        opciones_educacion=session["opciones_educacion"],
        opciones_tecnologias=session["opciones_tecnologias"],
        opciones_habilidades=session["opciones_habilidades"]
    )

@app.route("/postulacion", methods=["GET", "POST"])
def crear_csv():
    if request.method == "POST":
        # Obtener datos del formulario
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        email = request.form["email"]
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            flash("Correo electrónico inválido. Por favor ingresa un email válido.")
            return redirect("/postulacion")
        telefono = request.form["telefono"]
        if not telefono.isdigit() or len(telefono) < 8 or len(telefono) > 10:
            flash("El teléfono debe contener solo números y tener entre 8 y 10 cifras.")
            return redirect("/postulacion")
        ubicacion = request.form["ubicacion"]
        PROVINCIAS_ARG = [
        "Buenos Aires", "CABA", "Catamarca", "Chaco", "Chubut", "Córdoba",
        "Corrientes", "Entre Ríos", "Formosa", "Jujuy", "La Pampa", "La Rioja",
        "Mendoza", "Misiones", "Neuquén", "Río Negro", "Salta", "San Juan",
        "San Luis", "Santa Cruz", "Santa Fe", "Santiago del Estero",
        "Tierra del Fuego", "Tucumán"]
        if ubicacion not in PROVINCIAS_ARG:
            flash("Ubicación no válida. Selecciona una provincia de Argentina.")
            return redirect("/postulacion")
        experiencia = int(request.form["experiencia"])
        educacion = request.form["educacion"]
        tecnologias = request.form["tecnologias"]
        habilidades = request.form["habilidades"]

        try:
            # Buscar el ID correspondiente en las tablas
            educacion_obj = Educacion.query.filter_by(nombre=educacion).first()
            tecnologia_obj = Tecnologia.query.filter_by(nombre=tecnologias).first()
            habilidad_obj = Habilidad.query.filter_by(nombre=habilidades).first()

            if not educacion_obj or not tecnologia_obj or not habilidad_obj:
                return "Error: Valores inválidos seleccionados.", 400

            idedu = educacion_obj.idedu
            idtec = tecnologia_obj.idtec
            idhab = habilidad_obj.idhab

            # Crear y guardar el candidato
            nuevo_candidato_db = Candidato(
                id=email,
                nombre=nombre,
                apellido=apellido,  # Nuevo campo
                mail=email,
                telefono=telefono,  # Nuevo campo
                ubicacion=ubicacion,
                experiencia=experiencia,
                idedu=idedu,
                idtec=idtec,
                idhab=idhab,
                aptitud=None
            )
            db.session.add(nuevo_candidato_db)
            db.session.commit()
            print(f"Candidato {nombre} guardado correctamente en la base de datos.")
        except Exception as e:
            print(f"Error al guardar el candidato: {e}")
            return "Error al guardar el candidato.", 500

        return redirect("/")

    return render_template(
        "postulacion.html",
        opciones_educacion=session["opciones_educacion"],
        opciones_tecnologias=session["opciones_tecnologias"],
        opciones_habilidades=session["opciones_habilidades"]
    )

if __name__ == "__main__":
    threading.Timer(1.5, abrir_navegador).start()
    app.run(debug=False, host="127.0.0.1", port=5001)
    
    
    
    