import pytest
from app import app as appLocal, db, Postulacion, OfertaLaboral, OfertaEducacion, OfertaTecnologia, OfertaHabilidad,OfertaHabilidad2,OfertaTecnologia2, Candidato, Educacion, Tecnologia, Tecnologia2, Habilidad2, Habilidad
from datetime import datetime

@pytest.fixture(scope="module")
def setup_metricas():
    with appLocal.app_context():
        oferta = OfertaLaboral(
            nombre="Oferta Test Métricas",
            fecha_cierre=datetime(2030, 1, 1),
            max_candidatos="10",
            cant_candidatos = 0,
            remuneracion="1000",
            beneficio="Ninguno",
            descripcion="Se busca desarrollador backend con 3 años de experiencia",
            estado="Activa",
            modalidad='Local',
            usuario_responsable="Fernando"
        )
        db.session.add(oferta)
        db.session.commit()

        edu = Educacion.query.filter_by(nombre="postgrado").first()
        tec1 = Tecnologia.query.filter_by(nombre="aws").first()
        tec2 = Tecnologia2.query.filter_by(nombre ="azure").first()
        hab1 = Habilidad.query.filter_by(nombre="adaptabilidad").first()
        hab2 = Habilidad2.query.filter_by(nombre="autodidacta").first()

        oferta_edu = OfertaEducacion(idOfer=oferta.idOfer, idEdu=edu.idedu, importancia=3)
        oferta_tec = OfertaTecnologia(idOfer=oferta.idOfer, idTec=tec1.idtec, importancia=3)
        oferta_tec2 = OfertaTecnologia2(idOfer=oferta.idOfer, idTec2=tec2.idtec2, importancia=3)
        oferta_hab = OfertaHabilidad(idOfer=oferta.idOfer, idHab=hab1.idhab, importancia=3)
        oferta_hab2 = OfertaHabilidad2(idOfer=oferta.idOfer, idHab2=hab2.idhab2, importancia=3)
        
        db.session.add_all([oferta_edu, oferta_tec, oferta_tec2, oferta_hab, oferta_hab2])
        db.session.commit()
        for i in range(3):
            candidato = Candidato(
                id=f"apto{i}@gmail.com{oferta.idOfer}",
                nombre=f"Apto{i}",
                apellido="Test",
                mail=f"apto{i}@gmail.com",
                telefono="1123123456",
                ubicacion="Buenos Aires",
                experiencia=8,
                idedu=edu.idedu,
                idtec=tec1.idtec,
                idtec2=tec2.idtec2,
                idhab=hab1.idhab,
                idhab2=hab2.idhab2,
            )

            post_apto = Postulacion(
                idCandidato=candidato.id,
                idOfer=oferta.idOfer,
                experiencia=candidato.experiencia,
                idedu=candidato.idedu,
                idtec=candidato.idtec,
                idtec2=candidato.idtec2,
                idhab=candidato.idhab,
                idhab2=candidato.idhab2,
                aptitud=True,
                puntaje=90
            )
            db.session.add_all([candidato, post_apto])
        for i in range(2):
            candidato = Candidato(
                id=f"noapto{i}@gmail.com{oferta.idOfer}",
                nombre=f"NoApto{i}",
                apellido="Test",
                mail=f"noapto{i}@gmail.com",
                telefono="1165432321",
                ubicacion="Cordoba",
                experiencia=1,
                idedu=edu.idedu,
                idtec=tec1.idtec,
                idtec2=tec2.idtec2,
                idhab=hab1.idhab,
                idhab2=hab2.idhab2,
            )

            post_no_apto = Postulacion(
                idCandidato=candidato.id,
                idOfer=oferta.idOfer,
                experiencia=candidato.experiencia,
                idedu=candidato.idedu,
                idtec=candidato.idtec,
                idtec2=candidato.idtec2,
                idhab=candidato.idhab,
                idhab2=candidato.idhab2,
                aptitud=False,
                puntaje=0
            )
            db.session.add_all([candidato, post_no_apto])
        db.session.commit()

        yield oferta.idOfer

        Postulacion.query.filter_by(idOfer=oferta.idOfer).delete()
        Candidato.query.filter(Candidato.id.like(f"%{oferta.idOfer}")).delete()
        OfertaEducacion.query.filter_by(idOfer=oferta.idOfer).delete()
        OfertaTecnologia.query.filter_by(idOfer=oferta.idOfer).delete()
        OfertaTecnologia2.query.filter_by(idOfer=oferta.idOfer).delete()
        OfertaHabilidad.query.filter_by(idOfer=oferta.idOfer).delete()
        OfertaHabilidad2.query.filter_by(idOfer=oferta.idOfer).delete()
        OfertaLaboral.query.filter_by(idOfer=oferta.idOfer).delete()
        db.session.commit()

@pytest.fixture
def client():
    appLocal.config['TESTING'] = True
    appLocal.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/erp_rrhh.db'
    with appLocal.test_client() as cliente:
        yield cliente

def test_metricas_candidatos_totales(client, setup_metricas):
    oferta_id = setup_metricas

    with client.session_transaction() as sess:
        sess["username"] = "Fernando"
        sess["type"] = "Admin_RRHH"

    response = client.get(f'/metricas/{oferta_id}')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["total_postulantes"] == 5
    assert data["aptos"] == 3
    assert data["no_aptos"] == 2


def test_metricas_cantidad_por_etiqueta(client, setup_metricas):
    oferta_id = setup_metricas

    with client.session_transaction() as sess:
        sess["username"] = "Fernando"
        sess["type"] = "Admin_RRHH"

    response = client.get(f'/metricas/{oferta_id}')
    assert response.status_code == 200

    data = response.get_json()

    assert data["cant_educacion"][0] == 5
    assert data["cant_tecnologia"][0] == 5
    assert data["cant_tecnologia2"][0] == 5
    assert data["cant_habilidad"][0] == 5
    assert data["cant_habilidad2"][0] == 5

def test_metricas_promedios(client, setup_metricas):
    oferta_id = setup_metricas

    with client.session_transaction() as sess:
        sess["username"] = "Fernando"
        sess["type"] = "Admin_RRHH"

    response = client.get(f'/metricas/{oferta_id}')
    assert response.status_code == 200
    
    data = response.get_json()

    assert data["exp_educacion"]["postgrado"] == 5.2
    assert data["exp_tecnologia"]["aws"] == 5.2
    assert data["exp_tecnologia2"]["azure"] == 5.2
    assert data["exp_habilidad"]["adaptabilidad"] == 5.2
    assert data["exp_habilidad2"]["autodidacta"] == 5.2
    assert "liderazgo" not in data["exp_habilidad"]
    assert "python" not in data["exp_tecnologia"]

def test_metricas_por_provincias(client, setup_metricas):
    oferta_id = setup_metricas

    with client.session_transaction() as sess:
        sess["username"] = "Fernando"
        sess["type"] = "Admin_RRHH"

    response = client.get(f'/metricas/{oferta_id}')
    assert response.status_code == 200
    
    data = response.get_json()

    assert data["provincias_postulantes"]["Buenos Aires"] == 3
    assert data["provincias_postulantes"]["Cordoba"] == 2
    assert "Mendoza" not in data["provincias_postulantes"]
    assert "Banana" not in data["provincias_postulantes"]

def test_metricas_oferta_inexistente(client, setup_metricas):
    oferta_id = 43

    with client.session_transaction() as sess:
        sess["username"] = "Fernando"
        sess["type"] = "Admin_RRHH"

    response = client.get(f'/metricas/{oferta_id}')
    assert response.status_code == 404