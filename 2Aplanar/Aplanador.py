##################################################################################################################################
#                                                                     A P L A N A D O R                                          #
##################################################################################################################################
import pandas as pd
import numpy as np
from multiprocessing import Pool
from datetime import datetime
import pandas as pd
from sklearn.utils import shuffle
import sys
from multiprocessing import Pool, cpu_count
import subprocess
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..'))
ARCHIVOS_DIR = os.path.join(PROJECT_ROOT, 'Archivos')


# Función principal que se ejecuta al correr el script
def aplanar(moneda_seleccionada, evento_entrada):
    # Paso 1: Leer el archivo CSV
    file_path1 = os.path.join(ARCHIVOS_DIR, f"{moneda_seleccionada}Data.csv")
    df1 = pd.read_csv(file_path1)
    file_path2 = os.path.join(ARCHIVOS_DIR, f"{moneda_seleccionada}Data_Large.csv")
    df2 = pd.read_csv(file_path2)    

    print(f"Ambos ARCHIVOS de {moneda_seleccionada} leídos con éxito")

    # Paso 2: Inicializar variables
    num_operations = len(df1) // 30  # Número total de operaciones
    num_features1 = len(df1.columns)  # Número de características del primer archivo
    num_features2 = len(df2.columns)  # Número de características del segundo archivo



    # Crear un pool de procesos para procesamiento en paralelo
    with Pool(processes=cpu_count()) as pool:
        # Ejecutar la función de procesamiento en paralelo para cada operación
        resultados = pool.starmap(
            procesar_operacion,
            [(i, df1, df2, num_features1, num_features2) for i in range(num_operations)]
        )

    # Convertir la lista de resultados a un DataFrame
    new_columns = [f"Feature_{i}" for i in range(1, (num_features1 + num_features2) * 30 + 1)]
    new_df = pd.DataFrame(resultados, columns=new_columns)



    # Guardar el nuevo DataFrame en un archivo CSV
    new_csv_path = os.path.join(ARCHIVOS_DIR, f"Ap{moneda_seleccionada}.csv")
    new_df.to_csv(new_csv_path, index=False, header=True)


    # Eliminar el archivo CSV original (OPCIONAL)
    #os.remove(f"Archivos/{moneda_seleccionada}Data.csv")
    #os.remove(f"Archivos/{moneda_seleccionada}Data_Large.csv")

    
# Función para procesar y aplanar los datos de una operación
def procesar_operacion(i, df1, df2, num_features1, num_features2):
    start_idx = i * 30
    end_idx = start_idx + 30

    # Aplanar los datos de los dos ARCHIVOS usando numpy
    operation_data1 = df1.iloc[start_idx:end_idx].values.flatten()  # Datos del primer archivo
    operation_data2 = df2.iloc[start_idx:end_idx].values.flatten()  # Datos del segundo archivo

    # Concatenar y agregar la etiqueta de clase
    combined_operation_data = np.concatenate([operation_data1, operation_data2])
    return combined_operation_data



#                                                           --------                                                #
def analizar_data(moneda_seleccionada, tipo_patron):
    # Ejecución de script 3 para cargar el modelo en base al evento de entrada identificado en el evento 1: Se usará el codigo enviado en script 1 para ver cual url abre para cargar modelo
    
    if (tipo_patron == 0) or (tipo_patron == 2) or (tipo_patron == 4) or (tipo_patron == 7):
        ruta_script3 = os.path.join(PROJECT_ROOT, '3CargarModelo', 'Buy', 'CargarModelox.py')
    elif (tipo_patron == 1) or (tipo_patron == 3) or (tipo_patron == 5) or (tipo_patron == 8):
        ruta_script3 = os.path.join(PROJECT_ROOT, '3CargarModelo', 'Sell', 'CargarModelox.py')     
                       
    try:
        # Ejecutar script 3
        proc_script3 = subprocess.Popen([sys.executable, ruta_script3, moneda_seleccionada, str(tipo_patron)])
        # Esperar a que el script 3 termine
        proc_script3.wait()  
        if proc_script3.returncode == 0:
            sys.exit(0)
        elif proc_script3.returncode == 1:
            sys.exit(1)  
        elif proc_script3.returncode == 3:
            sys.exit(3)                
    except FileNotFoundError:
        print("El archivo correspondiente a la moneda seleccionada no se encontró.")




if __name__ == "__main__":


   # moneda_seleccionada = 'ETH'

    # Captura los argumentos
    moneda_seleccionada = sys.argv[1]
    evento_entrada = sys.argv[2]
    evento_entrada = int(evento_entrada)

    """moneda_seleccionada = 'XRP'
    evento_entrada = 5"""


    # "evento_entrada" nos dice el archivo pivote bin que se necesita abrir para transformar nuestros datos.

    aplanar(moneda_seleccionada, evento_entrada)
    analizar_data(moneda_seleccionada, evento_entrada)