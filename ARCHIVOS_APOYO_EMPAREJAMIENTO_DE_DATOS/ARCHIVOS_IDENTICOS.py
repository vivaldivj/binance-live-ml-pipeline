import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..'))
ARCHIVOS_DIR = os.path.join(PROJECT_ROOT, 'Archivos')

def comparar_csv(archivo1, archivo2):
    try:
        # Leer ambos archivos CSV
        df1 = pd.read_csv(archivo1)
        df2 = pd.read_csv(archivo2)

        # Verificar si tienen las mismas columnas (sin importar el orden)
        if set(df1.columns) != set(df2.columns):
            return "Los archivos tienen columnas diferentes."

        # Ordenar las columnas por nombre para ignorar el orden original
        df1 = df1[sorted(df1.columns)]
        df2 = df2[sorted(df2.columns)]

        # Ordenar las filas por todas las columnas para ignorar el orden de las filas
        df1 = df1.sort_values(by=sorted(df1.columns)).reset_index(drop=True)
        df2 = df2.sort_values(by=sorted(df2.columns)).reset_index(drop=True)

        # Verificar si los datos son idénticos
        if df1.equals(df2):
            return "*Los archivos CSV tienen la misma información interna* :)"
        else:
            return "Los archivos CSV tienen diferencias en los datos."

    except Exception as e:
        return f"Error al comparar los archivos: {e}"

# Rutas de los archivos CSV a comparar
archivo1 = os.path.join(ARCHIVOS_DIR, 'ApBTC.csv')
archivo2 = "1_SHORTShuffled.csv"

# Resultado de la comparación
resultado = comparar_csv(archivo1, archivo2)
print(resultado)