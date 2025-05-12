import pandas as pd
import random

# Lista de jugadores y cuerpo técnico de Boca Juniors

# Cargar el CSV inicial
data = pd.read_csv("candidatos.csv")

# Cambiar nombres y apellidos
#data["Nombre"] = [random.choice(nombres_boca) for _ in range(len(data))]
#data["Apellido"] = [random.choice(apellidos_boca) for _ in range(len(data))]

# Aumentar a 120 candidatos replicando y aleatorizando
#while len(data) < 120:
#    data = pd.concat([data, data.sample(frac=1).reset_index(drop=True)], ignore_index=True)
#data = data.sample(n=120).reset_index(drop=True)

# Cambiar la columna "Habilidades" a "Tecnologías"
#data.rename(columns={"Habilidades": "Tecnologías"}, inplace=True)

# Agregar columna "Habilidades" (habilidades blandas)
#data["Habilidades"] = [random.choice(habilidades_blandas) for _ in range(len(data))]

# Función para determinar si son "Aptos"
def definir_apto(row):
    experiencia = row["Experiencia"]
    tecnologia = row["Tecnologías"]
    educacion = row["Educacion"]
    habilidades = row["Habilidades"]
    
    if tecnologia == "Python" and experiencia > 5:
        return "Apto"
    elif tecnologia != "Python" and experiencia > 7:
        return "Apto"
    elif habilidades == "Trabajo en equipo" and educacion in ["Postgrado", "Universitario"] and tecnologia == "Python" and experiencia > 3:
        return "Apto"
    elif habilidades != "Trabajo en equipo"  and tecnologia != "Python":
        return "No Apto"
    elif tecnologia != "Python" and experiencia < 7:
        return "No Apto"
    else:
        return "No Apto"

# Actualizar columna "Apto"
data["Apto"] = data.apply(definir_apto, axis=1)

# Guardar el nuevo CSV
data.to_csv("candidatos2.csv", index=False)
print("¡Archivo modificado y guardado como 'nuevo_archivo.csv'!")