import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import app as app_local, db, Educacion, Tecnologia, Habilidad, OfertaLaboral, OfertaEducacion, OfertaTecnologia, OfertaHabilidad

@pytest.fixture
def app():
    app_local = Flask(__name__)
    app_local.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app_local.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app_local.config['TESTING'] = True
    db.init_app(app_local)
    return app_local

@pytest.fixture
def setup_db(app):
    with app.app_context():
        db.create_all()

        edu = Educacion(nombre='secundario')
        tec = Tecnologia(nombre='java')
        hab = Habilidad(nombre='liderazgo')

        db.session.add_all([edu, tec, hab])
        db.session.commit()

        oferta = OfertaLaboral(nombre="FrontEnd Developer JR", fecha_cierre=datetime.now(), max_candidatos=1, cant_candidatos = 0,remuneracion="100000", beneficio = "Home Office", estado = 'Activa', modalidad='Local',  usuario_responsable="Fernando")
        db.session.add(oferta)
        db.session.commit()

        db.session.add(OfertaEducacion(idOfer=oferta.idOfer, idEdu=edu.idedu, importancia=1))
        db.session.add(OfertaTecnologia(idOfer=oferta.idOfer, idTec=tec.idtec, importancia=1))
        db.session.add(OfertaHabilidad(idOfer=oferta.idOfer, idHab=hab.idhab, importancia=1))
        db.session.commit()

        yield db

        db.session.remove()
        db.drop_all()

#Test que prueba el cambio de importancia en la etiqueta educacion
def test_cambiar_importancia_oferta_educacion(app, setup_db):
    with app.app_context():
        oferta = OfertaLaboral.query.first()
        edu = Educacion.query.filter_by(nombre="secundario").first()
        rel = OfertaEducacion.query.filter_by(idOfer=oferta.idOfer, idEdu=edu.idedu).first()
        rel.importancia = 3
        db.session.commit()
        rel_actualizada = OfertaEducacion.query.filter_by(idOfer=oferta.idOfer, idEdu=edu.idedu).first()
        assert rel_actualizada.importancia == 3

#Test que prueba el cambio de importancia en la etiqueta tecnologia
def test_cambiar_importancia_oferta_tecnologia(app, setup_db):
    with app.app_context():
        oferta = OfertaLaboral.query.first()
        tec = Tecnologia.query.filter_by(nombre="java").first()
        rel = OfertaTecnologia.query.filter_by(idOfer=oferta.idOfer, idTec=tec.idtec).first()
        rel.importancia = 3
        db.session.commit()
        rel_actualizada = OfertaTecnologia.query.filter_by(idOfer=oferta.idOfer, idTec=tec.idtec).first()
        assert rel_actualizada.importancia == 3

#Test que prueba el cambio de importancia en la etiqueta habilidad
def test_cambiar_importancia_oferta_habilidad(app, setup_db):
    with app.app_context():
        oferta = OfertaLaboral.query.first()
        hab = Habilidad.query.filter_by(nombre="liderazgo").first()
        rel = OfertaHabilidad.query.filter_by(idOfer=oferta.idOfer, idHab=hab.idhab).first()
        rel.importancia = 3
        db.session.commit()
        rel_actualizada = OfertaHabilidad.query.filter_by(idOfer=oferta.idOfer, idHab=hab.idhab).first()
        assert rel_actualizada.importancia == 3