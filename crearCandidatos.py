import pandas as pd
import random

# Ruta del archivo original
archivo_csv = "candidatos.csv"

# Leer el CSV original
df = pd.read_csv(archivo_csv)

# Provincias de Argentina
provincias = [
    "Buenos Aires", "Córdoba", "Santa Fe", "Mendoza", "Tucumán",
    "Salta", "Entre Ríos", "Chaco", "Corrientes", "Santiago del Estero",
    "Misiones", "San Juan", "Jujuy", "Río Negro", "Neuquén",
    "Formosa", "Chubut", "San Luis", "Catamarca", "La Rioja",
    "La Pampa", "Santa Cruz", "Tierra del Fuego"
]

# Funciones para generar los datos
def generar_email(nombre, apellido):
    numero = random.randint(1, 100)
    email = f"{nombre.lower()}.{apellido.lower()}{numero}@gmail.com"
    return email

def generar_telefono():
    numero = '11' + ''.join([str(random.randint(0, 9)) for _ in range(8)])
    return numero

def generar_ubicacion():
    return random.choice(provincias)

# Crear las nuevas columnas
df['Email'] = df.apply(lambda row: generar_email(row['Nombre'], row['Apellido']), axis=1)
df['Teléfono'] = df.apply(lambda _: generar_telefono(), axis=1)
df['Ubicación'] = df.apply(lambda _: generar_ubicacion(), axis=1)

# Reordenar columnas según lo solicitado
orden_columnas = [
    'Nombre', 'Apellido', 'Email', 'Teléfono', 'Ubicación',
    'Experiencia', 'Educacion', 'Tecnologías', 'Habilidades', 'Apto'
]
df = df[orden_columnas]

# Guardar el archivo actualizado
df.to_csv("candidatos_actualizado.csv", index=False)

print("Archivo actualizado y guardado como 'candidatos_actualizado.csv'")