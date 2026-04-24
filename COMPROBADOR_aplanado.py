import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVOS_DIR = os.path.join(BASE_DIR, 'Archivos')

# Cargar los archivos CSV
df1 = pd.read_csv('1_LONGShuffled.csv')
df2 = pd.read_csv(os.path.join(ARCHIVOS_DIR, 'ApXRP.csv'))

# Eliminar la columna "Clase" del primer DataFrame
if 'Clase' in df1.columns:
    df1 = df1.drop('Clase', axis=1)

# Verificar si las columnas son idénticas
if df1.columns.tolist() == df2.columns.tolist():
    print("Las columnas de ambos archivos son idénticas.")
    
    # Convertir la única fila del segundo DataFrame en una lista
    fila_a_buscar = df2.iloc[0].tolist()  # Cambiar a 0 si el archivo 2 tiene solo una fila

    # Iterar sobre las filas del primer DataFrame y comparar con la fila a buscar
    encontrado = False
    for index, row in df1.iterrows():
        if row.tolist() == fila_a_buscar:
            encontrado = True
            print(f"La fila del archivo 2 se encuentra en el archivo 1, en la fila {index}.")
            break

    if not encontrado:
        print("La fila del archivo 2 no se encuentra en el archivo 1.")
else:
    print("Las columnas de los archivos no son idénticas.")