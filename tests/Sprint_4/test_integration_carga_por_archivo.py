import io
import pytest
from app import app as appLocal, db

@pytest.fixture
def client():
    appLocal.config['TESTING'] = True
    appLocal.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/erp_rrhh.db'
    with appLocal.test_client() as cliente:
        yield cliente

#Test que valida que el sistema acepte y cargue archivos pdf y docx
def test_validar_carga_de_archivo(client):
    with client.session_transaction() as sess:
        sess["username"] = "Fernando"
        sess["type"] = "Admin_RRHH"

    
    pdf_data = io.BytesIO(b"%PDF-1.4 test pdf content")
    pdf_data.name = "Test.pdf"
    response_pdf = client.post("/cargarCV",
        data={"cv_pdf": (pdf_data, "test.pdf")},
        content_type="multipart/form-data",
        follow_redirects=True
    )

    assert response_pdf.status_code == 200

    docx_data = io.BytesIO(b"PK\x03\x04 test docx content")
    docx_data.name = "Test.docx"
    response_docx = client.post("/cargarCV",
        data={"cv_pdf": (docx_data, "test.docx")},
        content_type="multipart/form-data",
        follow_redirects=True
    )

    assert response_docx.status_code == 200

#Test que valida la extracion correcta de datos de archivos pdf
def test_extraccion_datos_clave_pdf(client):
    with client.session_transaction() as sess:
        sess["username"] = "Fernando"
        sess["type"] = "Admin_RRHH"

    with open("tests/Sprint_4/Files/Lucas_abalos_cv.pdf", "rb") as f:
        pdf_data = io.BytesIO(f.read())
        pdf_data.name = "cv_test.pdf"
        response = client.post(
            "/cargarCV",
            data={"cv_pdf": (pdf_data, "cv_test.pdf")},
            content_type="multipart/form-data",
            follow_redirects=True
        )

    assert response.status_code == 200
    assert b"Lucas Gabriel Abalos" in response.data
    assert b"541164835671" in response.data
    assert b"Buenos Aires" in response.data
    assert b"lukotas100@gmail.com" in response.data
    assert b"java" in response.data or b"adaptabilidad" in response.data or b"Universitario" in response.data


#Test que valida que el sistema no acepte archivos invalidos
def test_validar_archivos_invalidos(client):
    with client.session_transaction() as sess:
        sess["username"] = "Fernando"
        sess["type"] = "Admin_RRHH"

    with open("tests/Sprint_4/Files/CV_dañado.pdf", "rb") as f:
        pdf_data = io.BytesIO(f.read())
        pdf_data.name = "cv_test.pdf"
        response = client.post(
            "/cargarCV",
            data={"cv_pdf": (pdf_data, "cv_test.pdf")},
            content_type="multipart/form-data",
            follow_redirects=True
        )

    assert b"El archivo no es un PDF" in response.data

#Test que valida que el sistema no acepte archivos mayores a 5 MB
def test_validar_limite_de_tamaño(client):
    with client.session_transaction() as sess:
        sess["username"] = "Fernando"
        sess["type"] = "Admin_RRHH"

    with open("tests/Sprint_4/Files/Archivo_pesado.pdf", "rb") as f:
        pdf_data = io.BytesIO(f.read())
        pdf_data.name = "cv_test.pdf"
        response = client.post(
            "/cargarCV",
            data={"cv_pdf": (pdf_data, "cv_test.pdf")},
            content_type="multipart/form-data",
            follow_redirects=True
        )

        assert b"El archivo excede" in response.data and b"El archivo excede" in response.data

#Test que valida que el sistema no acepte extensiones invalidas 
def test_validar_extension_invalida(client):
    with client.session_transaction() as sess:
        sess["username"] = "Fernando"
        sess["type"] = "Admin_RRHH"

    exe_data = io.BytesIO(b"Fake EXE content")
    exe_data.name = "malware.exe"
    response = client.post(
        "/cargarCV",
        data={"cv_pdf": (exe_data, "malware.exe")},
        content_type="multipart/form-data",
        follow_redirects=True
    )

    assert b"El archivo no es un PDF" in response.data or b"Debes seleccionar un archivo PDF" in response.data