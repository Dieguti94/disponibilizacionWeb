import pytest
from FlaskLocal import Candidato,db
from FlaskCandidatos import app as app_candidatos

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
def test_valid_agregar_postulacion(client_Candidatos, nombre, apellido, email, telefono, ubicacion, experiencia, educacion, tecnologias, habilidades):
    response = client_Candidatos.post('/postulacion', data={
        'nombre': nombre,
        'apellido': apellido,
        'email': email, 
        'telefono': telefono,
        'ubicacion': ubicacion, 
        'experiencia': experiencia, 
        'educacion': educacion,  
        'tecnologias': tecnologias,        
        'habilidades': habilidades    
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
def test_postulantes_duplicados(client_Candidatos,nombre, apellido, email, telefono, ubicacion, experiencia, educacion, tecnologias, habilidades):
    data = {
        'nombre': nombre,
        'apellido': apellido,
        'email': email, 
        'telefono': telefono,
        'ubicacion': ubicacion,
        'experiencia': experiencia, 
        'educacion': educacion,  
        'tecnologias': tecnologias,        
        'habilidades': habilidades
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
def test_campos_inexistentes(client_Candidatos,nombre, apellido, email, telefono, ubicacion, experiencia, educacion, tecnologias, habilidades):
    response = client_Candidatos.post('/postulacion', data = {
        'nombre': nombre,
        'apellido': apellido,
        'email': email, 
        'telefono': telefono,
        'ubicacion': ubicacion,
        'experiencia': experiencia, 
        'educacion': educacion,  
        'tecnologias': tecnologias,        
        'habilidades': habilidades
    })

    assert response.status_code == 400




# # ❓Consultar este test❓
# @pytest.mark.parametrize(
#      "nombre, apellido, email, telefono, ubicacion, experiencia, educacion, tecnologias, habilidades",
#      [
#          ("","","","","","","","",""),
#          ("","Garcia","DanielaGar@gmail.com","1123321212","Chaco","3","Postgrado","C++","Liderazgo"),
#          ("Daniela","","DanielaGar@gmail.com","1123321212","Chaco","3","Postgrado","C++","Liderazgo"),
#          ("Daniela","Garcia","","1123321212","Chaco","3","Postgrado","C++","Liderazgo"),
#          ("Daniela","Garcia","DanielaGar@gmail.com","","Chaco","3","Postgrado","C++","Liderazgo"),
#          ("Daniela","Garcia","DanielaGar@gmail.com","1123321212","","3","Postgrado","C++","Liderazgo"),
#          ("Daniela","Garcia","DanielaGar@gmail.com","1123321212","Chaco","","Postgrado","C++","Liderazgo"),
#          ("Daniela","Garcia","DanielaGar@gmail.com","1123321212","Chaco","3","","C++","Liderazgo"),
#          ("Daniela","Garcia","DanielaGar@gmail.com","1123321212","Chaco","3","Postgrado","","Liderazgo"),
#          ("Daniela","Garcia","DanielaGar@gmail.com","1123321212","Chaco","3","Postgrado","C++","")
#      ]
# )
# def test_caracteres_vacios(client_Candidatos,nombre, apellido, email, telefono, ubicacion, experiencia, educacion, tecnologias, habilidades):
#     response = client_Candidatos.post('/postulacion', data = {
#         'nombre': nombre,
#         'apellido': apellido,
#         'email': email, 
#         'telefono': telefono,
#         'ubicacion': ubicacion,
#         'experiencia': experiencia, 
#         'educacion': educacion,  
#         'tecnologias': tecnologias,        
#         'habilidades': habilidades
#     })

#     assert response.status_code == 400

#Sprint 1
#test de integracion: 
# postulacion de lado a lado (funcione, repetidos(id), casos invalidos) (✅,✅)
# validar que el candidato agregado este en la base de datos ✅
# para despues ver lo del modelo de prediccion ✅
# #testear que el mail no este repetido ✅
 

#Sprint 2
# etiquetas cargadas en base de datos
# testear algoritmo de ranking
# Validacion de emails


# ❌Problema: hay que borrar de forma manual la base de datos cada vez que se testea❌
