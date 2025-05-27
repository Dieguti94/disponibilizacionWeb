import pytest
from flask_sqlalchemy import SQLAlchemy
from app import app as appLocal, OfertaLaboral,OfertaEducacion,OfertaHabilidad,OfertaTecnologia, db, cerrar_oferta

@pytest.fixture
def client():
    appLocal.config['TESTING'] = True
    appLocal.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/erp_rrhh.db'
    
    with appLocal.app_context():
        with appLocal.test_client() as cliente:
            yield cliente

#Test que verifica que se cree la oferta y que impacte en la base de datos
def test_crear_oferta_exitosa(client):
    with appLocal.app_context():        
        with client.session_transaction() as sess:
            sess["username"] = "Fernando"
            sess["type"] = "Admin_RRHH"

        response = client.post('/crear_oferta', data={
            'nombre': 'Desarrollador Frontend SR',
            'fecha_cierre': '2025-06-01',
            'max_candidatos': '20',
            'remuneracion': '100000',
            'beneficio': 'Home Office',
            'estado': 'Activa',
            'usuario_responsable': 'Fernando' 
        })

        assert response.status_code in [200,302]

        oferta_laboral = OfertaLaboral.query.filter_by(nombre= 'Desarrollador Frontend SR').first()
        assert oferta_laboral is not None

        OfertaEducacion.query.filter_by(idOfer=oferta_laboral.idOfer).delete()
        OfertaTecnologia.query.filter_by(idOfer=oferta_laboral.idOfer).delete()
        OfertaHabilidad.query.filter_by(idOfer=oferta_laboral.idOfer).delete()
        
        db.session.delete(oferta_laboral)
        db.session.commit()

#Test que verifica la asignacion exitosa de las etiquetas a la oferta laboral
def test_asignacion_de_etiquetas_exitosa(client):
    with appLocal.app_context():
        with client.session_transaction() as sess:
            sess["username"] = "Fernando"
            sess["type"] = "Admin_RRHH"
        
        response = client.post('/crear_oferta', data={
            'nombre': 'Desarrollador Backend SR',
            'fecha_cierre': '2025-06-01',
            'max_candidatos': '20',
            'remuneracion': '100000',
            'beneficio': 'Home Office',
            'estado': 'Activa',
            'usuario_responsable': 'Fernando' 
        })

        assert response.status_code in [200,302]

        oferta_laboral = OfertaLaboral.query.filter_by(nombre = 'Desarrollador Backend SR').first();

        id_oferta = oferta_laboral.idOfer

        assert OfertaEducacion.query.filter_by(idOfer=id_oferta).count() > 0
        assert OfertaTecnologia.query.filter_by(idOfer=id_oferta).count() > 0
        assert OfertaHabilidad.query.filter_by(idOfer=id_oferta).count() > 0

        OfertaEducacion.query.filter_by(idOfer=oferta_laboral.idOfer).delete()
        OfertaTecnologia.query.filter_by(idOfer=oferta_laboral.idOfer).delete()
        OfertaHabilidad.query.filter_by(idOfer=oferta_laboral.idOfer).delete()

        db.session.delete(oferta_laboral)
        db.session.commit()

#Test que verifica que no se cree una oferta que ya existe
def test_oferta_duplicada(client):
    with appLocal.app_context():        
        with client.session_transaction() as sess:
            sess["username"] = "Fernando"
            sess["type"] = "Admin_RRHH"

        response1 = client.post('/crear_oferta', data={
            'nombre': 'Desarrollador Java JR',
            'fecha_cierre': '2025-06-01',
            'max_candidatos': '20',
            'remuneracion': '100000',
            'beneficio': 'Home Office',
            'estado': 'Activa',
            'usuario_responsable': 'Fernando'  
        })

        assert response1.status_code in [200,302]

        response2 = client.post('/crear_oferta', data={
            'nombre': 'Desarrollador Java SR',
            'fecha_cierre': '2025-06-01',
            'max_candidatos': '20',
            'remuneracion': '100000',
            'beneficio': 'Home Office',
            'estado': 'Activa',
            'usuario_responsable': 'Fernando' 
        })

        assert response2.status_code in [400,409,500]

        oferta_laboral = OfertaLaboral.query.filter_by(nombre= 'Desarrollador Java JR').first()

        OfertaEducacion.query.filter_by(idOfer=oferta_laboral.idOfer).delete()
        OfertaTecnologia.query.filter_by(idOfer=oferta_laboral.idOfer).delete()
        OfertaHabilidad.query.filter_by(idOfer=oferta_laboral.idOfer).delete()
        
        db.session.delete(oferta_laboral)
        db.session.commit()


#Test que verifica que no se cree la oferta con campos vacios ❌Fallando❌
def test_campos_vacios(client):
    with appLocal.app_context():
        with client.session_transaction() as sess:
            sess["username"] = "Fernando"
            sess["type"] = "Admin_RRHH"
        
        response = client.post('/crear_oferta', data={
            'nombre': '',
            'fecha_cierre': '',
            'max_candidatos': '',
            'remuneracion': '',
            'beneficio': '',
            'estado': '',
            'usuario_responsable': '' 
        })

        assert response.status_code in [400,422]

#Test que verifica que se cierre la oferta laboral
def test_validar_ciere_de_oferta(client):
    with appLocal.app_context():
        with client.session_transaction() as sess:
            sess["username"] = "Fernando"
            sess["type"] = "Admin_RRHH"
        
        response = client.post('/crear_oferta', data ={
            'nombre': 'QA Tester Ssr',
            'fecha_cierre': '2026-06-01',
            'max_candidatos': '10',
            'remuneracion': '300000',
            'beneficio': 'Gimnasio',
            'estado': 'Activa',
            'usuario_responsable': 'Fernando' 
        })

        assert response.status_code in [200,302]

        oferta_laboral = OfertaLaboral.query.filter_by(nombre = 'QA Tester Ssr').first()

        assert oferta_laboral is not None

        response = client.post(f'/cerrar_oferta/{oferta_laboral.idOfer}')

        assert response.status_code in [200,302]

        # client.get('/postulantes')
        
        estado_oferta_actualizada = OfertaLaboral.query.filter_by(nombre = 'QA Tester Ssr').first().estado

        assert estado_oferta_actualizada == 'Cerrada'

        OfertaEducacion.query.filter_by(idOfer=oferta_laboral.idOfer).delete()
        OfertaTecnologia.query.filter_by(idOfer=oferta_laboral.idOfer).delete()
        OfertaHabilidad.query.filter_by(idOfer=oferta_laboral.idOfer).delete()
        
        db.session.delete(oferta_laboral)
        db.session.commit()