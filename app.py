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
from flask import Flask
from flask_mail import Mail, Message
from functools import wraps

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



class Candidato(db.Model):
    id = db.Column(db.String, primary_key=True)  # Usamos el correo como ID único
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    mail = db.Column(db.String(100), nullable=False, unique=True)
    telefono = db.Column(db.String(50), nullable=False)
    ubicacion = db.Column(db.String(100), nullable=False)
    experiencia = db.Column(db.Integer, nullable=False)
    idedu = db.Column(db.Integer, db.ForeignKey('educacion.idedu'))
    idtec = db.Column(db.Integer, db.ForeignKey('tecnologia.idtec'))
    idhab = db.Column(db.Integer, db.ForeignKey('habilidad.idhab'))
    aptitud = db.Column(db.Boolean, nullable=True)
    puntaje = db.Column(db.Integer, nullable=False, default=0)

class Educacion(db.Model):
    __tablename__ = 'educacion'
    idedu = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    importancia = db.Column(db.Integer, nullable=False)

class Tecnologia(db.Model):
    __tablename__ = 'tecnologia'
    idtec = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    importancia = db.Column(db.Integer, nullable=False)

class Habilidad(db.Model):
    __tablename__ = 'habilidad'
    idhab = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    importancia = db.Column(db.Integer, nullable=False)
    
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
if not os.path.exists("erp_rrhh.db"):
    with app.app_context():
        db.create_all()
        # Agregar usuarios ficticios
        # Cargar los encoders
        encoder_educacion = joblib.load(get_path("encoder_educacion.pkl"))
        encoder_tecnologias = joblib.load(get_path("encoder_tecnologias.pkl"))
        encoder_habilidades = joblib.load(get_path("encoder_habilidades.pkl"))

        # Insertar las clases en la tabla de 'Educacion'
        for idx, clase in enumerate(encoder_educacion.classes_):
            nueva_educacion = Educacion(
                idedu=idx,  # El índice asignado por el encoder será el ID
                nombre=clase,
                importancia=0  # Ajustar según tu lógica
            )
            db.session.merge(nueva_educacion)  # Merge para evitar duplicados

        # Insertar las clases en la tabla de 'Tecnologia'
        for idx, clase in enumerate(encoder_tecnologias.classes_):
            nueva_tecnologia = Tecnologia(
                idtec=idx,
                nombre=clase,
                importancia=0  # Ajustar según tu lógica
            )
            db.session.merge(nueva_tecnologia)

        # Insertar las clases en la tabla de 'Habilidad'
        for idx, clase in enumerate(encoder_habilidades.classes_):
            nueva_habilidad = Habilidad(
                idhab=idx,
                nombre=clase,
                importancia=0  # Ajustar según tu lógica
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

def obtener_correos_aptos():
    candidatos_aptos = Candidato.query.filter_by(aptitud=True).all()
    return [c.mail for c in candidatos_aptos if c.mail]

def obtener_correos_noaptos():
    candidatos_no_aptos = Candidato.query.filter_by(aptitud=False).all()
    return [c.mail for c in candidatos_no_aptos if c.mail]

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


def abrir_navegador():
    webbrowser.open("http://127.0.0.1:5000/")  # URL de Flask

# 🔹 Obtener la ruta correcta dentro del ejecutable

# 🔹 Cargar el modelo correctamente
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


# Página principal postulacion
@app.route("/postulacionIT")
def postulacionIT():
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


# Página principal
@app.route('/')
def index():
    return redirect('/login')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario.query.filter_by(username=username).first()
        
        print("Ruta absoluta de la base de datos:", os.path.abspath("erp_rrhh.db"))
        
        if user and check_password_hash(user.password, password):
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


"""
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/", methods=["GET", "POST"])
def entrenar_inicio():
    if request.method == "POST":
        if "archivo_entrenamiento" not in request.files:
            return "Por favor, sube un archivo CSV."

        archivo = request.files["archivo_entrenamiento"]
        if archivo.filename == "":
            return "No seleccionaste ningún archivo."

        try:
            dataSet = pd.read_csv(archivo)
            dataSet2 = dataSet.copy()

            # Inicializar encoders
            encoder_educacion = LabelEncoder()
            encoder_habilidades = LabelEncoder()
            encoder_tecnologias = LabelEncoder()

            # Entrenamiento
            dataSet["Educacion"] = encoder_educacion.fit_transform(dataSet["Educacion"])
            dataSet["Habilidades"] = encoder_habilidades.fit_transform(dataSet["Habilidades"])
            dataSet["Tecnologías"] = encoder_tecnologias.fit_transform(dataSet["Tecnologías"])
            dataSet["Apto"] = dataSet["Apto"].map({"Apto": 1, "No Apto": 0})

            X = dataSet[["Experiencia", "Educacion", "Tecnologías", "Habilidades"]]
            y = dataSet["Apto"]

            modelo = DecisionTreeClassifier(max_depth=5)
            modelo.fit(X, y)

            # Guardar modelo y encoders
            joblib.dump(modelo, get_path("modelo_candidatos.pkl"))
            joblib.dump(encoder_educacion, get_path("encoder_educacion.pkl"))
            joblib.dump(encoder_habilidades, get_path("encoder_habilidades.pkl"))
            joblib.dump(encoder_tecnologias, get_path("encoder_tecnologias.pkl"))

            # Guardar dataset
            dataSet2.to_csv(get_path("entrenamientoActualizado.csv"), index=False)

            # Guardar en sesión para estadísticas
            session["clases_educacion"] = list(encoder_educacion.classes_)
            session["clases_habilidades"] = list(encoder_habilidades.classes_)
            session["clases_tecnologias"] = list(encoder_tecnologias.classes_)

            session["modelo_entrenado"] = True

            # Redirigir a la página de estadísticas
            return redirect("/estadisticas")

        except Exception as e:
            return f"❌ Ocurrió un error durante el entrenamiento: {e}"

    return render_template("index.html")
"""


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
def postulantes():
    candidatos = Candidato.query.order_by(Candidato.puntaje.desc()).all()
    #candidatos = Candidato.query.all()
        
    # Verificar si hay candidatos
    if not candidatos:  # Si la lista está vacía
        return render_template("postulantes.html", mensaje="No hay candidatos disponibles.")

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
        "Apto": "Apto" if c.aptitud is True else ("No apto" if c.aptitud is False else "Sin revisar"),
        "Puntaje": c.puntaje
    } for c in candidatos])
    
    educacion_map = {edu.idedu: edu.nombre for edu in Educacion.query.all()}
    Tecnologia_map = {tec.idtec: tec.nombre for tec in Tecnologia.query.all()}
    habilidad_map = {hab.idhab: hab.nombre for hab in Habilidad.query.all()}

    # Reemplazar los valores de 'Educacion' en el DataFrame con sus nombres
    dataSet["Educacion"] = dataSet["Educacion"].map(educacion_map)
    dataSet["Tecnologías"] = dataSet["Tecnologías"].map(Tecnologia_map)
    dataSet["Habilidades"] = dataSet["Habilidades"].map(habilidad_map)

    # Filtro por parámetro
    filtro = request.args.get("filtro")
    if filtro == "apto":
        dataSet = dataSet[dataSet["Apto"] == "Apto"]

    tabla_html = dataSet.to_html(classes="table table-striped", index=False)
    return render_template("postulantes.html", tabla=tabla_html)


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

    if candidato.idedu:
        edu = Educacion.query.get(candidato.idedu)
        if edu:
            puntaje += edu.importancia * 3

    if candidato.idtec:
        tec = Tecnologia.query.get(candidato.idtec)
        if tec:
            puntaje += tec.importancia * 5

    if candidato.idhab:
        hab = Habilidad.query.get(candidato.idhab)
        if hab:
            puntaje += hab.importancia * 2

    return puntaje

#EL SERVICIO POST DEL CREAR YA NO SE USA
@app.route("/crear", methods=["GET", "POST"])
@login_required(roles=["Admin_RRHH"])
def crear_csv():
    # Inicializar valores dinámicos para los inputs select
    encoder_educacion_path = get_path("encoder_educacion.pkl")
    encoder_habilidades_path = get_path("encoder_habilidades.pkl")
    encoder_tecnologias_path = get_path("encoder_tecnologias.pkl")
    encoder_educacion = joblib.load(encoder_educacion_path)
    session["opciones_educacion"] = list(encoder_educacion.classes_)
    encoder_habilidades = joblib.load(encoder_habilidades_path)
    session["opciones_habilidades"] = list(encoder_habilidades.classes_)
    encoder_tecnologias = joblib.load(encoder_tecnologias_path)
    session["opciones_tecnologias"] = list(encoder_tecnologias.classes_)
    
    if "candidatos" not in session:
        session["candidatos"] = []

    #ESTE POST YA NO SE USA, LIMPIAR
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

        # Crear un nuevo candidato como un diccionario
        nuevo_candidato = {
            "Nombre": nombre,
            "Apellido": apellido,
            "Experiencia": experiencia,
            "Educacion": educacion,
            "Tecnologías": tecnologias,
            "Habilidades": habilidades,
            "Apto": ""  # La columna Apto se evaluará después
        }

        # Agregar el nuevo candidato a la lista de candidatos
        if nuevo_candidato not in session["candidatos"]:
            session["candidatos"].append(nuevo_candidato)
            session.modified = True  # Marcar la sesión como modificada
        else:
            session.modified = False
            return redirect("/crear")

    # Renderizar la página HTML con los candidatos actuales
    return render_template(
        "crear.html",
        candidatos=session["candidatos"],
        opciones_educacion=session["opciones_educacion"],
        opciones_habilidades=session["opciones_habilidades"],
        opciones_tecnologias=session["opciones_tecnologias"]
    )

#ESTO SE VA TAMBIEN, LIMPIAR
@app.route("/eliminar_candidato/<int:indice>", methods=["POST"])
@login_required(roles=["Admin_RRHH"])
def eliminar_candidato(indice):
    if "candidatos" in session:
        try:
            # Eliminar el candidato en el índice especificado
            session["candidatos"].pop(indice)
            session.modified = True  # Marcar la sesión como modificada
            return redirect("/crear#tabla-container")  # Redirigir nuevamente a la página de creación
        except IndexError:
            return "Índice fuera de rango.", 400
    return redirect("/crear#tabla-container")

#LIMPIAR
@app.route("/guardar_csv", methods=["POST"])
@login_required(roles=["Admin_RRHH"])
def guardar_csv():
    # Obtener los datos de la sesión
    candidatos = session.get("candidatos", [])

    if not candidatos:
        return redirect("/crear#tabla-container")

    # Crear un DataFrame con los datos de los candidatos
    dataSet = pd.DataFrame(candidatos)

    # Reordenar las columnas en el orden deseado
    columnasOrdenadas = ["Nombre", "Apellido", "Experiencia", "Educacion", "Tecnologías", "Habilidades", "Apto"]
    dataSet = dataSet[columnasOrdenadas]

    # Guardar el archivo CSV con el orden adecuado
    candidatosPagina_path = get_path("candidatosPagina.csv")
    dataSet.to_csv(candidatosPagina_path, index=False)

    # Limpiar la sesión después de guardar el archivo
    session.pop("candidatos", None)

    return send_file(candidatosPagina_path, as_attachment=True)


@app.route("/etiquetas")
@login_required(roles=["Admin_RRHH"])
def mostrar_etiquetas():
    educaciones = Educacion.query.all()
    tecnologias = Tecnologia.query.all()
    habilidades = Habilidad.query.all()

    df_edu = pd.DataFrame([{"Nombre": e.nombre, "Valor": e.importancia} for e in educaciones])
    df_tec = pd.DataFrame([{"Nombre": t.nombre, "Valor": t.importancia} for t in tecnologias])
    df_hab = pd.DataFrame([{"Nombre": h.nombre, "Valor": h.importancia} for h in habilidades])

    tabla_edu = df_edu.to_html(classes="table table-bordered", index=False)
    tabla_tec = df_tec.to_html(classes="table table-bordered", index=False)
    tabla_hab = df_hab.to_html(classes="table table-bordered", index=False)

    return render_template("etiquetas.html",
                           tabla_edu=tabla_edu,
                           tabla_tec=tabla_tec,
                           tabla_hab=tabla_hab,
                           educaciones=educaciones,
                           habilidades=habilidades,
                           tecnologias=tecnologias)


@app.route("/asignar_valores", methods=["POST"])
@login_required(roles=["Admin_RRHH"])
def asignar_valores():
    # Educación
    educacion_id = request.form.get("educacion_id")
    valor_educacion = request.form.get("valor_educacion")
    if valor_educacion != "":
        edu = Educacion.query.get(int(educacion_id))
        if edu:
            edu.importancia = int(valor_educacion)

    # Tecnología
    tecnologia_id = request.form.get("tecnologia_id")
    valor_tecnologia = request.form.get("valor_tecnologia")
    if valor_tecnologia != "":
        tec = Tecnologia.query.get(int(tecnologia_id))
        if tec:
            tec.importancia = int(valor_tecnologia)

    # Habilidad
    habilidad_id = request.form.get("habilidad_id")
    valor_habilidad = request.form.get("valor_habilidad")
    if valor_habilidad != "":
        hab = Habilidad.query.get(int(habilidad_id))
        if hab:
            hab.importancia = int(valor_habilidad)

    db.session.commit()
    return redirect(url_for("mostrar_etiquetas"))


@app.route("/postulacion", methods=["GET", "POST"])
def postulacion():
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

        return redirect("/postulacionIT")

    return render_template(
        "postulacion.html",
        opciones_educacion=session["opciones_educacion"],
        opciones_tecnologias=session["opciones_tecnologias"],
        opciones_habilidades=session["opciones_habilidades"]
    )


if __name__ == "__main__":
    threading.Timer(1.5, abrir_navegador).start() 
    app.run(debug=False, host="127.0.0.1", port=5000)
