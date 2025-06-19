import requests
from flask import Flask, redirect, render_template, request, send_file, session, url_for, flash, has_request_context
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree
import webbrowser
import numpy as np
import threading
import joblib
import os
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import io
import base64
from werkzeug.security import generate_password_hash, check_password_hash
import re
from flask_mail import Mail, Message
from functools import wraps
from datetime import datetime
from flask import jsonify
import fitz
from datetime import datetime, timedelta


app = Flask(__name__)
app.secret_key = "MiraQueSéQueMeVes"  # Necesario para sesiones
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///erp_rrhh.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='perfectmatch.rrhh@gmail.com',
    MAIL_PASSWORD='wgro qiym amag zbjy'
)

email = Mail(app)


# Base de datos

class Candidato(db.Model):
    __tablename__ = "candidato"
    id = db.Column(db.String, primary_key=True)  # Usamos el correo como ID único
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    mail = db.Column(db.String(100), nullable=False, unique=True)
    telefono = db.Column(db.String(50), nullable=False)
    ubicacion = db.Column(db.String(100), nullable=False)
    
    experiencia = db.Column(db.Integer, nullable=True) 
    idedu = db.Column(db.Integer, db.ForeignKey("educacion.idedu"), nullable=True)
    idtec = db.Column(db.Integer, db.ForeignKey("tecnologia.idtec"), nullable=True)
    idtec2 = db.Column(db.Integer, db.ForeignKey("tecnologia2.idtec2"), nullable=True)
    idhab = db.Column(db.Integer, db.ForeignKey("habilidad.idhab"), nullable=True)
    idhab2 = db.Column(db.Integer, db.ForeignKey("habilidad2.idhab2"), nullable=True)

    postulaciones = db.relationship("Postulacion", back_populates="candidato", cascade="all, delete-orphan")

class Postulacion(db.Model):
    __tablename__ = "postulacion"

    idPostulacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idCandidato = db.Column(db.String, db.ForeignKey("candidato.id"))
    idOfer = db.Column(db.Integer, db.ForeignKey("oferta_laboral.idOfer"))
    
    experiencia = db.Column(db.Integer, nullable=False)
    idedu = db.Column(db.Integer, db.ForeignKey("educacion.idedu"))
    idtec = db.Column(db.Integer, db.ForeignKey("tecnologia.idtec"))
    idtec2 = db.Column(db.Integer, db.ForeignKey("tecnologia2.idtec2"))
    idhab = db.Column(db.Integer, db.ForeignKey("habilidad.idhab"))
    idhab2 = db.Column(db.Integer, db.ForeignKey("habilidad2.idhab2"))
    aptitud = db.Column(db.Boolean, nullable=True)
    puntaje = db.Column(db.Integer, nullable=False, default=0)

    candidato = db.relationship("Candidato", back_populates="postulaciones")
    oferta = db.relationship("OfertaLaboral", back_populates="postulaciones")

class OfertaLaboral(db.Model):
    __tablename__ = "oferta_laboral"

    idOfer = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(200), nullable=False, unique=True)
    fecha_cierre = db.Column(db.DateTime, nullable=False)
    max_candidatos = db.Column(db.Integer, nullable=False)
    cant_candidatos = db.Column(db.Integer, nullable=False, default=0)
    remuneracion = db.Column(db.String(50), nullable=False)
    beneficio = db.Column(db.String(200), nullable=True)
    estado = db.Column(db.String(50), nullable=False, default="Activa")
    modalidad = db.Column(db.String(20), nullable=False)
    usuario_responsable = db.Column(db.String(100), nullable=False)

    postulaciones = db.relationship("Postulacion", back_populates="oferta", cascade="all, delete-orphan", lazy=True)
    educaciones = db.relationship("OfertaEducacion", back_populates="oferta", lazy=True)
    tecnologias = db.relationship("OfertaTecnologia", back_populates="oferta", lazy=True)
    tecnologias2 = db.relationship("OfertaTecnologia2", back_populates="oferta", lazy=True)
    habilidades = db.relationship("OfertaHabilidad", back_populates="oferta", lazy=True)
    habilidades2 = db.relationship("OfertaHabilidad2", back_populates="oferta", lazy=True)



# Tablas intermedias para asociar cada oferta con sus etiquetas

class OfertaEducacion(db.Model):
    __tablename__ = 'oferta_educacion'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idOfer = db.Column(db.Integer, db.ForeignKey('oferta_laboral.idOfer'))
    idEdu = db.Column(db.Integer, db.ForeignKey('educacion.idedu'))
    importancia = db.Column(db.Integer, nullable=False)

    oferta = db.relationship('OfertaLaboral', back_populates='educaciones')
    educacion = db.relationship('Educacion')

class OfertaTecnologia(db.Model):
    __tablename__ = 'oferta_tecnologia'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idOfer = db.Column(db.Integer, db.ForeignKey('oferta_laboral.idOfer'))
    idTec = db.Column(db.Integer, db.ForeignKey('tecnologia.idtec'))
    importancia = db.Column(db.Integer, nullable=False)

    oferta = db.relationship('OfertaLaboral', back_populates='tecnologias')
    tecnologia = db.relationship('Tecnologia')
    
class OfertaTecnologia2(db.Model):
    __tablename__ = 'oferta_tecnologia2'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idOfer = db.Column(db.Integer, db.ForeignKey('oferta_laboral.idOfer'))
    idTec2 = db.Column(db.Integer, db.ForeignKey('tecnologia2.idtec2'))
    importancia = db.Column(db.Integer, nullable=False)

    oferta = db.relationship('OfertaLaboral', back_populates='tecnologias2')
    tecnologia2 = db.relationship('Tecnologia2')

class OfertaHabilidad(db.Model):
    __tablename__ = 'oferta_habilidad'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idOfer = db.Column(db.Integer, db.ForeignKey('oferta_laboral.idOfer'))
    idHab = db.Column(db.Integer, db.ForeignKey('habilidad.idhab'))
    importancia = db.Column(db.Integer, nullable=False)

    oferta = db.relationship('OfertaLaboral', back_populates='habilidades')
    habilidad = db.relationship('Habilidad')
    
class OfertaHabilidad2(db.Model):
    __tablename__ = 'oferta_habilidad2'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idOfer = db.Column(db.Integer, db.ForeignKey('oferta_laboral.idOfer'))
    idHab2 = db.Column(db.Integer, db.ForeignKey('habilidad2.idhab2'))
    importancia = db.Column(db.Integer, nullable=False)

    oferta = db.relationship('OfertaLaboral', back_populates='habilidades2')
    habilidad2 = db.relationship('Habilidad2')

class Educacion(db.Model):
    __tablename__ = 'educacion'
    idedu = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)


class Tecnologia(db.Model):
    __tablename__ = 'tecnologia'
    idtec = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    
class Tecnologia2(db.Model):
    __tablename__ = 'tecnologia2'
    idtec2 = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)


class Habilidad(db.Model):
    __tablename__ = 'habilidad'
    idhab = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    
class Habilidad2(db.Model):
    __tablename__ = 'habilidad2'
    idhab2 = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)

    
class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    
def get_path(relative_path):
    """Obtiene la ruta absoluta, considerando si se ejecuta como .exe"""
    if getattr(sys, 'frozen', False):
        # Si se ejecuta como ejecutable de PyInstaller
        base_path = sys._MEIPASS
    else:
        # Si se ejecuta como script Python normal
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

'''
# Crear la base de datos y agregar usuarios ficticios si no existen
with app.app_context():
    db.create_all()

    # 📌 Cargar los encoders
    encoder_educacion = joblib.load(get_path("encoder_educacion.pkl"))
    encoder_tecnologias = joblib.load(get_path("encoder_tecnologias.pkl"))
    encoder_habilidades = joblib.load(get_path("encoder_habilidades.pkl"))
    encoder_tecnologias2 = joblib.load(get_path("encoder_tecnologias2.pkl"))
    encoder_habilidades2 = joblib.load(get_path("encoder_habilidades2.pkl"))

    # 📌 Insertar educación en la tabla 'Educacion'
    for idx, clase in enumerate(encoder_educacion.classes_):
        nueva_educacion = Educacion(idedu=idx, nombre=clase)
        db.session.merge(nueva_educacion)  

    # 📌 Insertar tecnologías en 'Tecnologia'
    for idx, clase in enumerate(encoder_tecnologias.classes_):
        nueva_tecnologia = Tecnologia(idtec=idx, nombre=clase)
        db.session.merge(nueva_tecnologia)

    # 📌 Insertar tecnologías secundarias en 'Tecnologia2'
    for idx, clase in enumerate(encoder_tecnologias2.classes_):
        nueva_tecnologia2 = Tecnologia2(idtec2=idx, nombre=clase)
        db.session.merge(nueva_tecnologia2)

    # 📌 Insertar habilidades en 'Habilidad'
    for idx, clase in enumerate(encoder_habilidades.classes_):
        nueva_habilidad = Habilidad(idhab=idx, nombre=clase)
        db.session.merge(nueva_habilidad)

    # 📌 Insertar habilidades secundarias en 'Habilidad2'
    for idx, clase in enumerate(encoder_habilidades2.classes_):
        nueva_habilidad2 = Habilidad2(idhab2=idx, nombre=clase)
        db.session.merge(nueva_habilidad2)

    db.session.commit()
    print("Clases cargadas automáticamente en la base de datos.")

    # 📌 Crear usuarios ficticios correctamente adaptados
    usuario_admin = Usuario(username="Fernando", password=generate_password_hash("admin123", method="pbkdf2:sha256"), type="Admin_RRHH")
    usuario_supervisor = Usuario(username="Diego", password=generate_password_hash("supervisor123", method="pbkdf2:sha256"), type="Supervisor")
    usuario_analista = Usuario(username="Guada", password=generate_password_hash("analista123", method="pbkdf2:sha256"), type="Analista_Datos")

    db.session.add(usuario_admin)
    db.session.add(usuario_supervisor)
    db.session.add(usuario_analista)
    db.session.commit()
    print("Usuarios ficticios creados con éxito.")

'''

# Cargar el modelo correctamente
modelo_path = get_path("modelo_candidatos.pkl")

try:
    encoder_educacion_path = get_path("encoder_educacion.pkl")
    encoder_habilidades_path = get_path("encoder_habilidades.pkl")
    encoder_tecnologias_path = get_path("encoder_tecnologias.pkl")
    encoder_habilidades2_path = get_path("encoder_habilidades2.pkl")
    encoder_tecnologias2_path = get_path("encoder_tecnologias2.pkl")
except FileNotFoundError as e:
    print("Error: No se pudo cargar el archivo del encoder.", e)
    raise e
except Exception as e:
    print("Error al cargar los encoders:", e)
    raise e


# FUNCIONES
def abrir_navegador():
    webbrowser.open("http://127.0.0.1:5000/")  # URL de Flask


def obtener_correos_aptos(idOfer):
    postulaciones = Postulacion.query.filter_by(idOfer=idOfer, aptitud=True).all()  # 
    return [(p.candidato.nombre, p.candidato.mail) for p in postulaciones if p.candidato]  # 


def obtener_correos_noaptos(idOfer):
    postulaciones = Postulacion.query.filter_by(idOfer=idOfer, aptitud=False).all()  # 
    return [(p.candidato.nombre, p.candidato.mail) for p in postulaciones if p.candidato]  # 





def login_required(roles=None):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if 'username' not in session:
                return redirect(url_for('login'))
            if roles and session.get('type') not in roles:
                return "Acceso no autorizado"
            return f(*args, **kwargs)
        return wrapped
    return decorator
    
    
# Página principal RRHH
@app.route('/')
def index():
    return redirect('/login')


@app.route('/sobre-nosotros')
def sobre_nosotros():
    return render_template('sobre_nosotros.html')




@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario.query.filter_by(username=username).first()
        
        # Verificar si el usuario existe
        user_exists = user is not None
        
        # Verificar si la contraseña sería correcta para algún usuario
        password_exists = False
        if not user_exists:
            # Buscar si existe algún usuario con esta contraseña
            all_users = Usuario.query.all()
            for u in all_users:
                if check_password_hash(u.password, password):
                    password_exists = True
                    break
        
        if user_exists and check_password_hash(user.password, password):
            # Login exitoso
            session['username'] = user.username
            session['type'] = user.type
            # Redirige según el rol usando url_for
            if user.type == "Admin_RRHH":
                return redirect(url_for('admin_rrhh'))
            elif user.type == "Supervisor":
                return redirect(url_for('supervisor'))
            elif user.type == "Analista_Datos":
                return redirect(url_for('analista'))
        elif user_exists and not check_password_hash(user.password, password):
            # Usuario correcto, contraseña incorrecta
            flash("❌ Contraseña incorrecta", category="login")
            return redirect(url_for('login'))
        elif not user_exists and password_exists:
            # Usuario incorrecto, pero la contraseña existe
            flash("❌ Usuario no existente", category="login")
            return redirect(url_for('login'))
        else:
            # Ni el usuario ni la contraseña existen son correctos
            flash("❌ Credenciales inválidas", category="login")
            return redirect(url_for('login'))
            
    return render_template("auth/login.html")


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/admin_rrhh')
@login_required(roles=["Admin_RRHH"])
def admin_rrhh():
    #if 'username' in session and session.get('type') == "Admin_RRHH":
        #return f"Bienvenido {session.get('username')} al panel de Administrador de RRHH."
    return redirect('/predecir')


@app.route('/supervisor')
def supervisor():
    if 'username' in session and session.get('type') == "Supervisor":
        return f"Bienvenido {session.get('username')} al panel de Supervisor."
    return redirect('/login')


@app.route('/analista')
def analista():
    if 'username' in session and session.get('type') == "Analista_Datos":
        return f"Bienvenido {session.get('username')} al panel de Analista de Datos."
    return redirect('/login')

@app.route('/gestionar_usuarios', methods=['GET', 'POST'])
@login_required(roles=["Admin_RRHH"])
def gestionar_usuarios():
    filtro = request.args.get('rol')
    if filtro:
        usuarios = Usuario.query.filter(Usuario.type == filtro).all()
    else:
        usuarios = Usuario.query.all()
    return render_template('gestionarUsuarios.html', usuarios=usuarios, filtro=filtro)

@app.route('/crear_usuario', methods=["GET", "POST"])
@login_required(roles=["Admin_RRHH"])
def crear_usuario():
    if request.method == "POST":
        username = request.form['username']
        password = generate_password_hash(request.form['password'], method="pbkdf2:sha256")
        type = request.form['type']
        nuevo = Usuario(username=username, password=password, type=type)
        db.session.add(nuevo)
        db.session.commit()
        flash("Usuario creado")
        return redirect(url_for('gestionarUsuarios'))
    return render_template("crear_usuario.html")

@app.route('/cambiar_password', methods=["GET", "POST"])
@login_required()
def cambiar_password():
    if request.method == "POST":
        actual = request.form['actual']
        nueva = request.form['nueva']
        usuario = Usuario.query.filter_by(username=session['username']).first()
        if check_password_hash(usuario.password, actual):
            usuario.password = generate_password_hash(nueva)
            db.session.commit()
            flash("Contraseña actualizada")
        else:
            flash("Contraseña actual incorrecta")
    return render_template("cambiar_password.html")

@app.route('/editar_usuario/<int:id>', methods=["GET", "POST"])
@login_required(roles=["Admin_RRHH"])
def editar_usuario(id):
    usuario = Usuario.query.get_or_404(id)

    if request.method == "POST":
        usuario.username = request.form['username']
        nuevo_tipo = request.form['type']
        nueva_clave = request.form['password']

        if nuevo_tipo:
            usuario.type = nuevo_tipo

        if nueva_clave:
            usuario.password = generate_password_hash(nueva_clave, method="pbkdf2:sha256")

        db.session.commit()
        flash("Usuario actualizado correctamente")
        return redirect(url_for('gestionar_usuarios'))

    return render_template("editar_usuario.html", usuario=usuario)

@app.route('/eliminar_usuario/<int:id>', methods=["POST", "GET"])
@login_required(roles=["Admin_RRHH"])
def eliminar_usuario(id):
    usuario = Usuario.query.get_or_404(id)

    # Evitar que se elimine a sí mismo
    if usuario.username == session.get('username'):
        flash("No puedes eliminar tu propia cuenta", "error")
        return redirect(url_for("gestionar_usuarios"))

    db.session.delete(usuario)
    db.session.commit()
    flash("Usuario eliminado con éxito", "success")
    return redirect(url_for("gestionar_usuarios"))


@app.route('/enviar_correos')
def enviar_correos():
    #mails a candidatos aptos
    destinatariosAptos = obtener_correos_aptos()
    with email.connect() as conn:
        for nombre, mail in destinatariosAptos:
            mensaje = Message(subject='Oportunidad laboral',
                              sender=app.config['MAIL_USERNAME'],
                              recipients=[mail],
                              body=f"Hola {nombre},\n\nHemos revisado tu perfil y estamos interesados en tu candidatura.\n¡Gracias por postularte!")
            conn.send(mensaje)
    #mails a candidatos no aptos
    destinatariosNoAptos = obtener_correos_noaptos()
    with email.connect() as conn:
        for nombre, mail in destinatariosNoAptos:
            mensaje = Message(subject='Oportunidad laboral',
                                sender=app.config['MAIL_USERNAME'],
                                recipients=[mail],
                                body=f"Hola {nombre},\n\nLamentamos informarte que en esta oportunidad tu perfil no se ajusta a lo que buscamos.\nTe animamos a postularte en futuras oportunidades.")
            conn.send(mensaje)
    return redirect('/predecir')     






# Página principal postulacion
@app.route("/postulacionIT")
def postulacionIT():
    # Las opciones ya están en la base de datos, no necesitamos encoders aquí
    opciones_ofertas = [{"idOfer": oferta.idOfer, "nombre": oferta.nombre} for oferta in OfertaLaboral.query.filter(OfertaLaboral.estado != "Cerrada").all()]
    opciones_educacion = [educacion.nombre for educacion in Educacion.query.all()]
    opciones_tecnologias = [tecnologia.nombre for tecnologia in Tecnologia.query.all()]
    opciones_habilidades = [habilidad.nombre for habilidad in Habilidad.query.all()]
    opciones_tecnologias2 = [tecnologia2.nombre for tecnologia2 in Tecnologia2.query.all()]
    opciones_habilidades2 = [habilidad2.nombre for habilidad2 in Habilidad2.query.all()]

    session["opciones_ofertas"] = opciones_ofertas
    session["opciones_educacion"] = opciones_educacion
    session["opciones_tecnologias"] = opciones_tecnologias
    session["opciones_habilidades"] = opciones_habilidades
    session["opciones_tecnologias2"] = opciones_tecnologias2
    session["opciones_habilidades2"] = opciones_habilidades2

    return render_template(
        "postulacion.html",
        opciones_educacion=session["opciones_educacion"],
        opciones_ofertas=session["opciones_ofertas"],
        opciones_tecnologias=session["opciones_tecnologias"],
        opciones_habilidades=session["opciones_habilidades"],
        opciones_tecnologias2=session["opciones_tecnologias2"],
        opciones_habilidades2=session["opciones_habilidades2"]
    )


@app.route("/postulacion", methods=["GET", "POST"])
def postulacion():
    #es_admin = "username" in session and session.get("type") == "Admin_RRHH"

    if request.method == "POST":
        # Obtener datos del formulario
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        email = request.form["email"]
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            flash("Por favor ingresa un email válido.<br>Ejemplo: JuanPerez@gmail.com")
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
        idOfer = request.form.get("idOfer")
        tecnologias2 = request.form["tecnologias2"]
        habilidades2 = request.form["habilidades2"]

        try:
            # Buscar el ID correspondiente en las tablas
            educacion_obj = Educacion.query.filter_by(nombre=educacion).first()
            tecnologia_obj = Tecnologia.query.filter_by(nombre=tecnologias).first()
            habilidad_obj = Habilidad.query.filter_by(nombre=habilidades).first()
            tecnologia2_obj = Tecnologia2.query.filter_by(nombre=tecnologias2).first()
            habilidad2_obj = Habilidad2.query.filter_by(nombre=habilidades2).first()

            if not educacion_obj or not tecnologia_obj or not habilidad_obj or not tecnologia2_obj or not habilidad2_obj:
                flash("Error: Valores inválidos seleccionados.")
                return redirect("/postulacion")

            idedu = educacion_obj.idedu
            idtec = tecnologia_obj.idtec
            idhab = habilidad_obj.idhab
            idtec2 = tecnologia2_obj.idtec2
            idhab2 = habilidad2_obj.idhab2


            # Crear y guardar el candidato
            nuevo_candidato_db = Candidato(
                id=email + idOfer,
                nombre=nombre,
                apellido=apellido,
                mail=email,
                telefono=telefono,
                ubicacion=ubicacion,
                experiencia=experiencia,
                idOfer=idOfer,
                idedu=idedu,
                idtec=idtec,
                idhab=idhab,
                idtec2=idtec2,
                idhab2=idhab2,
                aptitud=None
            )
            db.session.add(nuevo_candidato_db)
            db.session.commit()
            flash(f"{nombre}, tu CV ha sido correctamente enviado a la oferta laboral de: '{OfertaLaboral.query.get(idOfer).nombre}'.")
        except Exception as e:
            flash(f"Este mail ya había sido registrado en esta postulación")
            return redirect("/postulacion")

    return render_template(
        "postulacion.html",
        #es_admin=es_admin,
        opciones_ofertas=session["opciones_ofertas"],
        opciones_educacion=session["opciones_educacion"],
        opciones_tecnologias=session["opciones_tecnologias"],
        opciones_habilidades=session["opciones_habilidades"],
        opciones_tecnologias2=session["opciones_tecnologias2"],
        opciones_habilidades2=session["opciones_habilidades2"]
    )

@app.route('/crear_oferta', methods=['GET', 'POST'])
@login_required(roles=["Admin_RRHH"])
def crear_oferta():
    if request.method == "POST":
        try:
            nombre = request.form.get("nombre")
            fecha_cierre_str = request.form.get("fecha_cierre")
            max_candidatos = int(request.form.get("max_candidatos"))
            remuneracion = "$" + request.form.get("remuneracion") 
            beneficio = request.form.get("beneficio")  
            usuario_responsable = session.get("username")  
            modalidad = request.form.get("modalidad")  
            fecha_cierre = datetime.strptime(fecha_cierre_str, "%Y-%m-%d")

            # Validaciones
            if not (nombre and 4 < len(nombre) < 51):
                flash("❌ El nombre debe tener entre 5 y 50 caracteres.", "error")
                return redirect("/crear_oferta")
            
            # Verificar si el nombre ya existe
            if OfertaLaboral.query.filter_by(nombre=nombre).first():
                flash(f"Error: La oferta '{nombre}' ya existe. Elige un nombre diferente.")
                return redirect("/crear_oferta")

            if not (4 < max_candidatos < 1001):
                flash("❌ La cantidad máxima de candidatos debe estar entre 5 y 1000.", "error")
                return redirect("/crear_oferta")

            try:
                remuneracion_int = int(request.form.get("remuneracion"))
            except ValueError:
                flash("❌ La remuneración debe ser un número entero válido.", "error")
                return redirect("/crear_oferta")

            if not (200 < remuneracion_int < 90000):
                flash("❌ La remuneración debe estar entre 201 y 89999.", "error")
                return redirect("/crear_oferta")

            if not (beneficio and 2 < len(beneficio) < 61):
                flash("❌ El campo beneficio debe tener entre 3 y 60 caracteres.", "error")
                return redirect("/crear_oferta")

            #  Validar modalidad antes de crear la oferta
            if modalidad not in ["Local", "Mixta", "Externa"]:
                flash("❌ Modalidad inválida. Debe ser 'Local', 'Mixta' o 'Externa'.", "error")
                return redirect("/crear_oferta")
           
            nueva_oferta = OfertaLaboral(
                nombre=nombre,
                fecha_cierre=fecha_cierre,
                max_candidatos=max_candidatos,
                remuneracion=remuneracion,
                beneficio=beneficio,
                estado="Activa",  #  Siempre comienza como "Activa"
                modalidad=modalidad,  #  Guardamos la modalidad
                usuario_responsable=usuario_responsable
            )
            db.session.add(nueva_oferta)
            db.session.flush()  #  Garantizar que obtenemos el ID antes de insertar etiquetas

           
            encoder_educacion = joblib.load(get_path("encoder_educacion.pkl"))
            encoder_tecnologias = joblib.load(get_path("encoder_tecnologias.pkl"))
            encoder_habilidades = joblib.load(get_path("encoder_habilidades.pkl"))
            encoder_tecnologias2 = joblib.load(get_path("encoder_tecnologias2.pkl"))
            encoder_habilidades2 = joblib.load(get_path("encoder_habilidades2.pkl"))

            # 🔹 Asignar etiquetas en las tablas intermedias con importancia = 0
            for idx, clase in enumerate(encoder_educacion.classes_):
                nueva_relacion = OfertaEducacion(idOfer=nueva_oferta.idOfer, idEdu=idx, importancia=0)
                db.session.add(nueva_relacion)

            for idx, clase in enumerate(encoder_tecnologias.classes_):
                nueva_relacion = OfertaTecnologia(idOfer=nueva_oferta.idOfer, idTec=idx, importancia=0)
                db.session.add(nueva_relacion)

            for idx, clase in enumerate(encoder_habilidades.classes_):
                nueva_relacion = OfertaHabilidad(idOfer=nueva_oferta.idOfer, idHab=idx, importancia=0)
                db.session.add(nueva_relacion)
                
            for idx, clase in enumerate(encoder_tecnologias2.classes_):
                nueva_relacion = OfertaTecnologia2(idOfer=nueva_oferta.idOfer, idTec2=idx, importancia=0)
                db.session.add(nueva_relacion)

            for idx, clase in enumerate(encoder_habilidades2.classes_):
                nueva_relacion = OfertaHabilidad2(idOfer=nueva_oferta.idOfer, idHab2=idx, importancia=0)
                db.session.add(nueva_relacion)
                
            if nueva_oferta.modalidad in ["Local", "Mixta"]:
                candidatos = Candidato.query.all()

                for candidato in candidatos:
                    nueva_postulacion = Postulacion(
                        idCandidato=candidato.id,
                        idOfer=nueva_oferta.idOfer,
                        experiencia=candidato.experiencia,
                        idedu=candidato.idedu,
                        idtec=candidato.idtec,
                        idtec2=candidato.idtec2,
                        idhab=candidato.idhab,
                        idhab2=candidato.idhab2,
                        aptitud=None,
                        puntaje=0
                    )
                    db.session.add(nueva_postulacion)

                nueva_oferta.cant_candidatos += len(candidatos)


            db.session.commit()  
            flash(f"✔️Oferta '{nombre}' creada con éxito, con estado '{nueva_oferta.estado}', modalidad '{nueva_oferta.modalidad}' y etiquetas asignadas", "success")
            return redirect("/crear_oferta")
        
        except Exception as e:
            db.session.rollback()  
            flash(f"Error al crear la oferta: {str(e)}", "error")
            return redirect("/crear_oferta")

    return render_template("crear_oferta.html")


@app.route("/ver_ofertas")
@login_required(roles=["Admin_RRHH"])
def ver_ofertas():
    ofertas = OfertaLaboral.query.order_by(OfertaLaboral.fecha_cierre.desc()).all()

    if not ofertas:
        return render_template("ver_ofertas.html", mensaje="No hay ofertas disponibles.")

    # Crear DataFrame con las ofertas, incluyendo botón de cierre
    dataSet = pd.DataFrame([{
        "ID Oferta": o.idOfer,
        "Nombre": o.nombre,
        "Fecha Cierre": o.fecha_cierre.strftime("%Y-%m-%d"),
        "Cantidad de Candidatos Postulados": o.cant_candidatos,
        "Cantidad Máx. de Candidatos": o.max_candidatos,
        "Remuneración": o.remuneracion,
        "Beneficio": o.beneficio,
        "Tipo": o.modalidad,
        "Estado": o.estado,
        "Responsable": o.usuario_responsable,
        "Acción": f'<form style="display: inline-block; width: 110px; height: 35px; margin: 0 auto;" method="POST" action="{url_for("cerrar_oferta", idOfer=o.idOfer)}">'
                f'<input type="hidden" name="forzar" value="1">'
                f'<button style="font-size: 12px; margin: 0 !important; padding: 0 !important; width: 100px; height: 30px;" type="submit">Cerrar oferta</button></form>' 
                if o.fecha_cierre > datetime.now() else "Oferta cerrada"

    } for o in ofertas])

    # Convertir el DataFrame a tabla HTML, asegurando que los botones sean renderizados
    tabla_html = dataSet.to_html(classes="table table-striped", index=False, escape=False)

    return render_template("ver_ofertas.html", tabla=tabla_html)



@app.route("/cerrar_oferta/<int:idOfer>", methods=["POST"])
@login_required(roles=["Admin_RRHH"])
def cerrar_oferta(idOfer):
    oferta = OfertaLaboral.query.get(idOfer)

    if not oferta or oferta.estado == "Cerrada":
        flash("La oferta ya está cerrada o no existe.", "error")
        return redirect(url_for("ver_ofertas"))

    forzar = request.form.get("forzar")

    print("Form data:", request.form)
    print("Valor de forzar:", request.form.get("forzar"))
    if forzar == "1" or oferta.fecha_cierre <= datetime.now() or oferta.cant_candidatos >= oferta.max_candidatos:
        oferta.fecha_cierre = datetime.now()
        oferta.estado = "Cerrada"

        predecir_postulantes_automatica(oferta.idOfer)
        asignar_puntajes_automatica(oferta.idOfer)
        enviar_correos_automatica(oferta.idOfer)

        db.session.commit()
        flash(f"La oferta '{oferta.nombre}' ha sido cerrada correctamente.", "success")
    else:
        flash("La oferta aún no puede cerrarse automáticamente.", "warning")

    return redirect(url_for("ver_ofertas"))


@app.route("/limpiar_ofertas", methods=["POST"])
@login_required(roles=["Admin_RRHH"])
def limpiar_ofertas_expiradas():
    umbral = datetime.now() - timedelta(hours=24)

    ofertas_a_eliminar = OfertaLaboral.query.filter(
        OfertaLaboral.estado == "Cerrada",
        OfertaLaboral.fecha_cierre <= umbral
    ).all()

    eliminadas = [oferta.nombre for oferta in ofertas_a_eliminar]

    for oferta in ofertas_a_eliminar:
        db.session.delete(oferta)

    db.session.commit()

    if eliminadas:
        flash(f"🗑 Se eliminaron {len(eliminadas)} ofertas cerradas: {', '.join(eliminadas)}", "success")
    else:
        flash("✅ No hay ofertas cerradas hace más de 24hs para eliminar.", "info")

    return redirect(url_for("ver_ofertas"))



# Página de estadísticas
@app.route("/estadisticas", methods=["GET", "POST"])
@login_required(roles=["Admin_RRHH"])
def estadisticas():
    if request.method == "POST":
        return render_template("index.html")
    # Cargar modelo y encoders
    modelo = joblib.load(get_path("modelo_candidatos.pkl"))
    encoder_educacion = joblib.load(get_path("encoder_educacion.pkl"))
    encoder_habilidades = joblib.load(get_path("encoder_habilidades.pkl"))
    encoder_tecnologias = joblib.load(get_path("encoder_tecnologias.pkl"))
    encoder_habilidades2 = joblib.load(get_path("encoder_habilidades2.pkl"))
    encoder_tecnologias2 = joblib.load(get_path("encoder_tecnologias2.pkl"))
    
    # Leer el dataset de entrenamiento
    dataSet = pd.read_csv(get_path("candidatos8.csv"))

    dataSet["Educacion"] = encoder_educacion.fit_transform(dataSet["Educacion"])
    dataSet["Habilidades"] = encoder_habilidades.fit_transform(dataSet["Habilidades"])
    dataSet["Habilidades2"] = encoder_habilidades2.fit_transform(dataSet["Habilidades2"])
    dataSet["Tecnologías"] = encoder_tecnologias.fit_transform(dataSet["Tecnologías"])
    dataSet["Tecnologías2"] = encoder_tecnologias2.fit_transform(dataSet["Tecnologías2"])

    # Ya está codificado, así que sólo aseguramos que Apto esté como entero
    if dataSet["Apto"].dtype == object:
        dataSet["Apto"] = dataSet["Apto"].map({"Apto": 1, "No Apto": 0})

    X = dataSet[["Educacion", "Tecnologías", "Tecnologías2", "Habilidades", "Habilidades2"]]
    y = dataSet["Apto"]
    precision = round(modelo.score(X, y), 4)

    # Clases de encoders
    clases = {
        "Educacion": list(encoder_educacion.classes_),
        "Habilidades": list(encoder_habilidades.classes_),
        "Tecnologías": list(encoder_tecnologias.classes_),
        "Habilidades2": list(encoder_habilidades2.classes_),
        "Tecnologías2": list(encoder_tecnologias2.classes_),
    }

    # Graficar árbol y convertir a imagen en base64
    fig, ax = plt.subplots(figsize=(14, 8))
    plot_tree(modelo, feature_names=[ "Educacion", "Tecnologías", "Tecnologías2", "Habilidades", "Habilidades2"], 
              class_names=["No Apto", "Apto"], filled=True, rounded=True, fontsize=10, ax=ax)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent = True)
    plt.close(fig)
    buf.seek(0)
    imagen_base64 = base64.b64encode(buf.read()).decode("utf-8")

    return render_template(
    "estadisticas.html",
    clases_educacion=clases["Educacion"],
    clases_habilidades=clases["Habilidades"],
    clases_tecnologias=clases["Tecnologías"],
    clases_habilidades2=clases["Habilidades2"],
    clases_tecnologias2=clases["Tecnologías2"],
    precision=precision,
    imagen_arbol=imagen_base64
)


# Ruta para predecir con un archivo CSV
@app.route("/predecir", methods=["GET", "POST"])
@login_required(roles=["Admin_RRHH"])
def predecir():
    plt.close("all")
    ofertas_activas = OfertaLaboral.query.filter_by(estado="Activa").all()
    ofertas_cerradas = OfertaLaboral.query.filter_by(estado="Cerrada").all()
    now = datetime.now()
    total_candidatos = Candidato.query.count()

    if request.method == "POST":
        # 📌 Verifica que el archivo CSV esté en la solicitud
        if "archivo_csv" not in request.files:
            return "Por favor, sube un archivo CSV."

        file = request.files["archivo_csv"]
        if file.filename == "":
            return "No seleccionaste ningún archivo."

        try:
            # 📌 Leer el archivo CSV y cargar el modelo
            dataSet = pd.read_csv(file)
            modelo = joblib.load(get_path("modelo_postulaciones.pkl"))

            # 📌 Cargar los encoders
            encoder_educacion = joblib.load(get_path("encoder_educacion.pkl"))
            encoder_habilidades = joblib.load(get_path("encoder_habilidades.pkl"))
            encoder_tecnologias = joblib.load(get_path("encoder_tecnologias.pkl"))
            encoder_habilidades2 = joblib.load(get_path("encoder_habilidades2.pkl"))
            encoder_tecnologias2 = joblib.load(get_path("encoder_tecnologias2.pkl"))

            session["opciones_educacion"] = list(encoder_educacion.classes_)
            session["opciones_habilidades"] = list(encoder_habilidades.classes_)
            session["opciones_tecnologias"] = list(encoder_tecnologias.classes_)
            session["opciones_habilidades2"] = list(encoder_habilidades2.classes_)
            session["opciones_tecnologias2"] = list(encoder_tecnologias2.classes_)

            # 📌 Verificar que el archivo contiene las columnas requeridas
            columnas_requeridas = ["Experiencia", "Educacion", "Tecnologías", "Habilidades", "Tecnologías2", "Habilidades2"]
            for columna in columnas_requeridas:
                if columna not in dataSet.columns:
                    return f"El archivo no contiene la columna requerida: {columna}"

            # 📌 Transformar las columnas categóricas utilizando los encoders cargados
            try:
                dataSet["Educacion"] = encoder_educacion.transform(dataSet["Educacion"])
                dataSet["Habilidades"] = encoder_habilidades.transform(dataSet["Habilidades"])
                dataSet["Habilidades2"] = encoder_habilidades2.transform(dataSet["Habilidades2"])
                dataSet["Tecnologías"] = encoder_tecnologias.transform(dataSet["Tecnologías"])
                dataSet["Tecnologías2"] = encoder_tecnologias2.transform(dataSet["Tecnologías2"])
            except ValueError as e:
                return f"Error en las transformaciones: {e}. Asegúrate de que todas las categorías estén reconocidas por los encoders."

            # 📌 Verificar si hay valores no válidos después de las transformaciones
            if dataSet[["Educacion", "Tecnologías", "Tecnologías2", "Habilidades", "Habilidades2"]].isnull().values.any():
                return "El archivo contiene categorías que no se pudieron transformar correctamente."

            # 📌 Realizar las predicciones con el modelo
            X = dataSet[["Educacion", "Tecnologías", "Tecnologías2", "Habilidades", "Habilidades2"]]
            predicciones = modelo.predict(X)

            # 📌 Actualizar las postulaciones con la predicción
            for i, pred in enumerate(predicciones):
                email = dataSet.iloc[i]["Email"]
                idOfer = dataSet.iloc[i]["Oferta Laboral"]  

                postulacion = Postulacion.query.filter_by(idCandidato=email, idOfer=idOfer).first()
                if postulacion:
                    postulacion.aptitud = bool(pred)
                    db.session.add(postulacion)

            db.session.commit()

            # 📌 Reordenar las columnas para mostrar en HTML
            dataSet["Apto"] = ["Apto" if pred == 1 else "No Apto" for pred in predicciones]
            columnasOrdenadas = [col for col in dataSet.columns if col != "Apto"] + ["Apto"]
            dataSet = dataSet[columnasOrdenadas]

            # 📌 Convertir DataFrame a HTML y mostrar resultados
            tabla_html = dataSet.to_html(classes="table table-striped", index=False)
            return render_template("resultado.html", tabla=tabla_html, ofertas_activas=ofertas_activas)

        except Exception as e:
            return f"Ocurrió un error al procesar el archivo: {e}"

    return render_template("index.html", ofertas_activas=ofertas_activas, ofertas_cerradas=ofertas_cerradas, now=now, total_candidatos=total_candidatos)




@app.route("/postulantes")
@login_required(roles=["Admin_RRHH"])
def postulantes():
    idOfer = request.args.get("idOfer")
    filtro = request.args.get("filtro")

    ofertas = OfertaLaboral.query.all()
    if not idOfer:
        idOfer = request.form.get("idOfer") if request.method == "POST" else request.args.get("idOfer")
        if not idOfer and ofertas:
            idOfer = ofertas[0].idOfer  

    # 🔹 Detectar ofertas cerradas automáticamente
    ofertas_cerradas = OfertaLaboral.query.filter(
        OfertaLaboral.fecha_cierre <= datetime.now(), OfertaLaboral.estado == "Activa"
    ).all()

    for oferta in ofertas_cerradas:
        oferta.estado = "Cerrada"
        db.session.add(oferta)

        predecir_postulantes_automatica(oferta.idOfer)
        asignar_puntajes_automatica(oferta.idOfer)
        enviar_correos_automatica(oferta.idOfer)

    db.session.commit()  

    # 🔹 Cargar postulaciones en lugar de candidatos
    postulaciones = Postulacion.query.filter_by(idOfer=idOfer).order_by(Postulacion.puntaje.desc()).all() if idOfer else Postulacion.query.order_by(Postulacion.puntaje.desc()).all()

    if not postulaciones:
        return render_template("postulantes.html", 
                               mensaje="No hay postulaciones disponibles.", 
                               ofertas=OfertaLaboral.query.all(), 
                               idOfer=idOfer)

    # 🏆 Generar tabla con los datos actualizados
    dataSet = pd.DataFrame([{
        "Nombre": p.candidato.nombre,
        "Apellido": p.candidato.apellido,
        "Email": p.candidato.mail,
        "Telefono": p.candidato.telefono,
        "Ubicacion": p.candidato.ubicacion,
        "Experiencia": p.experiencia,
        "Educacion": p.idedu,
        "Tecnologías": p.idtec,
        "Habilidades": p.idhab,
        "Tecnologías2": p.idtec2,
        "Habilidades2": p.idhab2,
        "Oferta Laboral": p.oferta.nombre,
        "Apto": "Apto" if p.aptitud is True else ("No apto" if p.aptitud is False else "Sin revisar"),
        "Puntaje": p.puntaje
    } for p in postulaciones])

    # Mapear nombres de educación, tecnología y habilidades como ya lo hacías
    educacion_map = {edu.idedu: edu.nombre for edu in Educacion.query.all()}
    tecnologia_map = {tec.idtec: tec.nombre for tec in Tecnologia.query.all()}
    habilidad_map = {hab.idhab: hab.nombre for hab in Habilidad.query.all()}
    tecnologia2_map = {tec2.idtec2: tec2.nombre for tec2 in Tecnologia2.query.all()}
    habilidad2_map = {hab2.idhab2: hab2.nombre for hab2 in Habilidad2.query.all()}

    dataSet["Educacion"] = dataSet["Educacion"].map(educacion_map)
    dataSet["Tecnologías"] = dataSet["Tecnologías"].map(tecnologia_map)
    dataSet["Habilidades"] = dataSet["Habilidades"].map(habilidad_map)
    dataSet["Tecnologías2"] = dataSet["Tecnologías2"].map(tecnologia2_map)
    dataSet["Habilidades2"] = dataSet["Habilidades2"].map(habilidad2_map)

    # Aplicar filtro por aptitud si está activado
    if filtro == "apto":
        dataSet = dataSet[dataSet["Apto"] == "Apto"]

    dataSet = dataSet.rename(columns={    
    "Tecnologías": "Tecnología Principal",
    "Habilidades": "Habilidad 1",
    "Tecnologías2": "Tecnología Secundaria",
    "Habilidades2": "Habilidad 2"
})

    tabla_html = dataSet.to_html(classes="table table-striped", index=False)
    return render_template("postulantes.html", tabla=tabla_html, ofertas=OfertaLaboral.query.all(), idOfer=idOfer)


def predecir_postulantes_automatica(idOfer):
    # 📌 Obtener las postulaciones de la oferta
    postulaciones = Postulacion.query.filter_by(idOfer=idOfer).all()

    if not postulaciones:
        return

    modelo = joblib.load(get_path("modelo_candidatos.pkl"))

    X = pd.DataFrame([{
        "Educacion": p.candidato.idedu,
        "Tecnologías": p.candidato.idtec,
        "Tecnologías2": p.candidato.idtec2,
        "Habilidades": p.candidato.idhab,
        "Habilidades2": p.candidato.idhab2
    } for p in postulaciones])

    predicciones = modelo.predict(X)

    for i, postulacion in enumerate(postulaciones):
        postulacion.aptitud = bool(predicciones[i])  #  Ahora asignamos `aptitud` a `Postulacion`, no `Candidato`
        db.session.add(postulacion)

    db.session.commit()


def asignar_puntajes_automatica(idOfer):
    postulaciones = Postulacion.query.filter_by(idOfer=idOfer, aptitud=True).all()  #  Filtrar postulaciones aptas

    if not postulaciones:
        return

    for p in postulaciones:
        p.puntaje = calcular_puntaje(p.candidato)  #  Asignamos puntaje a la `Postulacion`, no a `Candidato`
        db.session.add(p)  #  Agregamos la postulación actualizada

    db.session.commit()  #  Guardamos cambios en la base de datos



def enviar_correos_automatica(idOfer):
    destinatariosAptos = obtener_correos_aptos(idOfer)
    destinatariosNoAptos = obtener_correos_noaptos(idOfer)

    with email.connect() as conn:
        for nombre, mail in destinatariosAptos:
            mensaje = Message(
                subject="Oportunidad laboral",
                sender=app.config["MAIL_USERNAME"],
                recipients=[mail],
                body=f"Hola {nombre},\n\nHemos revisado tu perfil y estamos interesados en tu candidatura.\n¡Gracias por postularte!")
            conn.send(mensaje)

        for nombre, mail in destinatariosNoAptos:
            mensaje = Message(
                subject="Oportunidad laboral",
                sender=app.config["MAIL_USERNAME"],
                recipients=[mail],
                body=f"Hola {nombre},\n\nLamentamos informarte que en esta oportunidad tu perfil no se ajusta a lo que buscamos.\nTe animamos a postularte en futuras oportunidades.")
            conn.send(mensaje)


@app.route("/predecir_postulantes", methods=["POST"])
@login_required(roles=["Admin_RRHH"])
def predecir_postulantes():
    try:
        # Cargar los candidatos existentes
        candidatos = Candidato.query.all()

        # Crear un DataFrame con los datos de los candidatos
        dataSet = pd.DataFrame([{
            "Nombre": c.nombre,
            "Apellido": c.apellido,
            "Email": c.id,
            "Telefono": c.telefono,
            "Ubicacion": c.ubicacion,
            "Experiencia": c.experiencia,
            "Educacion": c.idedu,
            "Tecnologías": c.idtec,
            "Habilidades": c.idhab,
            "Tecnologías2": c.idtec2,
            "Habilidades2": c.idhab2,
            "Apto": c.aptitud if c.aptitud else "sin revisar",
            "Puntaje": c.puntaje
        } for c in candidatos])

        # Cargar el modelo entrenado
        modelo = joblib.load(get_path("modelo_candidatos.pkl"))

        # Verificar que las columnas necesarias estén presentes
        columnas_requeridas = ["Educacion", "Tecnologías", "Tecnologías2", "Habilidades", "Habilidades2"]
        for columna in columnas_requeridas:
            if columna not in dataSet.columns:
                return f"Falta la columna requerida: {columna}"

        # Realizar predicciones
        X = dataSet[["Educacion", "Tecnologías", "Tecnologías2", "Habilidades", "Habilidades2"]]
        predicciones = modelo.predict(X)

        # Guardar las predicciones en la base de datos
        for i, candidato in enumerate(candidatos):
            candidato.aptitud = predicciones[i] == 1  # True si es "Apto", False en caso contrario
            db.session.add(candidato)

        db.session.commit()  # Confirmar los cambios en la base de datos

        # Mapear valores a nombres descriptivos para visualización
        educacion_map = {edu.idedu: edu.nombre for edu in Educacion.query.all()}
        Tecnologia_map = {tec.idtec: tec.nombre for tec in Tecnologia.query.all()}
        habilidad_map = {hab.idhab: hab.nombre for hab in Habilidad.query.all()}
        Tecnologia2_map = {tec2.idtec2: tec2.nombre for tec2 in Tecnologia2.query.all()}
        habilidad2_map = {hab2.idhab2: hab2.nombre for hab2 in Habilidad2.query.all()}

        dataSet["Educacion"] = dataSet["Educacion"].map(educacion_map)
        dataSet["Tecnologías"] = dataSet["Tecnologías"].map(Tecnologia_map)
        dataSet["Habilidades"] = dataSet["Habilidades"].map(habilidad_map)
        dataSet["Tecnologías2"] = dataSet["Tecnologías2"].map(Tecnologia2_map)
        dataSet["Habilidades2"] = dataSet["Habilidades2"].map(habilidad2_map)

        # Actualizar el DataFrame con las predicciones
        dataSet["Apto"] = ["Apto" if pred == 1 else "No Apto" for pred in predicciones]
        columnasOrdenadas = [col for col in dataSet.columns if col != "Apto"] + ["Apto"]
        dataSet = dataSet[columnasOrdenadas]

        # Generar tabla HTML para mostrar en la página
        tabla_html = dataSet.to_html(classes="table table-striped", index=False)
        return render_template("postulantes.html", tabla=tabla_html)

    except Exception as e:
        return f"Ocurrió un error al predecir sobre los postulantes: {e}"


@app.route('/asignar_puntajes', methods=["GET", "POST"])
@login_required(roles=["Admin_RRHH"])
def asignar_puntajes():
    candidatos = Candidato.query.filter_by(aptitud=True).all()
    for c in candidatos:
        c.puntaje = calcular_puntaje(c)
    db.session.commit()
    if has_request_context():
        flash('Puntajes asignados correctamente.', 'success')
        return redirect(url_for('postulantes'))

def calcular_puntaje(candidato):
    puntaje = 0

    puntaje += candidato.experiencia * 2

    # 📌 Obtener la postulación más reciente del candidato
    postulacion = Postulacion.query.filter_by(idCandidato=candidato.id).order_by(Postulacion.idPostulacion.desc()).first()

    if postulacion:  # 🔹 Verificar que hay una postulación válida
        # Obtener la importancia desde OfertaEducacion
        edu_rel = OfertaEducacion.query.filter_by(idOfer=postulacion.idOfer, idEdu=candidato.idedu).first()
        if edu_rel:
            puntaje += edu_rel.importancia * 3

        # Obtener la importancia desde OfertaTecnologia
        tec_rel = OfertaTecnologia.query.filter_by(idOfer=postulacion.idOfer, idTec=candidato.idtec).first()
        if tec_rel:
            puntaje += tec_rel.importancia * 5
            
        tec2_rel = OfertaTecnologia2.query.filter_by(idOfer=postulacion.idOfer, idTec2=candidato.idtec2).first()
        if tec2_rel:
            puntaje += tec2_rel.importancia * 5

        # Obtener la importancia desde OfertaHabilidad
        hab_rel = OfertaHabilidad.query.filter_by(idOfer=postulacion.idOfer, idHab=candidato.idhab).first()
        if hab_rel:
            puntaje += hab_rel.importancia * 2
            
        hab2_rel = OfertaHabilidad2.query.filter_by(idOfer=postulacion.idOfer, idHab2=candidato.idhab2).first()
        if hab2_rel:
            puntaje += hab2_rel.importancia * 2

    return puntaje



def extraer_info_cv_pdf(file_storage):
    texto = ""
    with fitz.open(stream=file_storage.read(), filetype="pdf") as doc:
        for pagina in doc:
            texto += pagina.get_text()

    info = {}

    # Email
    email = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", texto)
    if email:
        info['email'] = email.group().lower()

    # Teléfono
    telefono = re.search(
        r"(?:\+54\s?|54\s?|0)?(?:\(?\d{2,4}\)?)[\s.-]{0,2}"      # Prefijo y área
        r"(?:15[\s.-]{0,2})?"                                     # Prefijo celular
        r"\d{3,4}[\s.-]?\d{4}",                                   # Número principal
        texto
    )
    if telefono:
        numero = re.sub(r"\D", "", telefono.group())  # quitar todo lo que no sea dígito
        if len(numero) >= 8:
            info["telefono"] = numero


    # Nombre y Apellido con validación en una o dos líneas en MAYÚSCULAS
    def es_nombre_o_apellido_valido(palabra):
        return palabra.isalpha() and (palabra.istitle() or palabra.isupper())

    lineas = texto.strip().split("\n")
    primeras_lineas = lineas[:5]  # Priorizamos las primeras líneas

    nombre, apellido = None, None

    # Paso 1: Revisar la primera línea
    primera_linea = primeras_lineas[0].strip()
    if primera_linea.isupper() and all(p.isalpha() for p in primera_linea.split()):
        palabras = primera_linea.split()
        if len(palabras) >= 2:
            nombre = " ".join(palabras[:2]).title()
            apellido = " ".join(palabras[2:4]).title() if len(palabras) > 2 else ""

    # Paso 2: Buscar nombres y apellidos en dos líneas consecutivas si no se encontraron antes
    if not nombre or not apellido:
        for i in range(len(primeras_lineas) - 1):
            palabras_actual = primeras_lineas[i].strip().split()
            palabras_siguiente = primeras_lineas[i + 1].strip().split()

            validas_actual = [p for p in palabras_actual if es_nombre_o_apellido_valido(p)]
            validas_siguiente = [p for p in palabras_siguiente if es_nombre_o_apellido_valido(p)]

            if len(validas_actual) >= 1 and len(validas_siguiente) >= 1:
                nombre = " ".join(validas_actual).title()
                apellido = " ".join(validas_siguiente).title()
                break

    # Paso 3: Si sigue sin detectarse, buscar en una sola línea
    if not nombre or not apellido:
        for linea in primeras_lineas:
            palabras = linea.strip().split()
            validas = [p for p in palabras if es_nombre_o_apellido_valido(p)]
            if len(validas) >= 2:
                nombre = " ".join(validas[:2]).title()
                apellido = " ".join(validas[2:4]).title() if len(validas) > 2 else ""
                break

    if nombre:
        info["nombre"] = nombre
    if apellido:
        info["apellido"] = apellido

    # Educación
    niveles_equivalentes = {
        "postgrado": ["postgrado", "maestría", "doctorado", "posgrado"],
        "universitario": ["universitario", "universidad", "universitaria", "licenciatura", "ingeniería", "ingeniero", "grado"],
        "secundario": ["secundario", "bachiller", "escuela secundaria", "nivel medio"]
    }

    for nivel, palabras_clave in niveles_equivalentes.items():
        for palabra in palabras_clave:
            if palabra in texto.lower():
                # Detectar si está "en curso"
                if re.search(fr"{palabra}.*(finalizado|completado|terminado|graduado|concluido|egresado)", texto.lower()):
                    info["educacion"] = nivel
                else:
                    info["educacion"] = f"{nivel}(encurso)"
                break
        if "educacion" in info:
            break

    # Tecnologías (primeras 2 coincidencias reales)
    # Obtener todas las tecnologías
    tecnologias = [t.nombre for t in Tecnologia.query.all()]
    texto_lower = texto.lower()

    # Armar expresión regular con todas las tecnologías escapadas
    patron_tec = r"(?:\b|[^a-zA-Z])(" + "|".join(re.escape(t.lower()) for t in tecnologias) + r")(?:\b|[^a-zA-Z])"

    # Buscar todas las coincidencias con sus posiciones
    coincidencias_tec = []
    for match in re.finditer(patron_tec, texto_lower):
        tecnologia_encontrada = match.group(1)
        # Evitar duplicados y mantener orden de aparición
        if tecnologia_encontrada not in coincidencias_tec:
            coincidencias_tec.append(tecnologia_encontrada)

    # Mapear nombres encontrados a nombres originales
    tec_encontradas = []
    for encontrada in coincidencias_tec:
        for tec in tecnologias:
            if tec.lower() == encontrada:
                tec_encontradas.append(tec)
                break
        if len(tec_encontradas) == 2:
            break

    if tec_encontradas:
        info["tecnologias"] = tec_encontradas[0]
        if len(tec_encontradas) > 1:
            info["tecnologias2"] = tec_encontradas[1]

    # Habilidades (primeras 2 que matcheen)
    habilidades = [h.nombre for h in Habilidad.query.all()]
    patron_hab = r"(?:\b|[^a-zA-Z])(" + "|".join(re.escape(h.lower()) for h in habilidades) + r")(?:\b|[^a-zA-Z])"

    coincidencias_hab = []
    for match in re.finditer(patron_hab, texto_lower):
        habilidad_encontrada = match.group(1)
        if habilidad_encontrada not in coincidencias_hab:
            coincidencias_hab.append(habilidad_encontrada)

    hab_encontradas = []
    for encontrada in coincidencias_hab:
        for hab in habilidades:
            if hab.lower() == encontrada:
                hab_encontradas.append(hab)
                break
        if len(hab_encontradas) == 2:
            break

    if hab_encontradas:
        info["habilidades"] = hab_encontradas[0]
        if len(hab_encontradas) > 1:
            info["habilidades2"] = hab_encontradas[1]

    # Ubicación (primera provincia argentina encontrada)
    provincias = [
        "Buenos Aires", "CABA", "Catamarca", "Chaco", "Chubut",
        "Córdoba", "Corrientes", "Entre Ríos", "Formosa", "Jujuy", "La Pampa", "La Rioja",
        "Mendoza", "Misiones", "Neuquén", "Río Negro", "Salta", "San Juan", "San Luis",
        "Santa Cruz", "Santa Fe", "Santiago del Estero", "Tierra del Fuego", "Tucumán"
    ]
    for prov in provincias:
        if prov.lower() in texto.lower():
            info["ubicacion"] = prov
            break

    # Estimar experiencia laboral a partir de rangos de años luego de la palabra "experiencia"
    texto_lower = texto.lower()
    indice_exp = texto_lower.find("experiencia")

    if indice_exp != -1:
        texto_despues_exp = texto_lower[indice_exp:]

        # Cortar si se menciona algo educativo
        palabras_corte = ["universidad", "licenciatura", "ingeniería", "educación", "estudios", "colegio", "título", "egresado"]
        for palabra in palabras_corte:
            corte_idx = texto_despues_exp.find(palabra)
            if corte_idx != -1:
                texto_despues_exp = texto_despues_exp[:corte_idx]
                break

        total_experiencia = 0
        anio_actual = 2025

        # Rango explícito (ej: "2015 - 2018", "2012 a 2014")
        patron_rango = r"(20(0[9]|1[0-9]|2[0-5]))\s*(?:-|–|—|a|hasta)\s*(20(0[9]|1[0-9]|2[0-5]))"
        for match in re.findall(patron_rango, texto_despues_exp):
            try:
                inicio = int(match[0])
                fin = int(match[2])
                if inicio < fin:
                    total_experiencia += (fin - inicio)
            except ValueError:
                continue

        # Rango abierto (ej: "2018 a actualidad", "2016 hasta hoy")
        patron_abierto = r"(20(0[9]|1[0-9]|2[0-5]))\s*(?:-|–|—|a|hasta)\s*(actualidad|presente|hoy|actual)"
        for match in re.findall(patron_abierto, texto_despues_exp):
            try:
                inicio = int(match[0])
                fin = anio_actual
                if inicio < fin:
                    total_experiencia += (fin - inicio)
            except ValueError:
                continue

        if total_experiencia >= 1:
            info["experiencia"] = total_experiencia

    return info


@app.route("/cargarCV", methods=["GET", "POST"])
@login_required(roles=["Admin_RRHH"])
def cargarCV():
    opciones_ofertas = [{"idOfer": oferta.idOfer, "nombre": oferta.nombre} for oferta in OfertaLaboral.query.filter(OfertaLaboral.estado != "Cerrada").all()]
    opciones_educacion = [educacion.nombre for educacion in Educacion.query.all()]
    opciones_tecnologias = [tecnologia.nombre for tecnologia in Tecnologia.query.all()]
    opciones_habilidades = [habilidad.nombre for habilidad in Habilidad.query.all()]
    opciones_tecnologias2 = [tecnologia2.nombre for tecnologia2 in Tecnologia2.query.all()]
    opciones_habilidades2 = [habilidad2.nombre for habilidad2 in Habilidad2.query.all()]

    session["opciones_ofertas"] = opciones_ofertas
    session["opciones_educacion"] = opciones_educacion
    session["opciones_tecnologias"] = opciones_tecnologias
    session["opciones_habilidades"] = opciones_habilidades
    session["opciones_tecnologias2"] = opciones_tecnologias2
    session["opciones_habilidades2"] = opciones_habilidades2

    if request.method == "POST":
        if "cv_pdf" in request.files:
            file = request.files["cv_pdf"]
            if file and file.filename.endswith(".pdf"):
                # revisar si pesa menos de 5MB:
                file.seek(0, os.SEEK_END)
                size = file.tell()
                file.seek(0)
               
                if size > 5 * 1024 * 1024:
                    flash("❌El archivo excede el tamaño máximo permitido de 5 MB.", category="pdf")
                    return redirect("/cargarCV")
                
                try:
                    info = extraer_info_cv_pdf(file)
                    flash("✔️Información extraída exitosamente del archivo PDF.", category="pdf")
                    return render_template(
                        "cargarCV.html",
                        opciones_ofertas=opciones_ofertas,
                        opciones_educacion=opciones_educacion,
                        opciones_tecnologias=opciones_tecnologias,
                        opciones_habilidades=opciones_habilidades,
                        opciones_tecnologias2=opciones_tecnologias2,
                        opciones_habilidades2=opciones_habilidades2,
                        precargado=info
                    )
                except Exception:
                    flash("❌El archivo no es un PDF válido o está dañado.", category="pdf")
                    return redirect("/cargarCV")
            else:
                flash("❌Debes seleccionar un archivo PDF válido para continuar.", category="pdf")
                return redirect("/cargarCV")

        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        email = request.form["email"]
        telefono = request.form["telefono"]
        ubicacion = request.form["ubicacion"]
        experiencia = int(request.form["experiencia"])
        educacion = request.form["educacion"]
        tecnologias = request.form["tecnologias"]
        habilidades = request.form["habilidades"]
        tecnologias2 = request.form["tecnologias2"]
        habilidades2 = request.form["habilidades2"]
        idOfer = request.form.get("idOfer")

        if not idOfer:
            flash("Debes seleccionar una oferta laboral.", category="form")
            return redirect("/cargarCV")

        try:
            oferta = OfertaLaboral.query.get(idOfer)

            if oferta.estado == "Cerrada":
                flash("❌La oferta ya alcanzó el máximo de postulaciones.", category="form")
                return redirect("/cargarCV")

            candidato = Candidato.query.filter_by(mail=email).first()

            educacion_obj = Educacion.query.filter_by(nombre=educacion).first()
            tecnologia_obj = Tecnologia.query.filter_by(nombre=tecnologias).first()
            habilidad_obj = Habilidad.query.filter_by(nombre=habilidades).first()
            tecnologia2_obj = Tecnologia2.query.filter_by(nombre=tecnologias2).first()
            habilidad2_obj = Habilidad2.query.filter_by(nombre=habilidades2).first()

            if not educacion_obj or not tecnologia_obj or not habilidad_obj or not tecnologia2_obj or not habilidad2_obj:
                flash("Error: Valores inválidos seleccionados.")
                return redirect("/cargarCV")

            if candidato:
                candidato.experiencia = experiencia
                candidato.idedu = educacion_obj.idedu
                candidato.idtec = tecnologia_obj.idtec
                candidato.idtec2 = tecnologia2_obj.idtec2
                candidato.idhab = habilidad_obj.idhab
                candidato.idhab2 = habilidad2_obj.idhab2
                db.session.add(candidato)
            else:
                candidato = Candidato(
                    id=email,
                    nombre=nombre,
                    apellido=apellido,
                    mail=email,
                    telefono=telefono,
                    ubicacion=ubicacion,
                    experiencia=experiencia,
                    idedu=educacion_obj.idedu,
                    idtec=tecnologia_obj.idtec,
                    idtec2=tecnologia2_obj.idtec2,
                    idhab=habilidad_obj.idhab,
                    idhab2=habilidad2_obj.idhab2
                )
                db.session.add(candidato)

            # Validación de postulación duplicada
            if Postulacion.query.filter_by(idCandidato=candidato.id, idOfer=idOfer).first():
                flash("❌Este candidato ya estaba postulado a la oferta seleccionada.", category="form")
                return redirect("/cargarCV")

            nueva_postulacion = Postulacion(
                idCandidato=candidato.id,
                idOfer=idOfer,
                experiencia=experiencia,
                idedu=educacion_obj.idedu,
                idtec=tecnologia_obj.idtec,
                idtec2=tecnologia2_obj.idtec2,
                idhab=habilidad_obj.idhab,
                idhab2=habilidad2_obj.idhab2,
                aptitud=None,
                puntaje=0
            )
            db.session.add(nueva_postulacion)

            oferta.cant_candidatos += 1
            db.session.add(oferta)
            db.session.commit()

            if oferta.cant_candidatos >= oferta.max_candidatos:
                cerrar_url = request.host_url.rstrip("/") + url_for("cerrar_oferta", idOfer=oferta.idOfer)
                try:
                    requests.post(cerrar_url, cookies=request.cookies)
                except Exception as e:
                    flash("⚠️ No se pudo cerrar automáticamente la oferta. Intentalo manualmente.", "warning")

            
            flash(f"✔️Postulación de {nombre} registrada en la oferta '{oferta.nombre}'.", category="form")

        except Exception as e:
            flash("❌Error al procesar la postulación.", category="form")
            return redirect("/cargarCV")
        
    opciones_ofertas = [{"idOfer": o.idOfer, "nombre": o.nombre} for o in OfertaLaboral.query.filter(OfertaLaboral.estado != "Cerrada").all()]
    return render_template(
        "cargarCV.html",
        opciones_ofertas=session["opciones_ofertas"],
        opciones_educacion=session["opciones_educacion"],
        opciones_tecnologias=session["opciones_tecnologias"],
        opciones_habilidades=session["opciones_habilidades"],
        opciones_tecnologias2=session["opciones_tecnologias2"],
        opciones_habilidades2=session["opciones_habilidades2"]
    )




@app.route("/etiquetas", methods=["GET", "POST"])
@login_required(roles=["Admin_RRHH"])
def mostrar_etiquetas(idOfer=None):
    ofertas = OfertaLaboral.query.all()
    ofertas_activas = OfertaLaboral.query.filter_by(estado="Activa").all()
    
    if not idOfer:
        idOfer = request.form.get("idOfer") if request.method == "POST" else request.args.get("idOfer")
        if not idOfer and ofertas:
            idOfer = ofertas[0].idOfer  

    educaciones, tecnologias, habilidades, tecnologias2, habilidades2 = [], [], [], [], []

    if idOfer:
        oferta = OfertaLaboral.query.get(idOfer)
        educaciones = OfertaEducacion.query.filter_by(idOfer=idOfer).all()
        tecnologias = OfertaTecnologia.query.filter_by(idOfer=idOfer).all()
        habilidades = OfertaHabilidad.query.filter_by(idOfer=idOfer).all()
        tecnologias2 = OfertaTecnologia2.query.filter_by(idOfer=idOfer).all()
        habilidades2 = OfertaHabilidad2.query.filter_by(idOfer=idOfer).all()

        # 📌 Generar DataFrames con datos recién recuperados
        df_edu = pd.DataFrame([{"Nombre": e.educacion.nombre, "Valor": e.importancia} for e in educaciones]) if educaciones else pd.DataFrame()
        df_tec = pd.DataFrame([{"Nombre": t.tecnologia.nombre, "Valor": t.importancia} for t in tecnologias]) if tecnologias else pd.DataFrame()
        df_hab = pd.DataFrame([{"Nombre": h.habilidad.nombre, "Valor": h.importancia} for h in habilidades]) if habilidades else pd.DataFrame()
        df_tec2 = pd.DataFrame([{"Nombre": t2.tecnologia2.nombre, "Valor": t2.importancia} for t2 in tecnologias2]) if tecnologias2 else pd.DataFrame()
        df_hab2 = pd.DataFrame([{"Nombre": h2.habilidad2.nombre, "Valor": h2.importancia} for h2 in habilidades2]) if habilidades2 else pd.DataFrame()

        # 📌 Convertir DataFrames a tablas HTML
        tabla_edu = df_edu.to_html(classes="table table-bordered", index=False) if not df_edu.empty else "<p>No hay etiquetas de educación</p>"
        tabla_tec = df_tec.to_html(classes="table table-bordered", index=False) if not df_tec.empty else "<p>No hay etiquetas de tecnología</p>"
        tabla_tec2 = df_tec2.to_html(classes="table table-bordered", index=False) if not df_tec2.empty else "<p>No hay etiquetas de tecnología secundaria</p>"
        tabla_hab = df_hab.to_html(classes="table table-bordered", index=False) if not df_hab.empty else "<p>No hay etiquetas de habilidades</p>"
        tabla_hab2 = df_hab2.to_html(classes="table table-bordered", index=False) if not df_hab2.empty else "<p>No hay etiquetas de habilidades secundarias</p>"
    else:
        oferta, tabla_edu, tabla_tec, tabla_tec2, tabla_hab, tabla_hab2 = None, "", "", "", "", ""

    return render_template("etiquetas.html",
                           ofertas=ofertas,
                           ofertas_activas=ofertas_activas,
                           oferta=oferta,
                           idOfer=idOfer,  
                           tabla_edu=tabla_edu,
                           tabla_tec=tabla_tec,
                           tabla_hab=tabla_hab,
                           tabla_tec2=tabla_tec2,
                           tabla_hab2=tabla_hab2,
                           educaciones=educaciones,
                           tecnologias=tecnologias,
                           habilidades=habilidades,
                           tecnologias2=tecnologias2,
                           habilidades2=habilidades2)


@app.route("/importancia/<tipo>/<int:id>", methods=["POST"])
@login_required(roles=["Admin_RRHH"])
def actualizar_importancia(tipo, id):
    data = request.get_json()
    importancia = int(data["importancia"])

    modelos = {
        "educacion": OfertaEducacion,
        "tecnologia": OfertaTecnologia,
        "tecnologia2": OfertaTecnologia2,
        "habilidad": OfertaHabilidad,
        "habilidad2": OfertaHabilidad2
    }

    modelo = modelos.get(tipo)
    if not modelo:
        return jsonify({"error": "Tipo inválido"}), 400

    relacion = db.session.get(modelo, id)
    if not relacion:
        return jsonify({"error": "Etiqueta no encontrada"}), 404

    relacion.importancia = importancia
    db.session.commit()
    return jsonify({"ok": True})


@app.route("/asignar_valores/<int:idOfer>", methods=["POST"])
@login_required(roles=["Admin_RRHH"])
def asignar_valores(idOfer):
    oferta = OfertaLaboral.query.get(idOfer)
    if not oferta:
        flash("Oferta no encontrada", "error")
        return redirect(url_for("ver_ofertas"))
    # 📌 Educación
    educacion_id = request.form.get("educacion_id")
    valor_educacion = request.form.get("valor_educacion")
    if valor_educacion:
        edu_rel = OfertaEducacion.query.filter_by(idOfer=idOfer, idEdu=educacion_id).first()
        if edu_rel:
            edu_rel.importancia = int(valor_educacion)

    # 📌 Tecnología
    tecnologia_id = request.form.get("tecnologia_id")
    valor_tecnologia = request.form.get("valor_tecnologia")
    if valor_tecnologia:
        tec_rel = OfertaTecnologia.query.filter_by(idOfer=idOfer, idTec=tecnologia_id).first()
        if tec_rel:
            tec_rel.importancia = int(valor_tecnologia)

    # 📌 Tecnología secundaria
    tecnologia2_id = request.form.get("tecnologia2_id")
    valor_tecnologia2 = request.form.get("valor_tecnologia2")
    if valor_tecnologia2:
        tec2_rel = OfertaTecnologia2.query.filter_by(idOfer=idOfer, idTec2=tecnologia2_id).first()
        if tec2_rel:
            tec2_rel.importancia = int(valor_tecnologia2)

    # 📌 Habilidad
    habilidad_id = request.form.get("habilidad_id")
    valor_habilidad = request.form.get("valor_habilidad")
    if valor_habilidad:
        hab_rel = OfertaHabilidad.query.filter_by(idOfer=idOfer, idHab=habilidad_id).first()
        if hab_rel:
            hab_rel.importancia = int(valor_habilidad)

    # 📌 Habilidad secundaria
    habilidad2_id = request.form.get("habilidad2_id")
    valor_habilidad2 = request.form.get("valor_habilidad2")
    if valor_habilidad2:
        hab2_rel = OfertaHabilidad2.query.filter_by(idOfer=idOfer, idHab2=habilidad2_id).first()
        if hab2_rel:
            hab2_rel.importancia = int(valor_habilidad2)

    db.session.commit()
    flash("Importancia actualizada correctamente", "success")

    return mostrar_etiquetas(idOfer)


@app.route("/metricas")
@login_required(roles=["Admin_RRHH"])
def metricas():
    ofertas = OfertaLaboral.query.all()
    return render_template("metricas.html", ofertas=ofertas)


    
@app.route("/metricas/<int:oferta_id>")
@login_required(roles=["Admin_RRHH"])
def obtener_metricas(oferta_id):
    oferta = OfertaLaboral.query.get_or_404(oferta_id)

    def obtener_datos_por_etiqueta(query, nombre_func):
        etiquetas = []
        cantidades = []
        promedios = {}
        for rel in query:
            etiqueta = nombre_func(rel)
            postulaciones = Postulacion.query.filter_by(idOfer=oferta_id, **etiqueta["filtro"]).all()  #  Ahora sobre `Postulacion`
            etiquetas.append(etiqueta["nombre"])
            cantidades.append(len(postulaciones))
            promedios[etiqueta["nombre"]] = (
                sum(p.experiencia for p in postulaciones) / len(postulaciones) if postulaciones else 0
            )
        return etiquetas, cantidades, promedios

    # 📌 Educación
    edu_etiquetas, edu_cant, edu_exp = obtener_datos_por_etiqueta(
        oferta.educaciones,
        lambda rel: {"nombre": rel.educacion.nombre, "filtro": {"idedu": rel.idEdu}}
    )

    # 📌 Tecnología
    tec_etiquetas, tec_cant, tec_exp = obtener_datos_por_etiqueta(
        oferta.tecnologias,
        lambda rel: {"nombre": rel.tecnologia.nombre, "filtro": {"idtec": rel.idTec}}
    )
    
    tec2_etiquetas, tec2_cant, tec2_exp = obtener_datos_por_etiqueta(
        oferta.tecnologias2,
        lambda rel: {"nombre": rel.tecnologia2.nombre, "filtro": {"idtec2": rel.idTec2}}
    )

    # 📌 Habilidad
    hab_etiquetas, hab_cant, hab_exp = obtener_datos_por_etiqueta(
        oferta.habilidades,
        lambda rel: {"nombre": rel.habilidad.nombre, "filtro": {"idhab": rel.idHab}}
    )
    
    hab2_etiquetas, hab2_cant, hab2_exp = obtener_datos_por_etiqueta(
        oferta.habilidades2,
        lambda rel: {"nombre": rel.habilidad2.nombre, "filtro": {"idhab2": rel.idHab2}}
    )

    # 📌 Provincias
    provincias_postulantes = {}
    for p in Postulacion.query.filter_by(idOfer=oferta_id).all():
        prov = p.candidato.ubicacion  #  Ahora accedemos desde `Postulacion.candidato`
        provincias_postulantes[prov] = provincias_postulantes.get(prov, 0) + 1

    # 📌 Totales
    total_postulantes = Postulacion.query.filter_by(idOfer=oferta_id).count()
    aptos = Postulacion.query.filter_by(idOfer=oferta_id, aptitud=True).count()
    no_aptos = Postulacion.query.filter_by(idOfer=oferta_id, aptitud=False).count()
    sin_revisar = Postulacion.query.filter_by(idOfer=oferta_id, aptitud=None).count()

    return jsonify({
        "etiquetas_educacion": edu_etiquetas,
        "cant_educacion": edu_cant,
        "exp_educacion": edu_exp,

        "etiquetas_tecnologia": tec_etiquetas,
        "cant_tecnologia": tec_cant,
        "exp_tecnologia": tec_exp,
        
        "etiquetas_tecnologia2": tec2_etiquetas,
        "cant_tecnologia2": tec2_cant,
        "exp_tecnologia2": tec2_exp,

        "etiquetas_habilidad": hab_etiquetas,
        "cant_habilidad": hab_cant,
        "exp_habilidad": hab_exp,
        
        "etiquetas_habilidad2": hab2_etiquetas,
        "cant_habilidad2": hab2_cant,
        "exp_habilidad2": hab2_exp,

        "total_postulantes": total_postulantes,
        "aptos": aptos,
        "no_aptos": no_aptos,
        "sin_revisar": sin_revisar,

        "provincias_postulantes": provincias_postulantes
    })
@app.route('/eliminar_oferta/<int:idOfer>', methods=['POST'])
@login_required(roles=["Admin_RRHH"])
def eliminar_oferta(idOfer):
    oferta = OfertaLaboral.query.get_or_404(idOfer)
    db.session.delete(oferta)
    db.session.commit()
    flash("Oferta eliminada correctamente.", "success")
    return redirect(url_for('predecir'))


if __name__ == "__main__":
    threading.Timer(1.5, abrir_navegador).start() 
    app.run(debug=True, host="127.0.0.1", port=5000)
