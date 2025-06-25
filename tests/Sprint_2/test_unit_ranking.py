import pytest
from flask import Flask
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app import db, OfertaEducacion, OfertaHabilidad, OfertaTecnologia,OfertaHabilidad2,OfertaTecnologia2, Educacion, Habilidad, Tecnologia, Candidato, OfertaLaboral, Postulacion, calcular_puntaje, asignar_puntajes_automatica 

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

        edu = Educacion(nombre="universitario")
        edu2 = Educacion(nombre="secundario")
        tec = Tecnologia(nombre="java")
        tec2 = Tecnologia(nombre="sql")
        tec3 = Tecnologia(nombre="aws")
        tec4 = Tecnologia(nombre="python")
        hab = Habilidad(nombre="liderazgo")
        hab2 = Habilidad(nombre="adaptabilidad")
        hab3 = Habilidad(nombre="empatia")
        hab4 = Habilidad(nombre="autodidacta")

        db.session.add_all([edu, edu2, tec, tec2, tec3, tec4, hab, hab2, hab3, hab4])
        db.session.commit()

        oferta = OfertaLaboral(
            nombre="Desarrollador Backend SR",
            fecha_cierre=datetime.now(),
            max_candidatos=10,
            cant_candidatos=0,
            remuneracion="100000",
            beneficio="Remoto",
            descripcion="Se busca desarrollador backend con 3 años de experiencia",
            estado="Activa",
            modalidad= 'Local',
            usuario_responsable="Fernando"
        )
        db.session.add(oferta)
        db.session.commit()

        db.session.add_all([
            OfertaEducacion(idOfer=oferta.idOfer, idEdu=edu.idedu, importancia=3),
            OfertaEducacion(idOfer=oferta.idOfer, idEdu=edu2.idedu, importancia=1),
            OfertaTecnologia(idOfer=oferta.idOfer, idTec=tec.idtec, importancia=2),
            OfertaTecnologia(idOfer=oferta.idOfer, idTec=tec2.idtec, importancia=1),
            OfertaTecnologia(idOfer=oferta.idOfer, idTec=tec3.idtec, importancia=1),  
            OfertaTecnologia(idOfer=oferta.idOfer, idTec=tec4.idtec, importancia=0),
            OfertaTecnologia2(idOfer=oferta.idOfer, idTec2=tec.idtec, importancia=2),  
            OfertaTecnologia2(idOfer=oferta.idOfer, idTec2=tec2.idtec, importancia=1),
            OfertaTecnologia2(idOfer=oferta.idOfer, idTec2=tec3.idtec, importancia=0),
            OfertaTecnologia2(idOfer=oferta.idOfer, idTec2=tec4.idtec, importancia=0),
            OfertaHabilidad(idOfer=oferta.idOfer, idHab=hab.idhab, importancia=3),
            OfertaHabilidad(idOfer=oferta.idOfer, idHab=hab2.idhab, importancia=2),
            OfertaHabilidad(idOfer=oferta.idOfer, idHab=hab3.idhab, importancia=0),
            OfertaHabilidad(idOfer=oferta.idOfer, idHab=hab4.idhab, importancia=0),
            OfertaHabilidad2(idOfer=oferta.idOfer, idHab2=hab.idhab, importancia=3),
            OfertaHabilidad2(idOfer=oferta.idOfer, idHab2=hab2.idhab, importancia=2),
            OfertaHabilidad2(idOfer=oferta.idOfer, idHab2=hab3.idhab, importancia=0),
            OfertaHabilidad2(idOfer=oferta.idOfer, idHab2=hab4.idhab, importancia=0),
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
            idtec2 = tec2.idtec,
            idhab=hab.idhab,
            idhab2 = hab2.idhab
        )
        db.session.add(candidato)
        db.session.commit()

        post = Postulacion(
            idCandidato=candidato.id,
            idOfer=oferta.idOfer,
            experiencia=candidato.experiencia,
            idedu=candidato.idedu,
            idtec=candidato.idtec,
            idtec2=candidato.idtec2,
            idhab=candidato.idhab,
            idhab2=candidato.idhab2,
            aptitud=True,
            puntaje=0
        )

        db.session.add(post)
        db.session.commit()

        app.test_ids = {
            "universitario": edu.idedu,
            "secundario": edu2.idedu,
            "java": tec.idtec,
            "sql": tec2.idtec,
            "python": tec3.idtec,
            "aws": tec4.idtec,
            "liderazgo": hab.idhab,
            "adaptabilidad": hab2.idhab,
            "empatia": hab3.idhab,
            "autodidacta": hab4.idhab
        }

        yield oferta.idOfer
        db.session.remove()
        db.drop_all()

#Test que comprueba la asignacion de puntaje a un candidato
def test_agregar_puntaje(app, setup_db):
    with app.app_context():
        oferta_id = setup_db
        asignar_puntajes_automatica(setup_db)
        postulacion = Postulacion.query.filter_by(idCandidato="JosePerez@gmail.com", idOfer=oferta_id).first()
        puntaje_esperado = (5 * 2 + 3 * 3 + 2 * 5 + 1 * 5 + 2 * 2 + 3 * 2)
        assert postulacion.puntaje == puntaje_esperado 
        
#Test que comprueba que se calcule el puntaje a 2 candidatos correctamente
@pytest.mark.parametrize(
    "nombre, apellido, email, telefono, ubicacion, experiencia, educacion, tecnologia1,tecnologia2,habilidad1, habilidad2",
    [
        ('Lucas', 'Abalos', 'correoDePueba123@gmail.com', '1135356456', 'Buenos Aires', 3, "universitario", "java", "aws", "adaptabilidad","empatia"),
        ('Hernesto', 'Gonzalez', 'correoDePueba4123@gmail.com', '1343567856', 'Buenos Aires', 6, "secundario", "sql","python", "liderazgo", "autodidacta"),
        ('Pedro', 'Gonzalez', 'correoDePueba41235@gmail.com', '1343567856', 'Buenos Aires', 6, "universitario", "java","sql", "autodidacta", "empatia"),

    ]
)
def test_calcular_puntaje_params(app, setup_db, nombre, apellido, email, telefono, ubicacion, experiencia, educacion, tecnologia1,tecnologia2, habilidad1, habilidad2):
    with app.app_context():
        oferta_id = setup_db

        postulante = Candidato(
            id=email,
            nombre=nombre,
            apellido=apellido,
            mail=email,
            telefono=telefono,
            ubicacion=ubicacion,
            experiencia=experiencia,
            idedu=app.test_ids[educacion],
            idtec=app.test_ids[tecnologia1],
            idtec2=app.test_ids[tecnologia2],
            idhab=app.test_ids[habilidad1],
            idhab2=app.test_ids[habilidad2],
        )
        db.session.add(postulante)
        db.session.commit()

        postulacion = Postulacion(
            idCandidato=postulante.id,
            idOfer=oferta_id,
            experiencia=postulante.experiencia,
            idedu=postulante.idedu,
            idtec=postulante.idtec,
            idtec2=postulante.idtec2,
            idhab=postulante.idhab,
            idhab2=postulante.idhab2,
            aptitud=True,
            puntaje=0
        )

        db.session.add(postulacion)
        db.session.commit()
        
        puntaje_esperado = (
            experiencia * 2 +
            OfertaEducacion.query.filter_by(idOfer=oferta_id, idEdu=postulacion.idedu).first().importancia * 3 +
            OfertaTecnologia.query.filter_by(idOfer=oferta_id, idTec=postulacion.idtec).first().importancia * 5 +
            OfertaTecnologia2.query.filter_by(idOfer=oferta_id, idTec2=postulacion.idtec2).first().importancia * 5 +
            OfertaHabilidad.query.filter_by(idOfer=oferta_id, idHab=postulacion.idhab).first().importancia * 2 +
            OfertaHabilidad2.query.filter_by(idOfer=oferta_id, idHab2=postulacion.idhab2).first().importancia * 2
        )

        assert calcular_puntaje(postulante) == puntaje_esperado

def test_ranking(app, setup_db):
    with app.app_context():
        ids = app.test_ids
        oferta_id = setup_db

        candidatos = [
            Candidato(
                id="lucas@mail.com",
                nombre="Lucas",
                apellido="Abalos",
                mail="lucas@mail.com",
                telefono="1111111111",
                ubicacion="Buenos Aires",
                experiencia=3,
                idedu=ids["universitario"],
                idtec=ids["java"],
                idtec2=ids["aws"],
                idhab=ids["adaptabilidad"],
                idhab2=ids["empatia"]
            ),
            Candidato(
                id="hernesto@mail.com",
                nombre="Hernesto",
                apellido="Gonzalez",
                mail="hernesto@mail.com",
                telefono="2222222222",
                ubicacion="Buenos Aires",
                experiencia=6,
                idedu=ids["secundario"],
                idtec=ids["sql"],
                idtec2=ids["python"],
                idhab=ids["liderazgo"],
                idhab2=ids["autodidacta"]
            )
        ]
        db.session.add_all(candidatos)
        db.session.commit()

        for candidato in candidatos:
            postulacion = Postulacion(
                idCandidato=candidato.id,
                idOfer=oferta_id,
                experiencia=candidato.experiencia,
                idedu=candidato.idedu,
                idtec=candidato.idtec,
                idtec2=candidato.idtec2,
                idhab=candidato.idhab,
                idhab2=candidato.idhab2,
                aptitud=True,
                puntaje=0  
            )
            db.session.add(postulacion)
        db.session.commit()

        asignar_puntajes_automatica(oferta_id)

        puntajes = [
            p.puntaje for p in Postulacion.query
                .filter_by(idOfer=oferta_id)
                .order_by(Postulacion.puntaje.desc())
                .all()
        ]

        assert puntajes == sorted(puntajes, reverse=True)

#Test que se encarga de verificar que el sistema maneje correctamente un empate de puntaje entre candidatos. 
def test_ranking_con_empate(app, setup_db):
    with app.app_context():
        ids = app.test_ids
        oferta_id = setup_db

        Candidato.query.delete()
        Postulacion.query.delete()
        db.session.commit()

        candidatos = [
            Candidato(
                id="empate1@mail.com",
                nombre="Ana",
                apellido="Lopez",
                mail="empate1@mail.com",
                telefono="1111111111",
                ubicacion="Buenos Aires",
                experiencia=4,
                idedu=ids["universitario"],
                idtec=ids["sql"],
                idtec2=ids["aws"],
                idhab=ids["liderazgo"],
                idhab2=ids["autodidacta"]
            ),
            Candidato(
                id="empate2@mail.com",
                nombre="Bruno",
                apellido="Martinez",
                mail="empate2@mail.com",
                telefono="2222222222",
                ubicacion="CABA",
                experiencia=4,
                idedu=ids["universitario"],
                idtec=ids["sql"],
                idtec2=ids["aws"],
                idhab=ids["liderazgo"],
                idhab2=ids["autodidacta"]
            )
        ]
        db.session.add_all(candidatos)
        db.session.commit()

        
        for c in candidatos:
            postulacion = Postulacion(
                idCandidato=c.id,
                idOfer=oferta_id,
                experiencia=c.experiencia,
                idedu=c.idedu,
                idtec=c.idtec,
                idtec2=c.idtec2,
                idhab=c.idhab,
                idhab2=c.idhab2,
                aptitud=True,
                puntaje=0  
            )
            db.session.add(postulacion)
        db.session.commit()

        asignar_puntajes_automatica(oferta_id)
        
        puntajes = [
            p.puntaje for p in Postulacion.query
                .filter_by(idOfer=oferta_id)
                .order_by(Postulacion.puntaje.desc())
                .all()
        ]

        assert puntajes == sorted(puntajes, reverse=True)
        assert puntajes.count(puntajes[0]) >= 2

#Test que verifica que no se le asigne el puntaje a un candidato no apto
def test_calcular_puntaje_a_no_apto(app, setup_db):
    with app.app_context():
        ids = app.test_ids
        oferta_id = setup_db

        Candidato.query.delete()
        Postulacion.query.delete()
        db.session.commit()

        candidato = Candidato(
            id="empate2@mail.com",
            nombre="Bruno",
            apellido="Martinez",
            mail="empate2@mail.com",
            telefono="2222222222",
            ubicacion="CABA",
            experiencia=4,
            idedu=ids["universitario"],
            idtec=ids["sql"],
            idtec2=ids["aws"],
            idhab=ids["liderazgo"],
            idhab2=ids["autodidacta"]
        )

        db.session.add(candidato)
        db.session.commit()

        postulacion = Postulacion(
            idCandidato=candidato.id,
            idOfer=oferta_id,
            experiencia=candidato.experiencia,
            idedu=candidato.idedu,
            idtec=candidato.idtec,
            idtec2=candidato.idtec2,
            idhab=candidato.idhab,
            idhab2=candidato.idhab2,
            aptitud=False,
            puntaje=0 
        )

        db.session.add(postulacion)
        db.session.commit()

        asignar_puntajes_automatica(oferta_id)
        postulacion = Postulacion.query.filter_by(idCandidato=candidato.id, idOfer=oferta_id).first()
        assert postulacion.puntaje == 0

#Test que verifica que en un ranking con candidatos no aptos ninguno tenga puntaje
def test_ranking_sin_aptos(app, setup_db):
    with app.app_context():
        ids = app.test_ids
        oferta_id = setup_db

        Candidato.query.delete()
        Postulacion.query.delete()
        db.session.commit()

        candidatos = [
            Candidato(
                id="noapto1@mail.com",
                nombre="Ana",
                apellido="Lopez",
                mail="noapto1@mail.com",
                telefono="1111111111",
                ubicacion="Buenos Aires",
                experiencia=4,
                idedu=ids["universitario"],
                idtec=ids["sql"],
                idtec2=ids["aws"],
                idhab=ids["liderazgo"],
                idhab2=ids["autodidacta"]
            ),
            Candidato(
                id="noapto2@mail.com",
                nombre="Bruno",
                apellido="Martinez",
                mail="noapto2@mail.com",
                telefono="2222222222",
                ubicacion="CABA",
                experiencia=4,
                idedu=ids["universitario"],
                idtec=ids["sql"],
                idtec2=ids["aws"],
                idhab=ids["liderazgo"],
                idhab2=ids["autodidacta"]
            )
        ]
        db.session.add_all(candidatos)
        db.session.commit()

        for c in candidatos:
            postulacion = Postulacion(
                idCandidato=c.id,
                idOfer=oferta_id,
                experiencia=c.experiencia,
                idedu=c.idedu,
                idtec=c.idtec,
                idtec2=c.idtec2,
                idhab=c.idhab,
                idhab2=c.idhab2,
                aptitud=False,
                puntaje=0  
            )
            db.session.add(postulacion)
        db.session.commit()

        asignar_puntajes_automatica(oferta_id)

        puntajes = [
            p.puntaje for p in Postulacion.query
                .filter_by(idOfer=oferta_id)
                .order_by(Postulacion.puntaje.desc())
                .all()
        ]

        assert len(puntajes) == 2

        for puntaje in puntajes:
            assert puntaje == 0