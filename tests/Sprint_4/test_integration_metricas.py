import pytest
from app import app as appLocal, db, OfertaLaboral, OfertaEducacion, OfertaTecnologia, OfertaHabilidad, Candidato, Educacion, Tecnologia, Habilidad
from datetime import datetime

@pytest.fixture(scope="module")
def setup_metricas():
    with appLocal.app_context():
        # Crear oferta
        oferta = OfertaLaboral(
            nombre="Oferta Test Métricas",
            fecha_cierre=datetime(2030, 1, 1),
            max_candidatos="10",
            remuneracion="1000",
            beneficio="Ninguno",
            estado="Activa",
            usuario_responsable="Fernando"
        )
        db.session.add(oferta)
        db.session.commit()

        # Obtengo las etiquetas
        edu = Educacion.query.filter_by(nombre="Postgrado").first()
        tec = Tecnologia.query.filter_by(nombre = "Java").first()
        hab = Habilidad.query.filter_by(nombre = "Liderazgo").first()
        
        # Asociar etiquetas a la oferta
        db.session.add(OfertaEducacion(idOfer=oferta.idOfer, idEdu=edu.idedu, importancia=3))
        db.session.add(OfertaTecnologia(idOfer=oferta.idOfer, idTec=tec.idtec, importancia=3))
        db.session.add(OfertaHabilidad(idOfer=oferta.idOfer, idHab=hab.idhab, importancia=3))
        db.session.commit()

        # Crear candidatos (3 aptos, 2 no aptos)
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
                idtec=tec.idtec,
                idhab=hab.idhab,
                idOfer=oferta.idOfer,
                aptitud=True,
                puntaje=90
            )
            db.session.add(candidato)
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
                idtec=tec.idtec,
                idhab=hab.idhab,
                idOfer=oferta.idOfer,
                aptitud=False,
                puntaje=0
            )
            db.session.add(candidato)
        db.session.commit()

        yield oferta.idOfer

        # Limpieza: borrar candidatos, etiquetas y oferta
        Candidato.query.filter_by(idOfer=oferta.idOfer).delete()
        OfertaEducacion.query.filter_by(idOfer=oferta.idOfer).delete()
        OfertaTecnologia.query.filter_by(idOfer=oferta.idOfer).delete()
        OfertaHabilidad.query.filter_by(idOfer=oferta.idOfer).delete()
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
    assert data["total_candidatos"] == 5
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

    assert data["cantidades"][0] == 5
    assert data["cantidades"][1] == 5
    assert data["cantidades"][2] == 5

def test_metricas_promedios(client, setup_metricas):
    oferta_id = setup_metricas

    with client.session_transaction() as sess:
        sess["username"] = "Fernando"
        sess["type"] = "Admin_RRHH"

    response = client.get(f'/metricas/{oferta_id}')
    assert response.status_code == 200
    
    data = response.get_json()

    assert data["promedios_experiencia"]["Postgrado"] == 5.2
    assert data["promedios_experiencia"]["Java"] == 5.2
    assert data["promedios_experiencia"]["Liderazgo"] == 5.2

def test_metricas_por_provincias(client, setup_metricas):
    oferta_id = setup_metricas

    with client.session_transaction() as sess:
        sess["username"] = "Fernando"
        sess["type"] = "Admin_RRHH"

    response = client.get(f'/metricas/{oferta_id}')
    assert response.status_code == 200
    
    data = response.get_json()

    assert data["provincias_candidatos"]["Buenos Aires"] == 3
    assert data["provincias_candidatos"]["Cordoba"] == 2
    assert "Mendoza" not in data["provincias_candidatos"]
    assert "Banana" not in data["provincias_candidatos"]

def test_metricas_oferta_inexistente(client, setup_metricas):
    oferta_id = 43

    with client.session_transaction() as sess:
        sess["username"] = "Fernando"
        sess["type"] = "Admin_RRHH"

    response = client.get(f'/metricas/{oferta_id}')
    assert response.status_code == 404