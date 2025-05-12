import pytest
from FlaskLocal import app as app_local  # Cambiar a una importación relativa
from FlaskCandidatos import app as app_candidatos

# Fixture de pytest que configura un cliente de prueba de Flask
# Se usa para simular solicitudes HTTP en un entorno controlado (modo TESTING)
@pytest.fixture
def client():
    # Configurar el entorno de prueba
    app_local.config['TESTING'] = True # Activa el modo TESTING de Flask
    app_local.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/erp_rrhh.db' # Configura la base de datos para usar SQLite local en lugar de la base real
    with app_local.test_client() as client:  # Crea un cliente de prueba de Flask que permite simular solicitudes como POST, GET, etc.
        yield client  # Devuelve el cliente para que sea usado dentro de los tests

# Test parametrizado que verifica el inicio de sesión exitoso para distintos usuarios válidos
# Envía una solicitud POST con credenciales correctas y espera una redirección (status 302)
@pytest.mark.parametrize(
    "user, passw",
    [
        ('Fernando', 'admin123'),
        ('Diego', 'supervisor123'),
        ('Guada','analista123')
    ]
)
def test_login_valid_credentials_params(client, user, passw):
    # Simulo una solicitud POST con credenciales válidas
    response = client.post('/login', data={'username': user, 'password': passw})
    assert response.status_code == 302  
    assert b"Redirecting" in response.data

# Test parametrizado que verifica intentos de login con credenciales inválidas
# Envía una solicitudPOST con combinaciones incorrectas y espera una respuesta 200 (página recargada sin redirigir)
@pytest.mark.parametrize(
    "user, passw",
    [
        ('Hernesto','admin123'),
        ('Fernando', 'admin321'),
        ('Hernesto','admin321')
    ]
)
def test_login_invalid_credentials_params(client, user, passw):
    # Simulo una solicitud POST con credenciales inválidas
    response = client.post('/login', data={'username': user, 'password': passw})
    assert response.status_code == 200
    # assert b"Credenciales inválidas" in response.data

# Test parametrizado que verifica el comportamiento cuando se envían campos vacíos
# Envía una solicitud POST con combinaciones de usuario y contraseña vacíos
# y espera un código de estado 400 (Bad Request)
@pytest.mark.parametrize(
    "user, passw",
    [
        (None,'admin123'),
        ('Fernando', None),
        (None,None)
    ]
)
def test_login_empty_fields_params(client, user, passw):
    # Simulo una solicitud POST con campos vacios
    response = client.post('/login', data={'username': user, 'password': passw})
    assert response.status_code == 400
    # assert b"Usuario y contrasena no pueden estar vacios" in response.data 

