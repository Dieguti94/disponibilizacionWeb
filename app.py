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
    id = db.Column(db.String(150), primary_key=True)  # Usamos el correo como ID único
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    mail = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(50), nullable=False)
    ubicacion = db.Column(db.String(100), nullable=False)
    experiencia = db.Column(db.Integer, nullable=False)
    idedu = db.Column(db.Integer, db.ForeignKey('educacion.idedu'))
    idtec = db.Column(db.Integer, db.ForeignKey('tecnologia.idtec'))
    idhab = db.Column(db.Integer, db.ForeignKey('habilidad.idhab'))
    idOfer = db.Column(db.Integer, db.ForeignKey('oferta_laboral.idOfer'))
    aptitud = db.Column(db.Boolean, nullable=True)
    puntaje = db.Column(db.Integer, nullable=False, default=0)

    oferta = db.relationship('OfertaLaboral', back_populates='candidatos') 

    
class OfertaLaboral(db.Model):
    __tablename__ = 'oferta_laboral'
    
    idOfer = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(200), nullable=False, unique=True)
    fecha_cierre = db.Column(db.DateTime, nullable=False)
    max_candidatos = db.Column(db.Integer, nullable=False)
    remuneracion = db.Column(db.String(50), nullable=False)  
    beneficio = db.Column(db.String(200), nullable=True)  
    estado = db.Column(db.String(50), nullable=False, default="Activa")  
    usuario_responsable = db.Column(db.String(100), nullable=False)  

    # Relaciones
    candidatos = db.relationship('Candidato', back_populates='oferta', lazy=True)
    educaciones = db.relationship('OfertaEducacion', back_populates='oferta', lazy=True)
    tecnologias = db.relationship('OfertaTecnologia', back_populates='oferta', lazy=True)
    habilidades = db.relationship('OfertaHabilidad', back_populates='oferta', lazy=True)


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

class OfertaHabilidad(db.Model):
    __tablename__ = 'oferta_habilidad'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idOfer = db.Column(db.Integer, db.ForeignKey('oferta_laboral.idOfer'))
    idHab = db.Column(db.Integer, db.ForeignKey('habilidad.idhab'))
    importancia = db.Column(db.Integer, nullable=False)

    oferta = db.relationship('OfertaLaboral', back_populates='habilidades')
    habilidad = db.relationship('Habilidad')

class Educacion(db.Model):
    __tablename__ = 'educacion'
    idedu = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)


class Tecnologia(db.Model):
    __tablename__ = 'tecnologia'
    idtec = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)


class Habilidad(db.Model):
    __tablename__ = 'habilidad'
    idhab = db.Column(db.Integer, primary_key=True)
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


"""
# Crear la base de datos y agregar usuarios ficticios si no existen
#if not os.path.exists("erp_rrhh.db"):
with app.app_context():
    db.create_all()
    # Agregar usuarios ficticios
    # Cargar los encoders
    encoder_educacion = joblib.load(get_path("encoder_educacion.pkl"))
    encoder_tecnologias = joblib.load(get_path("encoder_tecnologias.pkl"))
    encoder_habilidades = joblib.load(get_path("encoder_habilidades.pkl"))

    # Insertar las clases en la tabla intermedia de 'OfertaEducacion'
    for idx, clase in enumerate(encoder_educacion.classes_):
        nueva_educacion = Educacion(
            idedu=idx,  # El índice asignado por el encoder será el ID
            nombre=clase
        )
        db.session.merge(nueva_educacion)  # Merge para evitar duplicados

    # Insertar las clases en la tabla intermedia de 'OfertaTecnologia'
    for idx, clase in enumerate(encoder_tecnologias.classes_):
        nueva_tecnologia = Tecnologia(
            idtec=idx,
            nombre=clase
        )
        db.session.merge(nueva_tecnologia)

    # Insertar las clases en la tabla intermedia de 'OfertaHabilidad'
    for idx, clase in enumerate(encoder_habilidades.classes_):
        nueva_habilidad = Habilidad(
            idhab=idx,
            nombre=clase
        )
        db.session.merge(nueva_habilidad)

    # Confirmar los cambios
    db.session.commit()
    print("Clases cargadas automáticamente en la base de datos.")
    usuario_admin = Usuario(username="Fernando", password=generate_password_hash("admin123", method="pbkdf2:sha256"), type="Admin_RRHH")
    usuario_supervisor = Usuario(username="Diego", password=generate_password_hash("supervisor123", method="pbkdf2:sha256"), type="Supervisor")
    usuario_analista = Usuario(username="Guada", password=generate_password_hash("analista123", method="pbkdf2:sha256"), type="Analista_Datos")
    
    db.session.add(usuario_admin)
    db.session.add(usuario_supervisor)
    db.session.add(usuario_analista)
    db.session.commit()
    print("Usuarios ficticios creados con éxito.")
"""
# Cargar el modelo correctamente
modelo_path = get_path("modelo_candidatos.pkl")

try:
    encoder_educacion_path = get_path("encoder_educacion.pkl")
    encoder_habilidades_path = get_path("encoder_habilidades.pkl")
    encoder_tecnologias_path = get_path("encoder_tecnologias.pkl")
    
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
    return [c.mail for c in Candidato.query.filter_by(idOfer=idOfer, aptitud=True).all()]

def obtener_correos_noaptos(idOfer):
    return [c.mail for c in Candidato.query.filter_by(idOfer=idOfer, aptitud=False).all()]




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


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario.query.filter_by(username=username).first()
        
        if user:
            if (check_password_hash(user.password, password)):
                session['username'] = user.username
                session['type'] = user.type
                # Redirige según el rol usando url_for
                if user.type == "Admin_RRHH":
                    return redirect(url_for('admin_rrhh'))
                elif user.type == "Supervisor":
                    return redirect(url_for('supervisor'))
                elif user.type == "Analista_Datos":
                    return redirect(url_for('analista'))
                else:
                    return "Rol no reconocido"
            else:
                flash("Contraseña incorrecta")
                return render_template("auth/login.html")
        else:
            flash("Usuario no existente")
            return render_template("auth/login.html")
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



@app.route('/enviar_correos')
def enviar_correos():
    #mails a candidatos aptos
    destinatariosAptos = obtener_correos_aptos()
    with email.connect() as conn:
        for mail in destinatariosAptos:
            mensaje = Message(subject='Oportunidad laboral',
                              sender=app.config['MAIL_USERNAME'],
                              recipients=[mail],
                              body='Hola, hemos revisado tu curriculum y estamos interesados en tu perfil.')
            conn.send(mensaje)
    #mails a candidatos no aptos
    destinatariosNoAptos = obtener_correos_noaptos()
    with email.connect() as conn:
        for mail in destinatariosNoAptos:
            mensaje = Message(subject='Oportunidad laboral',
                                sender=app.config['MAIL_USERNAME'],
                                recipients=[mail],
                                body='Hola, lamentamos que en esta oportunidad tu perfil no se ajusta a lo que buscamos.')
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

    session["opciones_ofertas"] = opciones_ofertas
    session["opciones_educacion"] = opciones_educacion
    session["opciones_tecnologias"] = opciones_tecnologias
    session["opciones_habilidades"] = opciones_habilidades

    return render_template(
        "postulacion.html",
        opciones_ofertas=session["opciones_ofertas"],
        opciones_educacion=session["opciones_educacion"],
        opciones_tecnologias=session["opciones_tecnologias"],
        opciones_habilidades=session["opciones_habilidades"]
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

        try:
            # Buscar el ID correspondiente en las tablas
            educacion_obj = Educacion.query.filter_by(nombre=educacion).first()
            tecnologia_obj = Tecnologia.query.filter_by(nombre=tecnologias).first()
            habilidad_obj = Habilidad.query.filter_by(nombre=habilidades).first()

            if not educacion_obj or not tecnologia_obj or not habilidad_obj:
                flash("Error: Valores inválidos seleccionados.")
                return redirect("/postulacion")

            idedu = educacion_obj.idedu
            idtec = tecnologia_obj.idtec
            idhab = habilidad_obj.idhab

            # Crear y guardar el candidato
            nuevo_candidato_db = Candidato(
                id=email + idOfer,
                nombre=nombre,
                apellido=apellido,
                mail=email,
                telefono=telefono,
                ubicacion=ubicacion,
                experiencia=experiencia,
                idedu=idedu,
                idtec=idtec,
                idhab=idhab,
                idOfer=idOfer,
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
        opciones_habilidades=session["opciones_habilidades"]
    )

@app.route('/crear_oferta', methods=['GET', 'POST'])
@login_required(roles=["Admin_RRHH"])
def crear_oferta():
    if request.method == "POST":
        try:
            nombre = request.form.get("nombre")
            fecha_cierre_str = request.form.get("fecha_cierre")
            max_candidatos = int(request.form.get("max_candidatos"))
            remuneracion = "$" + request.form.get("remuneracion")  # 💰 Agregar "$"
            beneficio = request.form.get("beneficio")  # 🎁 Recibir beneficio
            usuario_responsable = session.get("username")  # 👤 Obtener usuario logueado
            fecha_cierre = datetime.strptime(fecha_cierre_str, "%Y-%m-%d")

            # 🔹 Verificar si el nombre ya existe
            if OfertaLaboral.query.filter_by(nombre=nombre).first():
                flash(f"Error: La oferta '{nombre}' ya existe. Elige un nombre diferente.")
                return redirect("/crear_oferta")

            nueva_oferta = OfertaLaboral(
                nombre=nombre,
                fecha_cierre=fecha_cierre,
                max_candidatos=max_candidatos,
                remuneracion=remuneracion,
                beneficio=beneficio,
                estado="Activa",  # 🔄 Siempre comienza como "Activa"
                usuario_responsable=usuario_responsable
            )
            db.session.add(nueva_oferta)
            db.session.flush()  # 🔹 Garantizar que obtenemos el ID antes de insertar etiquetas

            # 🔹 Cargar encoders
            encoder_educacion = joblib.load(get_path("encoder_educacion.pkl"))
            encoder_tecnologias = joblib.load(get_path("encoder_tecnologias.pkl"))
            encoder_habilidades = joblib.load(get_path("encoder_habilidades.pkl"))

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

            db.session.commit()  # 🔹 Guardar todas las asociaciones
            flash(f"Oferta '{nombre}' creada con éxito 🎉 con estado '{nueva_oferta.estado}' y etiquetas asignadas", "success")
            return redirect("/crear_oferta")

        except Exception as e:
            db.session.rollback()  # 🔄 Revierte cambios si hay error
            flash(f"Error al crear la oferta: {str(e)}")
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
        "Fecha de Cierre": o.fecha_cierre.strftime("%Y-%m-%d"),
        "Máx. Candidatos": o.max_candidatos,
        "Remuneración": o.remuneracion,
        "Beneficio": o.beneficio,
        "Estado": o.estado,
        "Responsable": o.usuario_responsable,
        "Acción": f'<form style="display: inline-block; width: 110px; height: 35px; margin: 0 auto;" method="POST" action="{url_for("cerrar_oferta", idOfer=o.idOfer)}">'
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
    oferta.fecha_cierre = datetime.now()  # 🔹 Fecha de cierre en el momento actual
    oferta.estado = "Cerrada"
    
    predecir_postulantes_automatica(oferta.idOfer)
    asignar_puntajes_automatica(oferta.idOfer)
    enviar_correos_automatica(oferta.idOfer)
    
    db.session.commit()

    return redirect(url_for("ver_ofertas"))


# Página de estadísticas
@app.route("/estadisticas", methods=["GET", "POST"])
@login_required(roles=["Admin_RRHH"])
def estadisticas():
    if request.method == "POST":
        return render_template("predecir.html")
    # Cargar modelo y encoders
    modelo = joblib.load(get_path("modelo_candidatos.pkl"))
    encoder_educacion = joblib.load(get_path("encoder_educacion.pkl"))
    encoder_habilidades = joblib.load(get_path("encoder_habilidades.pkl"))
    encoder_tecnologias = joblib.load(get_path("encoder_tecnologias.pkl"))

    # Leer el dataset de entrenamiento
    dataSet = pd.read_csv(get_path("entrenamientoActualizado.csv"))

    dataSet["Educacion"] = encoder_educacion.fit_transform(dataSet["Educacion"])
    dataSet["Habilidades"] = encoder_habilidades.fit_transform(dataSet["Habilidades"])
    dataSet["Tecnologías"] = encoder_tecnologias.fit_transform(dataSet["Tecnologías"])

    # Ya está codificado, así que sólo aseguramos que Apto esté como entero
    if dataSet["Apto"].dtype == object:
        dataSet["Apto"] = dataSet["Apto"].map({"Apto": 1, "No Apto": 0})

    X = dataSet[["Experiencia", "Educacion", "Tecnologías", "Habilidades"]]
    y = dataSet["Apto"]
    precision = round(modelo.score(X, y), 4)

    # Clases de encoders
    clases = {
        "Educacion": list(encoder_educacion.classes_),
        "Habilidades": list(encoder_habilidades.classes_),
        "Tecnologías": list(encoder_tecnologias.classes_),
    }

    # Graficar árbol y convertir a imagen en base64
    fig, ax = plt.subplots(figsize=(14, 8))
    plot_tree(modelo, feature_names=["Experiencia", "Educacion", "Tecnologías", "Habilidades"], 
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
    precision=precision,
    imagen_arbol=imagen_base64
)


# Ruta para predecir con un archivo CSV
@app.route("/predecir", methods=["GET", "POST"])
@login_required(roles=["Admin_RRHH"])
def predecir():
    if request.method == "POST":

        # Verifica que el archivo esté en la solicitud
        if "archivo_csv" not in request.files:
            return "Por favor, sube un archivo CSV."

        file = request.files["archivo_csv"]
        if file.filename == "":
            return "No seleccionaste ningún archivo."

        try:
            # Leer el archivo CSV
            dataSet = pd.read_csv(file)
            encoder_educacion_path = get_path("encoder_educacion.pkl")
            encoder_habilidades_path = get_path("encoder_habilidades.pkl")
            encoder_tecnologias_path = get_path("encoder_tecnologias.pkl")
        
            encoder_educacion = joblib.load(encoder_educacion_path)
            session["opciones_educacion"] = list(encoder_educacion.classes_)
            encoder_habilidades = joblib.load(encoder_habilidades_path)
            session["opciones_habilidades"] = list(encoder_habilidades.classes_)
            encoder_tecnologias = joblib.load(encoder_tecnologias_path)
            session["opciones_tecnologias"] = list(encoder_tecnologias.classes_)
            modelo = joblib.load(modelo_path)

            # Verifica que las columnas necesarias existan en el archivo
            columnas_requeridas = ["Experiencia", "Educacion", "Tecnologías", "Habilidades"]
            for columna in columnas_requeridas:
                if columna not in dataSet.columns:
                    return f"El archivo no contiene la columna requerida: {columna}"

            dataSet2 = dataSet.copy()

            # Transformar las columnas categóricas utilizando los encoders cargados
            try:
                dataSet["Educacion"] = encoder_educacion.transform(dataSet["Educacion"])
                dataSet["Habilidades"] = encoder_habilidades.transform(dataSet["Habilidades"])
                dataSet["Tecnologías"] = encoder_tecnologias.transform(dataSet["Tecnologías"])
            except ValueError as e:
                return f"Error en las transformaciones: {e}. Asegúrate de que todas las categorías estén reconocidas por los encoders."

            # Verificar si hay valores no válidos después de las transformaciones
            if dataSet[["Educacion", "Habilidades", "Tecnologías"]].isnull().values.any():
                return "El archivo contiene categorías que no se pudieron transformar correctamente."

            # Realizar las predicciones con el modelo
            X = dataSet[["Experiencia", "Educacion", "Tecnologías", "Habilidades"]]
            predicciones = modelo.predict(X)

            # Añadir predicciones al DataFrame
            dataSet2["Apto"] = ["Apto" if pred == 1 else "No Apto" for pred in predicciones]

            # Reordenar las columnas para asegurar que "Apto" esté al final
            columnasOrdenadas = [col for col in dataSet2.columns if col != "Apto"] + ["Apto"]
            dataSet2 = dataSet2[columnasOrdenadas]

            # Convertir DataFrame a HTML
            tabla_html = dataSet2.to_html(classes="table table-striped", index=False)

            # Renderizar resultado con HTML
            return render_template("resultado.html", tabla=tabla_html)

        except Exception as e:
            return f"Ocurrió un error al procesar el archivo: {e}"
    
    return render_template("predecir.html")


@app.route("/postulantes")
@login_required(roles=["Admin_RRHH"])
def postulantes(idOfer=None):
    filtro = request.args.get("filtro")
    
    ofertas = OfertaLaboral.query.all()
    if not idOfer:
        idOfer = request.form.get("idOfer") if request.method == "POST" else request.args.get("idOfer")
        if not idOfer and ofertas:
            idOfer = ofertas[0].idOfer  # Primera oferta como default

    # 🔹 Detectar ofertas cerradas automáticamente
    ofertas_cerradas = OfertaLaboral.query.filter(OfertaLaboral.fecha_cierre <= datetime.now(), OfertaLaboral.estado == "Activa").all()
    
    for oferta in ofertas_cerradas:
        oferta.estado = "Cerrada"
        db.session.add(oferta)

        # 🔹 Ejecutar predicción y asignación de puntajes
        predecir_postulantes_automatica(oferta.idOfer)
        asignar_puntajes_automatica(oferta.idOfer)

        # 🔹 Enviar correos automáticamente
        enviar_correos_automatica(oferta.idOfer)

    db.session.commit()  # Guardar cambios en la base de datos

    # 🔹 Cargar candidatos como ya lo hacías
    if idOfer:
        candidatos = Candidato.query.filter_by(idOfer=idOfer).order_by(Candidato.puntaje.desc()).all()
    else:
        candidatos = Candidato.query.order_by(Candidato.puntaje.desc()).all()

    if not candidatos:
        return render_template("postulantes.html", mensaje="No hay candidatos disponibles.", ofertas=OfertaLaboral.query.all(), idOfer=idOfer)

    # 🏆 Generar tabla de ranking de aptos con tu lógica actual
    dataSet = pd.DataFrame([{
        "Nombre": c.nombre,
        "Apellido": c.apellido,
        "Email": c.mail,
        "Telefono": c.telefono,
        "Ubicacion": c.ubicacion,
        "Experiencia": c.experiencia,
        "Educacion": c.idedu,
        "Tecnologías": c.idtec,
        "Habilidades": c.idhab,
        "Oferta Laboral": c.oferta.nombre,
        "Apto": "Apto" if c.aptitud is True else ("No apto" if c.aptitud is False else "Sin revisar"),
        "Puntaje": c.puntaje
    } for c in candidatos])

    # Mapear nombres de educación, tecnología y habilidades como ya lo hacías
    educacion_map = {edu.idedu: edu.nombre for edu in Educacion.query.all()}
    tecnologia_map = {tec.idtec: tec.nombre for tec in Tecnologia.query.all()}
    habilidad_map = {hab.idhab: hab.nombre for hab in Habilidad.query.all()}

    dataSet["Educacion"] = dataSet["Educacion"].map(educacion_map)
    dataSet["Tecnologías"] = dataSet["Tecnologías"].map(tecnologia_map)
    dataSet["Habilidades"] = dataSet["Habilidades"].map(habilidad_map)

    # Aplicar filtro por aptitud si está activado
    if filtro == "apto":
        dataSet = dataSet[dataSet["Apto"] == "Apto"]

    tabla_html = dataSet.to_html(classes="table table-striped", index=False)
    return render_template("postulantes.html", tabla=tabla_html, ofertas=OfertaLaboral.query.all(), idOfer=idOfer)

def predecir_postulantes_automatica(idOfer):
    candidatos = Candidato.query.filter_by(idOfer=idOfer).all()

    if not candidatos:
        return

    modelo = joblib.load(get_path("modelo_candidatos.pkl"))

    X = pd.DataFrame([{
        "Experiencia": c.experiencia,
        "Educacion": c.idedu,
        "Tecnologías": c.idtec,
        "Habilidades": c.idhab
    } for c in candidatos])

    predicciones = modelo.predict(X)

    for i, candidato in enumerate(candidatos):
        candidato.aptitud = bool(predicciones[i])  # 🔹 Convertir predicción a `True` o `False`
        db.session.add(candidato)

    db.session.commit()


def asignar_puntajes_automatica(idOfer):
    candidatos = Candidato.query.filter_by(idOfer=idOfer, aptitud=True).all()

    if not candidatos:
        return

    for c in candidatos:
        c.puntaje = calcular_puntaje(c)
        db.session.add(c)

    db.session.commit()


def enviar_correos_automatica(idOfer):
    destinatariosAptos = obtener_correos_aptos(idOfer)
    destinatariosNoAptos = obtener_correos_noaptos(idOfer)

    with email.connect() as conn:
        for mail in destinatariosAptos:
            mensaje = Message(
                subject="Oportunidad laboral",
                sender=app.config["MAIL_USERNAME"],
                recipients=[mail],
                body="Hola, hemos revisado tu perfil y estamos interesados en tu candidatura."
            )
            conn.send(mensaje)

        for mail in destinatariosNoAptos:
            mensaje = Message(
                subject="Oportunidad laboral",
                sender=app.config["MAIL_USERNAME"],
                recipients=[mail],
                body="Hola, lamentamos informarte que en esta oportunidad tu perfil no se ajusta a lo que buscamos."
            )
            conn.send(mensaje)


@app.route("/limpiar_postulantes", methods=["POST"])
@login_required(roles=["Admin_RRHH"])
def limpiar_postulantes():
    try:
        # Eliminar todos los registros de la tabla "Candidato"
        db.session.query(Candidato).delete()
        db.session.commit()  # Confirmar los cambios en la base de datos

        # También puedes actualizar o limpiar el archivo CSV
        entrenamientoActualizado_path = get_path("candidatosLocales.csv")
        columnas = ["Nombre", "Apellido", "Educacion", "Experiencia", "Habilidades", "Tecnologías", "Apto"]
        pd.DataFrame(columns=columnas).to_csv(entrenamientoActualizado_path, index=False)

        return redirect(url_for("postulantes"))
    except Exception as e:
        return f"Ocurrió un error al limpiar los postulantes: {e}"


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
            "Apto": c.aptitud if c.aptitud else "sin revisar",
            "Puntaje": c.puntaje
        } for c in candidatos])

        # Cargar el modelo entrenado
        modelo = joblib.load(get_path("modelo_candidatos.pkl"))

        # Verificar que las columnas necesarias estén presentes
        columnas_requeridas = ["Experiencia", "Educacion", "Tecnologías", "Habilidades"]
        for columna in columnas_requeridas:
            if columna not in dataSet.columns:
                return f"Falta la columna requerida: {columna}"

        # Realizar predicciones
        X = dataSet[["Experiencia", "Educacion", "Tecnologías", "Habilidades"]]
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

        dataSet["Educacion"] = dataSet["Educacion"].map(educacion_map)
        dataSet["Tecnologías"] = dataSet["Tecnologías"].map(Tecnologia_map)
        dataSet["Habilidades"] = dataSet["Habilidades"].map(habilidad_map)

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

    if candidato.idOfer:  # Asegurarse de que el candidato esté vinculado a una oferta laboral
        # Obtener la importancia desde OfertaEducacion
        edu_rel = OfertaEducacion.query.filter_by(idOfer=candidato.idOfer, idEdu=candidato.idedu).first()
        if edu_rel:
            puntaje += edu_rel.importancia * 3

        # Obtener la importancia desde OfertaTecnologia
        tec_rel = OfertaTecnologia.query.filter_by(idOfer=candidato.idOfer, idTec=candidato.idtec).first()
        if tec_rel:
            puntaje += tec_rel.importancia * 5

        # Obtener la importancia desde OfertaHabilidad
        hab_rel = OfertaHabilidad.query.filter_by(idOfer=candidato.idOfer, idHab=candidato.idhab).first()
        if hab_rel:
            puntaje += hab_rel.importancia * 2

    return puntaje


@app.route("/cargarCV", methods=["GET", "POST"])
@login_required(roles=["Admin_RRHH"])
def cargarCV():
    # Obtener todas las ofertas laborales disponibles
    opciones_ofertas = [{"idOfer": oferta.idOfer, "nombre": oferta.nombre} for oferta in OfertaLaboral.query.filter(OfertaLaboral.estado != "Cerrada").all()]
    opciones_educacion = [educacion.nombre for educacion in Educacion.query.all()]
    opciones_tecnologias = [tecnologia.nombre for tecnologia in Tecnologia.query.all()]
    opciones_habilidades = [habilidad.nombre for habilidad in Habilidad.query.all()]

    session["opciones_ofertas"] = opciones_ofertas
    session["opciones_educacion"] = opciones_educacion
    session["opciones_tecnologias"] = opciones_tecnologias
    session["opciones_habilidades"] = opciones_habilidades

    if request.method == "POST":
        # Obtener datos del formulario
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        email = request.form["email"]
        telefono = request.form["telefono"]
        ubicacion = request.form["ubicacion"]
        experiencia = int(request.form["experiencia"])
        educacion = request.form["educacion"]
        tecnologias = request.form["tecnologias"]
        habilidades = request.form["habilidades"]
        idOfer = request.form.get("idOfer")  # Nueva variable para oferta laboral

        if not idOfer:
            flash("Debes seleccionar una oferta laboral.")
            return redirect("/cargarCV")

        try:
            # Buscar el ID correspondiente en las tablas
            educacion_obj = Educacion.query.filter_by(nombre=educacion).first()
            tecnologia_obj = Tecnologia.query.filter_by(nombre=tecnologias).first()
            habilidad_obj = Habilidad.query.filter_by(nombre=habilidades).first()

            if not educacion_obj or not tecnologia_obj or not habilidad_obj:
                flash("Error: Valores inválidos seleccionados.")
                return redirect("/cargarCV")

            idedu = educacion_obj.idedu
            idtec = tecnologia_obj.idtec
            idhab = habilidad_obj.idhab

            # Crear y guardar el candidato con la oferta laboral seleccionada
            nuevo_candidato_db = Candidato(
                id=email + idOfer,
                nombre=nombre,
                apellido=apellido,
                mail=email,
                telefono=telefono,
                ubicacion=ubicacion,
                experiencia=experiencia,
                idedu=idedu,
                idtec=idtec,
                idhab=idhab,
                idOfer=idOfer,  # Asociación con la oferta laboral
                aptitud=None
            )
            db.session.add(nuevo_candidato_db)
            db.session.commit()
            flash(f"Candidato {nombre} guardado correctamente y asociado a la oferta laboral '{OfertaLaboral.query.get(idOfer).nombre}'.")
        except Exception as e:
            flash(f"Este mail ya había sido registrado en esta postulación")
            return redirect("/cargarCV")

    return render_template(
        "cargarCV.html",
        opciones_ofertas=session["opciones_ofertas"],  # Pasamos ofertas al HTML
        opciones_educacion=session["opciones_educacion"],
        opciones_tecnologias=session["opciones_tecnologias"],
        opciones_habilidades=session["opciones_habilidades"]
    )


@app.route("/etiquetas", methods=["GET", "POST"])
@login_required(roles=["Admin_RRHH"])
def mostrar_etiquetas(idOfer=None):

    ofertas_activas = [{"idOfer": oferta.idOfer, "nombre": oferta.nombre} for oferta in OfertaLaboral.query.filter(OfertaLaboral.estado != "Cerrada").all()]
    ofertas = OfertaLaboral.query.all()
    if not idOfer:
        idOfer = request.form.get("idOfer") if request.method == "POST" else request.args.get("idOfer")
        if not idOfer and ofertas:
            idOfer = ofertas[0].idOfer  # Primera oferta como default

    educaciones, tecnologias, habilidades = [], [], []

    if idOfer:
        oferta = OfertaLaboral.query.get(idOfer)
        educaciones = OfertaEducacion.query.filter_by(idOfer=idOfer).all()
        tecnologias = OfertaTecnologia.query.filter_by(idOfer=idOfer).all()
        habilidades = OfertaHabilidad.query.filter_by(idOfer=idOfer).all()

        # Generar DataFrames con datos recién recuperados
        df_edu = pd.DataFrame([{"Nombre": e.educacion.nombre, "Valor": e.importancia} for e in educaciones]) if educaciones else pd.DataFrame()
        df_tec = pd.DataFrame([{"Nombre": t.tecnologia.nombre, "Valor": t.importancia} for t in tecnologias]) if tecnologias else pd.DataFrame()
        df_hab = pd.DataFrame([{"Nombre": h.habilidad.nombre, "Valor": h.importancia} for h in habilidades]) if habilidades else pd.DataFrame()

        # Convertir DataFrames a tablas HTML
        tabla_edu = df_edu.to_html(classes="table table-bordered", index=False) if not df_edu.empty else "<p>No hay etiquetas de educación</p>"
        tabla_tec = df_tec.to_html(classes="table table-bordered", index=False) if not df_tec.empty else "<p>No hay etiquetas de tecnología</p>"
        tabla_hab = df_hab.to_html(classes="table table-bordered", index=False) if not df_hab.empty else "<p>No hay etiquetas de habilidades</p>"
    else:
        oferta, tabla_edu, tabla_tec, tabla_hab = None, "", "", ""

    return render_template("etiquetas.html",
                           ofertas=ofertas,
                           ofertas_activas=ofertas_activas,
                           oferta=oferta,
                           idOfer=idOfer,  # 🔹 Pasar la oferta seleccionada al HTML
                           tabla_edu=tabla_edu,
                           tabla_tec=tabla_tec,
                           tabla_hab=tabla_hab,
                           educaciones=educaciones,
                           tecnologias=tecnologias,
                           habilidades=habilidades)


@app.route("/asignar_valores/<int:idOfer>", methods=["POST"])
@login_required(roles=["Admin_RRHH"])
def asignar_valores(idOfer):
    oferta = OfertaLaboral.query.get(idOfer)
    if not oferta:
        flash("Oferta no encontrada", "error")
        return redirect(url_for("dashboard"))

    # Educación
    educacion_id = request.form.get("educacion_id")
    valor_educacion = request.form.get("valor_educacion")
    if valor_educacion:
        edu_rel = OfertaEducacion.query.filter_by(idOfer=idOfer, idEdu=educacion_id).first()
        if edu_rel:
            edu_rel.importancia = int(valor_educacion)

    # Tecnología
    tecnologia_id = request.form.get("tecnologia_id")
    valor_tecnologia = request.form.get("valor_tecnologia")
    if valor_tecnologia:
        tec_rel = OfertaTecnologia.query.filter_by(idOfer=idOfer, idTec=tecnologia_id).first()
        if tec_rel:
            tec_rel.importancia = int(valor_tecnologia)

    # Habilidad
    habilidad_id = request.form.get("habilidad_id")
    valor_habilidad = request.form.get("valor_habilidad")
    if valor_habilidad:
        hab_rel = OfertaHabilidad.query.filter_by(idOfer=idOfer, idHab=habilidad_id).first()
        if hab_rel:
            hab_rel.importancia = int(valor_habilidad)

    db.session.commit()
    flash("Importancia actualizada correctamente", "success")

    return mostrar_etiquetas(idOfer)  # 🔹 Recuperamos datos actualizados antes de renderizar


@app.route("/metricas")
@login_required(roles=["Admin_RRHH"])
def metricas():
    ofertas = OfertaLaboral.query.all()
    return render_template("metricas.html", ofertas=ofertas)


@app.route("/metricas/<int:oferta_id>")
@login_required(roles=["Admin_RRHH"])
def obtener_metricas(oferta_id):
    oferta = OfertaLaboral.query.get_or_404(oferta_id)

    etiquetas = []
    cantidades = []
    promedios_experiencia = {}
    # Datos de ubicación
    provincias_candidatos = {}

    candidatos = Candidato.query.filter_by(idOfer=oferta_id).all()
    for c in candidatos:
        provincia = c.ubicacion  # Suponiendo que `ubicacion` es el nombre de la provincia
        provincias_candidatos[provincia] = provincias_candidatos.get(provincia, 0) + 1

    # Educación
    for edu_rel in oferta.educaciones:
        etiqueta = edu_rel.educacion.nombre
        candidatos = Candidato.query.filter_by(idOfer=oferta_id, idedu=edu_rel.idEdu).all()
        promedio_exp = sum(c.experiencia for c in candidatos) / len(candidatos) if candidatos else 0
        etiquetas.append(f"Edu: {etiqueta}")
        cantidades.append(len(candidatos))
        promedios_experiencia[etiqueta] = promedio_exp

    # Tecnología
    for tec_rel in oferta.tecnologias:
        etiqueta = tec_rel.tecnologia.nombre
        candidatos = Candidato.query.filter_by(idOfer=oferta_id, idtec=tec_rel.idTec).all()
        promedio_exp = sum(c.experiencia for c in candidatos) / len(candidatos) if candidatos else 0
        etiquetas.append(f"Tec: {etiqueta}")
        cantidades.append(len(candidatos))
        promedios_experiencia[etiqueta] = promedio_exp

    # Habilidad
    for hab_rel in oferta.habilidades:
        etiqueta = hab_rel.habilidad.nombre
        candidatos = Candidato.query.filter_by(idOfer=oferta_id, idhab=hab_rel.idHab).all()
        promedio_exp = sum(c.experiencia for c in candidatos) / len(candidatos) if candidatos else 0
        etiquetas.append(f"Hab: {etiqueta}")
        cantidades.append(len(candidatos))
        promedios_experiencia[etiqueta] = promedio_exp

    # Datos de candidatos
    total_candidatos = Candidato.query.filter_by(idOfer=oferta_id).count()
    aptos = Candidato.query.filter_by(idOfer=oferta_id, aptitud=True).count()
    no_aptos = Candidato.query.filter_by(idOfer=oferta_id, aptitud=False).count()
    sin_revisar = Candidato.query.filter_by(idOfer=oferta_id, aptitud=None).count()

    return jsonify({
        "etiquetas": etiquetas,
        "cantidades": cantidades,
        "promedios_experiencia": promedios_experiencia,
        "total_candidatos": total_candidatos,
        "aptos": aptos,
        "no_aptos": no_aptos,
        "sin_revisar": sin_revisar,
        "provincias_candidatos": provincias_candidatos
    })


if __name__ == "__main__":
    threading.Timer(1.5, abrir_navegador).start() 
    app.run(debug=False, host="127.0.0.1", port=5000)
