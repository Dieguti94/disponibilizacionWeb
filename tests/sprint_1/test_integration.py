from typing import Literal
from flask.testing import FlaskClient
import pytest
from app import app as app_candidatos,Candidato,db

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

#🟡A revisar🟡
# Test parametrizado que verifica intentos de agregar postulantes validos
# Envía una solicitud POST con datos válidos y espera una respuesta 200 o 302
# Luego verifica que el postulante fue correctamente guardado en la base de datos
@pytest.mark.parametrize(
    "nombre, apellido, email, telefono, ubicacion, experiencia, educacion, tecnologias, habilidades",
    [
        ('Lucas', 'Abalos', 'correoDePueba123@gmail.com', '1135356456', 'Buenos Aires', '2', 'Secundario', 'Python', 'Trabajo en equipo'),
        ('Jose', 'Perez', 'correoDePueba4123@gmail.com', '1343567856', 'Buenos Aires', '2', 'Secundario', 'Python', 'Trabajo en equipo'),
    ]
)
def test_valid_agregar_postulacion(client_Candidatos: FlaskClient, nombre: Literal['Lucas'] | Literal['Jose'], apellido: Literal['Abalos'] | Literal['Perez'], email: Literal['correoDePueba123@gmail.com'] | Literal['correoDePueba4123@gmail.com'], telefono: Literal['1135356456'] | Literal['1343567856'], ubicacion: Literal['Buenos Aires'], experiencia: Literal['2'], educacion: Literal['Secundario'], tecnologias: Literal['Python'], habilidades: Literal['Trabajo en equipo']):
    client_Candidatos.get('/postulacionIT')
    response = client_Candidatos.post('/postulacion', data={
        'nombre': nombre,
        'apellido': apellido,
        'email': email, 
        'telefono': telefono,
        'ubicacion': ubicacion, 
        'experiencia': experiencia, 
        'educacion': educacion,  
        'tecnologias': tecnologias,        
        'habilidades': habilidades,
        'puntaje': 0
    })
    assert response.status_code in [200, 302]

    # Verificar que el postulante fue ingresado en la base de datos
    with client_Candidatos.application.app_context():
        candidato = Candidato.query.filter_by(id=email).first()
        assert candidato is not None
        #Se puede explayar mas

#🟡A revisar🟡
# Test parametrizado que verifica el intento de agregar postulantes duplicados
# Envía una solicitud POST con datos válidos dos veces seguidas
# Espera que la primera solicitud se procese correctamente (200 o 302)
# La segunda debería fallar con un código de error (500) por ser duplicado
# Luego verifica que el postulante no fue duplicado en la base de datos
@pytest.mark.parametrize(
     "nombre, apellido, email, telefono, ubicacion, experiencia, educacion, tecnologias, habilidades",
     [
         ('Martin', 'Gonzales', 'tincho462@gmail.com','1125432354', 'Buenos Aires', '6','Universitario', 'Java', 'Trabajo en equipo'),
         ('Agustin', 'Martinez', 'agusmartinez@hotmail.com','1123432345', 'Formosa', '3' ,'Postgrado', 'SQL', 'Liderazgo')
     ]
)
def test_postulantes_duplicados(client_Candidatos: FlaskClient,nombre: Literal['Martin'] | Literal['Agustin'], apellido: Literal['Gonzales'] | Literal['Martinez'], email: Literal['tincho462@gmail.com'] | Literal['agusmartinez@hotmail.com'], telefono: Literal['1125432354'] | Literal['1123432345'], ubicacion: Literal['Buenos Aires'] | Literal['Formosa'], experiencia: Literal['6'] | Literal['3'], educacion: Literal['Universitario'] | Literal['Postgrado'], tecnologias: Literal['Java'] | Literal['SQL'], habilidades: Literal['Trabajo en equipo'] | Literal['Liderazgo']):
    client_Candidatos.get('/postulacionIT')

    data = {
        'nombre': nombre,
        'apellido': apellido,
        'email': email, 
        'telefono': telefono,
        'ubicacion': ubicacion,
        'experiencia': experiencia, 
        'educacion': educacion,  
        'tecnologias': tecnologias,        
        'habilidades': habilidades,
        'puntaje': 0
    }

    response1 = client_Candidatos.post('/postulacion', data=data)
    assert response1.status_code in [200,302]

    response2 = client_Candidatos.post('/postulacion', data=data)
    assert response2.status_code == 500

    with client_Candidatos.application.app_context():
       candidato = Candidato.query.filter_by(id=email).all()
       assert len(candidato) == 1


#test que evalua que si se pasa un campo inexistente en educacion, habilidad y tecnologia
@pytest.mark.parametrize(
    "nombre, apellido, email, telefono, ubicacion, experiencia, educacion, tecnologias, habilidades",
    [
        ("Pepe", "Argento", "pepeargento1903@hotmail.com", "1535674323", "Buenos Aires", "7", "Primario","Java","Empatia"),
        ("Pepe", "Argento", "pepeargento1903@hotmail.com", "1535674323", "Buenos Aires", "7", "Postgrado","Assembler","Empatia"),
        ("Pepe", "Argento", "pepeargento1903@hotmail.com", "1535674323", "Buenos Aires", "7", "Postgrado","Java","Vender zapatos")
    ]

)
def test_campos_inexistentes(client_Candidatos: FlaskClient,nombre: Literal['Pepe'], apellido: Literal['Argento'], email: Literal['pepeargento1903@hotmail.com'], telefono: Literal['1535674323'], ubicacion: Literal['Buenos Aires'], experiencia: Literal['7'], educacion: Literal['Primario'] | Literal['Postgrado'], tecnologias: Literal['Java'] | Literal['Assembler'], habilidades: Literal['Empatia'] | Literal['Vender zapatos']):
    response = client_Candidatos.post('/postulacion', data = {
        'nombre': nombre,
        'apellido': apellido,
        'email': email, 
        'telefono': telefono,
        'ubicacion': ubicacion,
        'experiencia': experiencia, 
        'educacion': educacion,  
        'tecnologias': tecnologias,        
        'habilidades': habilidades,
        'puntaje': 0
    })

    assert response.status_code == 400
