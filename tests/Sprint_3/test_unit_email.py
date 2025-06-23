import pytest
from flask import Flask
from unittest.mock import patch, MagicMock
from flask_sqlalchemy import SQLAlchemy
from app import db, email, Candidato,Postulacion, obtener_correos_aptos, obtener_correos_noaptos, enviar_correos_automatica, OfertaLaboral
from datetime import datetime

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

        oferta = OfertaLaboral(
            nombre="Desarrollador Backend SR",
            fecha_cierre=datetime.now(),
            max_candidatos=10,
            cant_candidatos=0,
            remuneracion="100000",
            beneficio="Remoto",
            estado="Activa",
            modalidad = 'Local',
            usuario_responsable="Fernando"
        )
        db.session.add(oferta)
        db.session.commit()

        candidato1 = Candidato(
            id="JosePerez@gmail.com",
            nombre="Jose",
            apellido="Abalos",
            mail="JosePerez@gmail.com",
            telefono="1122334455",
            ubicacion="Buenos Aires",
            experiencia=10,
            idedu=0,
            idtec=0,
            idtec2=0,
            idhab=0,
            idhab2=0,
        )

        post1 = Postulacion(
            idCandidato=candidato1.id,
            idOfer=oferta.idOfer,
            experiencia=candidato1.experiencia,
            idedu=candidato1.idedu,
            idtec=candidato1.idtec,
            idtec2=candidato1.idtec2,
            idhab=candidato1.idhab,
            idhab2=candidato1.idhab2,
            aptitud=True,
            puntaje=0
        )

        candidato2 = Candidato(
            id="PedroPascal@gmail.com",
            nombre="Pedro",
            apellido="Pascal",
            mail="PedroPascal@gmail.com",
            telefono="1123456789",
            ubicacion="Jujuy",
            experiencia=2,
            idedu=1,
            idtec=1,
            idtec2=1,
            idhab=1,
            idhab2=1
        )

        post2 = Postulacion(
            idCandidato=candidato2.id,
            idOfer=oferta.idOfer,
            experiencia=candidato2.experiencia,
            idedu=candidato2.idedu,
            idtec=candidato2.idtec,
            idtec2=candidato2.idtec2,
            idhab=candidato2.idhab,
            idhab2=candidato2.idhab2,
            aptitud=False,
            puntaje=0
        )

        candidato3 = Candidato(
            id="MartinGonzalez@gmail.com",
            nombre="Martin",
            apellido="Gonzalez",
            mail="MartinGonzalez@gmail.com",
            telefono="1198765432",
            ubicacion="Formosa",
            experiencia=1,
            idedu=2,
            idtec=1,
            idtec2=0,
            idhab=0,
            idhab2=1
        )

        post3 = Postulacion(
            idCandidato=candidato3.id,
            idOfer=oferta.idOfer,
            experiencia=candidato3.experiencia,
            idedu=candidato3.idedu,
            idtec=candidato3.idtec,
            idtec2=candidato3.idtec2,
            idhab=candidato3.idhab,
            idhab2=candidato3.idhab2,
            aptitud=False,
            puntaje=0
        )
        db.session.add_all([candidato1, post1, candidato2, post2, candidato3, post3])
        db.session.commit()

        yield oferta.idOfer  

        db.session.remove()
        db.drop_all()

#Test que prueba la obtencion de todos los correos de los candidatos aptos
def test_obtener_correos_aptos(app, setup_db):
    with app.app_context():
        candidatosAptos = obtener_correos_aptos(setup_db)

        assert len(candidatosAptos) == 1
        assert candidatosAptos[0][1] == "JosePerez@gmail.com"

#Test que prueba la obtencion de todos los correos de los candidatos no aptos
def test_obtener_correos_no_aptos(app, setup_db):
    with app.app_context():
        candidatoNoAptos = obtener_correos_noaptos(setup_db)

        assert len(candidatoNoAptos) == 2
        assert candidatoNoAptos[0][1] == "PedroPascal@gmail.com"
        assert candidatoNoAptos[1][1] == "MartinGonzalez@gmail.com"

#Test que prueba que se enviaron los mails a todos los candidatos aptos
def test_envio_email_apto(app, setup_db):
    with app.app_context():
        with patch.object(email, 'connect', autospec=True) as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value.__enter__.return_value = mock_conn

            aptos = obtener_correos_aptos(setup_db)

            enviar_correos_automatica(setup_db)
            llamadas = [llamada.args[0] for llamada in mock_conn.send.call_args_list]
            
            for msg in llamadas:
                destinatario = msg.recipients[0]
                if destinatario in aptos:
                    assert "Hola, hemos revisado tu perfil y estamos interesados en tu candidatura." in msg.body

#Test que prueba que se enviaron los mails a todos los candidatos no aptos
def test_envio_email_no_apto(app, setup_db):
    with app.app_context():
        with patch.object(email, 'connect', autospec=True) as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value.__enter__.return_value = mock_conn

            no_aptos = obtener_correos_noaptos(setup_db)

            enviar_correos_automatica(setup_db)

            llamadas = [llamada.args[0] for llamada in mock_conn.send.call_args_list]
            
            for msg in llamadas:
                destinatario = msg.recipients[0]
                if destinatario in no_aptos:
                    assert "Hola, lamentamos informarte que en esta oportunidad tu perfil no se ajusta a lo que buscamos." in msg.body