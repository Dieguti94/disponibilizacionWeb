import joblib
import pytest
import pandas as pd

def loadModel():
    modelo_path = "modelo_candidatos.pkl"

    try:
        modelo = joblib.load(modelo_path)
        return modelo
    except FileNotFoundError:
        pytest.fail(f"No se encontro el arhivo del modelo")

def test_model_prediction_apto():
    # Se carga el modelo
    modelo = loadModel()

    # Se crean los datos de prueba
    columnas = ["Experiencia", "Educacion", "Tecnologías", "Habilidades"] 
    datos_prueba = pd.DataFrame([[10, 2, 3, 1]], columns=columnas)

    # Se realiza la predicción
    try:
        prediccion = modelo.predict(datos_prueba)
    except Exception as e:
        pytest.fail(f"El modelo falló al realizar la predicción: {e}")

    assert prediccion[0] == 1


def test_model_prediction_no_apto():
    # Se carga el modelo
    modelo = loadModel()

    # Se crean los datos de prueba
    columnas = ["Experiencia", "Educacion", "Tecnologías", "Habilidades"]  # Asegúrate de que coincidan con las esperadas
    datos_prueba = pd.DataFrame([[1, 0, 0, 0]], columns=columnas)

    # Se realiza la predicción
    try:
        prediccion = modelo.predict(datos_prueba)
    except Exception as e:
        pytest.fail(f"El modelo falló al realizar la predicción: {e}")

    assert prediccion[0] == 0