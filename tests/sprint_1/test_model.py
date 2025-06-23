import pytest
import joblib
import pandas as pd
from datetime import datetime
from app import app as appLocal, db, OfertaLaboral, Candidato, Educacion, Tecnologia, Tecnologia2,Habilidad, Habilidad2,OfertaEducacion,OfertaHabilidad,OfertaHabilidad2,OfertaTecnologia,OfertaTecnologia2, Postulacion

@pytest.fixture
def client():
    appLocal.config['TESTING'] = True
    appLocal.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/erp_rrhh.db'
    with appLocal.test_client() as cliente:
        yield cliente

def loadModel():
    modelo_path = "modelo_candidatos.pkl"

    try:
        modelo = joblib.load(modelo_path)
        return modelo
    except FileNotFoundError:
        pytest.fail(f"No se encontro el arhivo del modelo")

#Test que verifica que un candidato es apto
def test_model_prediction_apto():
    modelo = loadModel()

    columnas = ["Educacion", "Tecnologías", "Tecnologías2", "Habilidades", "Habilidades2"]
    datos_prueba = pd.DataFrame([[0, 0, 0, 0, 0]], columns=columnas)

    try:
        prediccion = modelo.predict(datos_prueba)
    except Exception as e:
        pytest.fail(f"El modelo falló al realizar la predicción: {e}")

    assert prediccion[0] == 1

#Test que verifica que un candidato es no apto
def test_model_prediction_no_apto():
    modelo = loadModel()

    columnas = ["Educacion", "Tecnologías", "Tecnologías2", "Habilidades", "Habilidades2"]
    datos_prueba = pd.DataFrame([[2, 3, 1, 1, 2]], columns=columnas)

    try:
        prediccion = modelo.predict(datos_prueba)
    except Exception as e:
        pytest.fail(f"El modelo falló al realizar la predicción: {e}")

    assert prediccion[0] == 0

#Test que verifica que se aplique el modelo al cerrar una oferta (hablarlo con fer)
def test_model_aplicado_al_cerrar_oferta(client):
    with client.session_transaction() as sess:
        sess["username"] = "Fernando"
        sess["type"] = "Admin_RRHH"

    with client.application.app_context():
        oferta = OfertaLaboral(
            nombre="Oferta Test",
            fecha_cierre=datetime(2025, 1, 1),
            max_candidatos=10,
            cant_candidatos = 0,
            remuneracion="1000",
            beneficio="Home Office",
            estado="Activa",
            modalidad= 'Local',
            usuario_responsable="Fernando"
        )
        db.session.add(oferta)
        db.session.flush()

        edu = Educacion.query.filter_by(nombre="postgrado").first()
        tec1 = Tecnologia.query.filter_by(nombre="aws").first()
        tec2 = Tecnologia2.query.filter_by(nombre ="azure").first()
        hab1 = Habilidad.query.filter_by(nombre="adaptabilidad").first()
        hab2 = Habilidad2.query.filter_by(nombre="autodidacta").first()

        oferta_edu = OfertaEducacion(idOfer=oferta.idOfer, idEdu=edu.idedu, importancia=3)
        oferta_tec = OfertaTecnologia(idOfer=oferta.idOfer, idTec=tec1.idtec, importancia=3)
        oferta_tec2 = OfertaTecnologia2(idOfer=oferta.idOfer, idTec2=tec2.idtec2, importancia=2)
        oferta_hab = OfertaHabilidad(idOfer=oferta.idOfer, idHab=hab1.idhab, importancia=3)
        oferta_hab2 = OfertaHabilidad2(idOfer=oferta.idOfer, idHab2=hab2.idhab2, importancia=2)

        db.session.add_all([oferta_edu, oferta_tec, oferta_tec2, oferta_hab, oferta_hab2])
        db.session.commit()

        c_apto = Candidato(
            id="apto_test@gmail.com",
            nombre="Apto",
            apellido="ApellidoTest",
            mail="apto_test@gmail.com",
            telefono="1111111111",
            ubicacion="Buenos Aires",
            experiencia=10,
            idedu=edu.idedu,
            idtec=tec1.idtec,
            idtec2=tec2.idtec2,
            idhab=hab1.idhab,
            idhab2=hab2.idhab2,
        )

        c_noapto = Candidato(
            id="noapto_test@gmail.com",
            nombre="NoApto",
            apellido="Apellidonoapto",
            mail="noapto_test@gmail.com",
            telefono="1122222222",
            ubicacion="Cordoba",
            experiencia=2,
            idedu=2,
            idtec=3,
            idtec2=1,
            idhab=1,
            idhab2=2,
        )

        db.session.add_all([c_apto, c_noapto])
        db.session.commit()
        
        oferta_id = oferta.idOfer 

        post_apto = Postulacion(
            idCandidato=c_apto.id,
            idOfer=oferta_id,
            experiencia=c_apto.experiencia,
            idedu=c_apto.idedu,
            idtec=c_apto.idtec,
            idtec2=c_apto.idtec2,
            idhab=c_apto.idhab,
            idhab2=c_apto.idhab2,
            puntaje=0
        )
     
        post_noapto = Postulacion(
            idCandidato=c_noapto.id,
            idOfer=oferta_id,
            experiencia=c_noapto.experiencia,
            idedu=c_noapto.idedu,
            idtec=c_noapto.idtec,
            idtec2=c_noapto.idtec2,
            idhab=c_noapto.idhab,
            idhab2=c_noapto.idhab2,
            puntaje=0
        )

        db.session.add_all([post_apto, post_noapto])
        db.session.commit()

    response = client.post(f"/cerrar_oferta/{oferta_id}")
    assert response.status_code == 302

    with client.application.app_context():
        post1 = Postulacion.query.filter_by(idCandidato="apto_test@gmail.com", idOfer=oferta_id).first()
        post2 = Postulacion.query.filter_by(idCandidato="noapto_test@gmail.com", idOfer=oferta_id).first()

        # assert post1.aptitud is True
        assert post2.aptitud is False

        Candidato.query.filter(Candidato.id.in_([ "apto_test@gmail.com", "noapto_test@gmail.com"])).delete()
        Postulacion.query.filter(Postulacion.idCandidato.in_([ "apto_test@gmail.com", "noapto_test@gmail.com"])).delete()
        OfertaLaboral.query.filter_by(idOfer=oferta_id).delete()
        db.session.commit()