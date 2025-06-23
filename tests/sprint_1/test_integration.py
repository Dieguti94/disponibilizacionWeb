import pytest
from app import app as app_candidatos,Candidato,OfertaLaboral,db, Postulacion

# Fixture para eliminar candidatos específicos antes de ejecutar los tests
@pytest.fixture(scope="function", autouse=True)
def eliminar_candidatos():
    ids_a_eliminar = [
        'correoDePueba123@gmail.com',
        'correoDePueba4123@gmail.com',
        'tincho462@gmail.com',
        'agusmartinez@hotmail.com'
    ]
    with app_candidatos.app_context():
        for id_candidato in ids_a_eliminar:
            candidato = Candidato.query.filter_by(id=id_candidato).first()
            if candidato:
                db.session.delete(candidato)
        db.session.commit()

@pytest.fixture
def client_Candidatos():
    app_candidatos.config['TESTING'] = True  # Activa el modo TESTING de Flask
    app_candidatos.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/erp_rrhh.db'  # Configura la base de datos para usar SQLite local
    with app_candidatos.test_client() as client_Candidatos:  # Crea un cliente de prueba de Flask
        yield client_Candidatos  # Devuelve el cliente para que sea usado dentro de los tests


@pytest.mark.parametrize(
    "nombre, apellido, email, telefono, provincia, experiencia, educacion, tecnologia1, tecnologia2, habilidad1, habilidad2",
    [
        ('Lucas', 'Abalos', 'correoDePueba123@gmail.com', '1135356456', 'Buenos Aires', '2', 'universitario', 'java', 'sql', 'empatía', 'adaptabilidad'),
        ('Jose', 'Perez', 'correoDePueba4123@gmail.com', '1343567856', 'Buenos Aires', '2', 'secundario', 'python','aws' ,'organizado','adaptabilidad')

    ]
)
def test_valid_agregar_postulacion(client_Candidatos, nombre, apellido, email, telefono, provincia, experiencia, educacion, tecnologia1, tecnologia2, habilidad1, habilidad2):
    with client_Candidatos.session_transaction() as sess:
        sess["username"] = "Fernando"
        sess["type"] = "Admin_RRHH"

    with app_candidatos.app_context():
        oferta = OfertaLaboral.query.filter_by(estado='Activa').first()
        assert oferta is not None

    oferta_id = oferta.idOfer

    response = client_Candidatos.post('/cargarCV', data={
        'nombre': nombre,
        'apellido': apellido,
        'email': email,
        'telefono': telefono,
        'ubicacion': provincia,  
        'experiencia': experiencia,
        'educacion': educacion,
        'idOfer': str(oferta_id),  
        'tecnologias': tecnologia1,    
        'tecnologias2': tecnologia2,   
        'habilidades': habilidad1,     
        'habilidades2': habilidad2     
    }, follow_redirects=True)

    assert response.status_code in [200, 302]

    with app_candidatos.app_context():
        candidato = Candidato.query.filter_by(id=email).first()
        assert candidato is not None

        postulacion = Postulacion.query.filter_by(idCandidato=email, idOfer=oferta_id).first()
        assert postulacion is not None

#🟡A revisar🟡
# Test parametrizado que verifica el intento de agregar postulantes duplicados
@pytest.mark.parametrize(
    "nombre, apellido, email, telefono, ubicacion, experiencia, educacion, tecnologia1,tecnologia2, habilidad1, habilidad2",
     [
         ('Martin', 'Gonzales', 'tincho462@gmail.com','1125432354', 'Buenos Aires', '6','universitario', 'java','css', 'trabajo en equipo','autodidacta'),
         ('Agustin', 'Martinez', 'agusmartinez@hotmail.com','1123432345', 'Formosa', '3' ,'postgrado', 'sql','css', 'liderazgo','autodidacta')
     ]
)
def test_postulantes_duplicados(client_Candidatos ,nombre,apellido,email,telefono,ubicacion,experiencia,educacion,tecnologia1,tecnologia2,habilidad1,habilidad2):
    
    with client_Candidatos.session_transaction() as sess:
        sess["username"] = "Fernando"
        sess["type"] = "Admin_RRHH"
    
    with app_candidatos.app_context():
        oferta = OfertaLaboral.query.filter_by(estado='Activa').first()
        assert oferta is not None

    oferta_id = oferta.idOfer

    data = {
        'nombre': nombre,
        'apellido': apellido,
        'email': email,
        'telefono': telefono,
        'ubicacion': ubicacion,
        'experiencia': experiencia,
        'educacion': educacion,
        'tecnologias': tecnologia1,      
        'tecnologias2': tecnologia2,     
        'habilidades': habilidad1,       
        'habilidades2': habilidad2,      
        'idOfer': str(oferta_id),
    }

    response1 = client_Candidatos.post('/cargarCV', data=data)
    assert response1.status_code in [200,302]

    response2 = client_Candidatos.post('/cargarCV', data=data, follow_redirects=True)
    assert b"Este candidato ya estaba postulado" in response2.data

    with client_Candidatos.application.app_context():
       candidatos = Candidato.query.filter_by(id=email).all()
       assert len(candidatos) == 1

       postulaciones = Postulacion.query.filter_by(idCandidato=email, idOfer=oferta_id).all()
       assert len(postulaciones) == 1

#Test que verifica que no se pueda agregar un candidato a una oferta cerrada ❌Preguntar❌
def test_cargar_candidatos_con_oferta_cerrada(client_Candidatos):
    with client_Candidatos.session_transaction() as sess:
        sess["username"] = "Fernando"
        sess["type"] = "Admin_RRHH"

    email = 'Carlitos@gmail.com'

    with app_candidatos.app_context():
        oferta = OfertaLaboral.query.filter_by(estado='Cerrada').first()
        assert oferta is not None
        oferta_cerrada_id = oferta.idOfer
        Postulacion.query.filter_by(idCandidato=email, idOfer=oferta_cerrada_id).delete()
        db.session.commit()

    response = client_Candidatos.post('/cargarCV', data={
        'nombre': 'Carlos',
        'apellido': 'Rodriguez',
        'email': email,
        'telefono': '1134123423',
        'ubicacion': 'Buenos Aires',
        'experiencia': 5,
        'educacion': 'universitario',
        'tecnologias': 'java',
        'tecnologias2': 'sql',
        'habilidades': 'liderazgo',
        'habilidades2': 'adaptabilidad',
        'idOfer': str(oferta_cerrada_id)
    }, follow_redirects=True)

    assert b"La oferta ya alcanz" in response.data
    assert b"el m" in response.data
    assert b"de postulaciones" in response.data

    with app_candidatos.app_context():
        postulacion = Postulacion.query.filter_by(idCandidato=email, idOfer=oferta_cerrada_id).first()
        assert postulacion is None

#Test que verifica que no se pueda agregar un candidato cuando se supera el limite de candidatos
def test_agregar_postulacion_con_limite_de_candidato_superado(client_Candidatos):
    with client_Candidatos.session_transaction() as sess:
        sess["username"] = "Fernando"
        sess["type"] = "Admin_RRHH"
    
    with app_candidatos.app_context():
        oferta = OfertaLaboral.query.filter_by(estado='Cerrada').first()
        assert oferta is not None

    oferta_cerrada_id = oferta.idOfer
    email = 'JosePerez@gmail.com'

    response = client_Candidatos.post('/cargarCV', data={
        'nombre': 'Jose',
        'apellido': 'Perez',
        'email': email,
        'telefono': '1134123423',
        'ubicacion': 'Buenos Aires',
        'experiencia': 5,
        'educacion': 'universitario',   
        'tecnologias': 'java',
        'tecnologias2': 'sql',          
        'habilidades': 'liderazgo',
        'habilidades2': 'adaptabilidad',
        'idOfer': str(oferta_cerrada_id)
    }, follow_redirects=True)

    assert b"La oferta ya alcanz" in response.data
    assert b"el m" in response.data
    assert b"de postulaciones" in response.data

# Test que verifica que no se cargue el CV cuando no se selecciona una oferta
def test_postulacion_sin_oferta(client_Candidatos):
    with client_Candidatos.session_transaction() as sess:
        sess["username"] = "Fernando"
        sess["type"] = "Admin_RRHH"

    response = client_Candidatos.post('/cargarCV', data={
        'nombre': 'Juan',
        'apellido': 'Gonzalez',
        'email': 'juanGonzalez@gmail.com',
        'telefono': '1134123456',
        'ubicacion': 'Buenos Aires',
        'experiencia': 3,
        'educacion': 'universitario',
        'tecnologias': 'java',
        'tecnologias2': 'sql',
        'habilidades': 'liderazgo',
        'habilidades2': 'adaptabilidad'
    }, follow_redirects=True)

    assert b"Debes seleccionar una oferta laboral" in response.data