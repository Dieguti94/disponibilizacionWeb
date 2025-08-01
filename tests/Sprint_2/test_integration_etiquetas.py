import pytest
from app import app as appLocal, db, Educacion, Tecnologia, Habilidad,OfertaEducacion,OfertaLaboral,OfertaTecnologia,OfertaHabilidad

@pytest.fixture
def client():
    appLocal.config['TESTING'] = True
    appLocal.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/erp_rrhh.db'
    with appLocal.test_client() as cliente:
        with appLocal.app_context():
            yield cliente

#Test que prueba que las etiquetas se actualizen con los datos permitidos
@pytest.mark.parametrize(
    "importancia",
    [
        (0),
        (1),
        (2),
        (3)
    ]
)
def test_actualizacion_importancia(client, importancia):
    with appLocal.app_context():
        oferta = db.session.query(OfertaLaboral).first()
        idOfer = oferta.idOfer

        edu = db.session.execute(db.select(Educacion).filter_by(nombre="secundario")).scalar_one()
        id_edu = edu.idedu

        tec = db.session.execute(db.select(Tecnologia).filter_by(nombre="java")).scalar_one()
        id_tec = tec.idtec

        hab = db.session.execute(db.select(Habilidad).filter_by(nombre="liderazgo")).scalar_one()
        id_hab = hab.idhab

        edu_rel = OfertaEducacion.query.filter_by(idOfer=idOfer, idEdu=id_edu).first()
        tec_rel = OfertaTecnologia.query.filter_by(idOfer=idOfer, idTec=id_tec).first()
        hab_rel = OfertaHabilidad.query.filter_by(idOfer=idOfer, idHab=id_hab).first()
        valor_edu_original = edu_rel.importancia
        valor_tec_original = tec_rel.importancia
        valor_hab_original = hab_rel.importancia

    with client.session_transaction() as sess:
        sess["username"] = "Fernando"
        sess["type"] = "Admin_RRHH"

    respuesta = client.post(f"/asignar_valores/{idOfer}", data={
        "educacion_id": id_edu,
        "valor_educacion": importancia,
        "tecnologia_id": id_tec,
        "valor_tecnologia": importancia,
        "habilidad_id": id_hab,
        "valor_habilidad": importancia
    }, follow_redirects=True)

    assert respuesta.status_code == 200

    with appLocal.app_context():
        edu_rel = OfertaEducacion.query.filter_by(idOfer=idOfer, idEdu=id_edu).first()
        assert edu_rel.importancia == importancia
        edu_rel.importancia = valor_edu_original

        tec_rel = OfertaTecnologia.query.filter_by(idOfer=idOfer, idTec=id_tec).first()
        assert tec_rel.importancia == importancia
        tec_rel.importancia = valor_tec_original

        hab_rel = OfertaHabilidad.query.filter_by(idOfer=idOfer, idHab=id_hab).first()
        assert hab_rel.importancia == importancia
        hab_rel.importancia = valor_hab_original

        db.session.commit()

#Test que prueba que no se actualizen las etiquetas con datos no validos (❌Fallando❌)
@pytest.mark.parametrize(
        "importancia",
        [
            (-1),
            (4)
        ]
)
def test_actualizar_etiquetas_fuera_de_rango(client, importancia):
    with appLocal.app_context():
        oferta = db.session.query(OfertaLaboral).first()
        id_oferta = oferta.idOfer
        edu = db.session.execute(db.select(Educacion).filter_by(nombre="secundario")).scalar_one()
        id_edu = edu.idedu
        
        tec = db.session.execute(db.select(Tecnologia).filter_by(nombre ="java")).scalar_one()
        id_tec = tec.idtec
       
        hab = db.session.execute(db.select(Habilidad).filter_by(nombre ="liderazgo")).scalar_one()
        id_hab = hab.idhab

        edu_rel = OfertaEducacion.query.filter_by(idOfer=id_oferta, idEdu=id_edu).first()
        tec_rel = OfertaTecnologia.query.filter_by(idOfer=id_oferta, idTec=id_tec).first()
        hab_rel = OfertaHabilidad.query.filter_by(idOfer=id_oferta, idHab=id_hab).first()
        valor_edu_original = edu_rel.importancia
        valor_tec_original = tec_rel.importancia
        valor_hab_original = hab_rel.importancia

    with client.session_transaction() as sess:
            sess["username"] = "Fernando"
            sess["type"] = "Admin_RRHH"
       
    respuesta = client.post(f"/asignar_valores/{id_oferta}", data={
    "educacion_id": id_edu,
    "valor_educacion": importancia,
    "tecnologia_id": id_tec,
    "valor_tecnologia": importancia,
    "habilidad_id": id_hab,
    "valor_habilidad": importancia
    }, follow_redirects=True)

    assert respuesta.status_code == 200

    with appLocal.app_context():
        edu_rel = OfertaEducacion.query.filter_by(idOfer=id_oferta, idEdu=id_edu).first()
        tec_rel = OfertaTecnologia.query.filter_by(idOfer=id_oferta, idTec=id_tec).first()
        hab_rel = OfertaHabilidad.query.filter_by(idOfer=id_oferta, idHab=id_hab).first()

        assert edu_rel.importancia in [0, 1, 2, 3]
        assert tec_rel.importancia in [0, 1, 2, 3]
        assert hab_rel.importancia in [0, 1, 2, 3]

        assert edu_rel.importancia == valor_edu_original
        assert tec_rel.importancia == valor_tec_original
        assert hab_rel.importancia == valor_hab_original

#Test que verifica que no se pueda asignar la importancia a una oferta inexistente
def test_actualizar_etiquetas_con_oferta_inexistente(client):
    with client.session_transaction() as sess:
        sess["username"] = "Fernando"
        sess["type"] = "Admin_RRHH"

    with appLocal.app_context():
        
        edu = db.session.execute(db.select(Educacion).filter_by(nombre="secundario")).scalar_one()
        id_edu = edu.idedu
        
        tec = db.session.execute(db.select(Tecnologia).filter_by(nombre ="java")).scalar_one()
        id_tec = tec.idtec
       
        hab = db.session.execute(db.select(Habilidad).filter_by(nombre ="liderazgo")).scalar_one()
        id_hab = hab.idhab


    response = client.post(f"/asignar_valores/{23564}", data={
        "educacion_id": id_edu,
        "valor_educacion": 3,
        "tecnologia_id": id_tec,
        "valor_tecnologia": 3,
        "habilidad_id": id_hab,
        "valor_habilidad": 3
    }, follow_redirects=False)

    assert response.status_code == 302
    assert "/ver_ofertas" in response.headers["Location"]