import pytest
from app import app as app_local 

# Fixture de pytest que configura un cliente de prueba de Flask
@pytest.fixture
def client():
    app_local.config['TESTING'] = True 
    app_local.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/erp_rrhh.db' 
    with app_local.test_client() as client:  
        yield client 

# Test parametrizado que verifica el inicio de sesión exitoso para distintos usuarios válidos
@pytest.mark.parametrize(
    "user, passw",
    [
        ('Fernando', 'admin123'),
        ('Diego', 'supervisor123'),
        ('Guada','analista123')
    ]
)
def test_login_valid_credentials_params(client, user, passw):
    response = client.post('/login', data={'username': user, 'password': passw})
    assert response.status_code == 302  
    assert b"Redirecting" in response.data

# Test parametrizado que verifica intentos de login con credenciales inválidas
@pytest.mark.parametrize(
    "user, passw",
    [
        ('Hernesto','admin123'),
        ('Fernando', 'admin321'),
        ('Hernesto','admin321')
    ]
)
def test_login_invalid_credentials_params(client, user, passw):
   response = client.post('/login', data={'username': user, 'password': passw}, follow_redirects=True)
   assert b"Usuario no existente" in response.data or b"incorrecta" in response.data or b"Credenciales inv" in response.data 

# Test parametrizado que verifica el comportamiento cuando se envían campos vacíos
@pytest.mark.parametrize(
    "user, passw",
    [
        (None,'admin123'),
        ('Fernando', None),
        (None,None)
    ]
)
def test_login_empty_fields_params(client, user, passw):
    response = client.post('/login', data={'username': user, 'password': passw})
    assert response.status_code == 400
    # assert b"Credenciales inv" in response.data 

#Test que verifica el correcto funcionamiento del logout
def test_logout_session(client):
    with client.session_transaction() as sess:
        sess["username"] = "Fernando"
        sess["type"] = "Admin_RRHH"

    response = client.get('/logout', follow_redirects=True)
    assert b"login" in response.data
    with client.session_transaction() as sess:
        assert "username" not in sess
        assert "type" not in sess

#Test parametrizado que verifica que no se pueda ingresar a las rutas protegidas
@pytest.mark.parametrize(
    "ruta",
    [
        "/admin_rrhh",
        "/crear_usuario",
        "/gestionar_usuarios",
        "/cambiar_password",
        "/ver_ofertas",
        "/estadisticas",
        "/predecir",
        "/postulantes",
        "/metricas",
    ]
)
def test_protected_routes_require_login(client, ruta):
    response = client.get(ruta, follow_redirects=True)
    assert b"login" in response.data.lower()