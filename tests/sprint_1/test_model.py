import pytest
import joblib
import pandas as pd
from app import app as appLocal

@pytest.fixture
def client():
    appLocal.config['TESTING'] = True
    appLocal.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/erp_rrhh.db'
    with appLocal.test_client() as cliente:
        yield cliente

def loadModel():
    modelo_path = "modelo_candidatos.pkl"

    try:
        modelo = joblib.load(modelo_path)
        return modelo
    except FileNotFoundError:
        pytest.fail(f"No se encontro el arhivo del modelo")

#Test que verifica que un candidato es apto
def test_model_prediction_apto():
    modelo = loadModel()

    columnas = ["Educacion", "Tecnologías", "Tecnologías2", "Habilidades", "Habilidades2"]
    datos_prueba = pd.DataFrame([[0, 0, 0, 0, 0]], columns=columnas)

    try:
        prediccion = modelo.predict(datos_prueba)
    except Exception as e:
        pytest.fail(f"El modelo falló al realizar la predicción: {e}")

    assert prediccion[0] == 1

#Test que verifica que un candidato es no apto
def test_model_prediction_no_apto():
    modelo = loadModel()

    columnas = ["Educacion", "Tecnologías", "Tecnologías2", "Habilidades", "Habilidades2"]
    datos_prueba = pd.DataFrame([[2, 3, 1, 1, 2]], columns=columnas)

    try:
        prediccion = modelo.predict(datos_prueba)
    except Exception as e:
        pytest.fail(f"El modelo falló al realizar la predicción: {e}")

    assert prediccion[0] == 0
