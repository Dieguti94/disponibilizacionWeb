import pytest
from flask import Flask
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app import db, OfertaEducacion, OfertaHabilidad, OfertaTecnologia, Educacion, Habilidad, Tecnologia, Candidato, OfertaLaboral, calcular_puntaje, asignar_puntajes_automatica 

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    db.init_app(app)
    return app

@pytest.fixture
def setup_db(app):
    with app.app_context():
        db.create_all()

        edu = Educacion(nombre="Universitario")
        edu2 = Educacion(nombre="Secundario")
        tec = Tecnologia(nombre="Java")
        tec2 = Tecnologia(nombre="SQL")
        hab = Habilidad(nombre="Liderazgo")
        hab2 = Habilidad(nombre="Adaptabilidad")

        db.session.add_all([edu, edu2, tec, tec2, hab, hab2])
        db.session.commit()

        oferta = OfertaLaboral(
            nombre="Desarrollador Backend SR",
            fecha_cierre=datetime.now(),
            max_candidatos=10,
            remuneracion="100000",
            beneficio="Remoto",
            estado="Activa",
            usuario_responsable="Fernando"
        )
        db.session.add(oferta)
        db.session.commit()

        db.session.add_all([
            OfertaEducacion(idOfer=oferta.idOfer, idEdu=edu.idedu, importancia=3),
            OfertaEducacion(idOfer=oferta.idOfer, idEdu=edu2.idedu, importancia=1),
            OfertaTecnologia(idOfer=oferta.idOfer, idTec=tec.idtec, importancia=2),
            OfertaTecnologia(idOfer=oferta.idOfer, idTec=tec2.idtec, importancia=1),
            OfertaHabilidad(idOfer=oferta.idOfer, idHab=hab.idhab, importancia=2),
            OfertaHabilidad(idOfer=oferta.idOfer, idHab=hab2.idhab, importancia=3),
        ])
        db.session.commit()

        candidato = Candidato(
            id="JosePerez@gmail.com",
            nombre="Jose",
            apellido="Abalos",
            mail="JosePerez@gmail.com",
            telefono="1122334455",
            ubicacion="Buenos Aires",
            experiencia=5,
            idedu=edu.idedu,
            idtec=tec.idtec,
            idhab=hab.idhab,
            idOfer=oferta.idOfer,
            aptitud=True,
            puntaje=0
        )
        db.session.add(candidato)
        db.session.commit()

        app.test_ids = {
            "Universitario": edu.idedu,
            "Secundario": edu2.idedu,
            "Java": tec.idtec,
            "SQL": tec2.idtec,
            "Liderazgo": hab.idhab,
            "Adaptabilidad": hab2.idhab,
        }

        yield oferta.idOfer
        db.session.remove()
        db.drop_all()

#Test que comprueba la asignacion de puntaje a un candidato
def test_agregar_puntaje(app, setup_db):
    with app.app_context():
        asignar_puntajes_automatica(setup_db)
        postulante = Candidato.query.get("JosePerez@gmail.com")
        assert postulante.puntaje == 33 
        
#Test que comprueba que se calcule el puntaje a 2 candidatos correctamente
@pytest.mark.parametrize(
    "nombre, apellido, email, telefono, ubicacion, experiencia, educacion, tecnologias, habilidades",
    [
        ('Lucas', 'Abalos', 'correoDePueba123@gmail.com', '1135356456', 'Buenos Aires', 3, "Universitario", "Java", "Adaptabilidad"),
        ('Hernesto', 'Gonzalez', 'correoDePueba4123@gmail.com', '1343567856', 'Buenos Aires', 6, "Secundario", "SQL", "Liderazgo"),
    ]
)
def test_calcular_puntaje_params(app, setup_db, nombre, apellido, email, telefono, ubicacion, experiencia, educacion, tecnologias, habilidades):
    with app.app_context():
        postulante = Candidato(
            id=email,
            nombre=nombre,
            apellido=apellido,
            mail=email,
            telefono=telefono,
            ubicacion=ubicacion,
            experiencia=experiencia,
            idedu=app.test_ids[educacion],
            idtec=app.test_ids[tecnologias],
            idhab=app.test_ids[habilidades],
            idOfer=setup_db,
            aptitud=True,
            puntaje=0
        )
        db.session.add(postulante)
        db.session.commit()

        puntaje_esperado = (
            experiencia * 2 +
            OfertaEducacion.query.filter_by(idOfer=setup_db, idEdu=postulante.idedu).first().importancia * 3 +
            OfertaTecnologia.query.filter_by(idOfer=setup_db, idTec=postulante.idtec).first().importancia * 5 +
            OfertaHabilidad.query.filter_by(idOfer=setup_db, idHab=postulante.idhab).first().importancia * 2
        )

        assert calcular_puntaje(postulante) == puntaje_esperado

def test_ranking(app, setup_db):
    with app.app_context():
        ids = app.test_ids
        db.session.add_all([
            Candidato(id="lucas@mail.com", nombre="Lucas", apellido="Abalos", mail="lucas@mail.com", telefono="1111111111", ubicacion="Buenos Aires", experiencia=3, idedu=ids["Universitario"], idtec=ids["Java"], idhab=ids["Adaptabilidad"], idOfer=setup_db, aptitud=True, puntaje=0),
            Candidato(id="hernesto@mail.com", nombre="Hernesto", apellido="Gonzalez", mail="hernesto@mail.com", telefono="2222222222", ubicacion="Buenos Aires", experiencia=6, idedu=ids["Secundario"], idtec=ids["SQL"], idhab=ids["Liderazgo"], idOfer=setup_db, aptitud=True, puntaje=0)
        ])
        db.session.commit()

        for c in Candidato.query.all():
            c.puntaje = calcular_puntaje(c)
        db.session.commit()

        puntajes = [c.puntaje for c in Candidato.query.order_by(Candidato.puntaje.desc()).all()]
        assert puntajes == sorted(puntajes, reverse=True)

#Test que se encarga de verificar que el sistema maneje correctamente un empate de puntaje entre candidatos. 
def test_ranking_con_empate(app, setup_db):
    with app.app_context():
        ids = app.test_ids
        Candidato.query.delete()
        db.session.commit()

        db.session.add_all([
            Candidato(id="empate1@mail.com", nombre="Ana", apellido="Lopez", mail="empate1@mail.com", telefono="1111111111", ubicacion="Buenos Aires", experiencia=4, idedu=ids["Universitario"], idtec=ids["SQL"], idhab=ids["Liderazgo"], idOfer=setup_db, aptitud=True, puntaje=0),
            Candidato(id="empate2@mail.com", nombre="Bruno", apellido="Martinez", mail="empate2@mail.com", telefono="2222222222", ubicacion="CABA", experiencia=4, idedu=ids["Universitario"], idtec=ids["SQL"], idhab=ids["Liderazgo"], idOfer=setup_db, aptitud=True, puntaje=0)
        ])
        db.session.commit()

        asignar_puntajes_automatica(setup_db)
        puntajes = [c.puntaje for c in Candidato.query.order_by(Candidato.puntaje.desc()).all()]
        assert puntajes == sorted(puntajes, reverse=True)
        assert puntajes.count(puntajes[0]) >= 2

#Test que verifica que no se le asigne el puntaje a un candidato no apto
def test_calcular_puntaje_a_no_apto(app, setup_db):
    with app.app_context():
        ids = app.test_ids
        Candidato.query.delete()
        db.session.commit()

        c = Candidato(
            id="anaLopez@gmail.com",
            nombre="Ana",
            apellido="Lopez",
            mail="anaLopez@gmail.com",
            telefono="1111111111",
            ubicacion="Buenos Aires",
            experiencia=4,
            idedu=ids["Universitario"],
            idtec=ids["SQL"],
            idhab=ids["Liderazgo"],
            idOfer=setup_db,
            aptitud=False,
            puntaje=0
        )
        db.session.add(c)
        db.session.commit()

        asignar_puntajes_automatica(setup_db)
        assert db.session.get(Candidato, c.id).puntaje == 0