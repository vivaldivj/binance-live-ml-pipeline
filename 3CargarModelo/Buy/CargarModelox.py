##################################################################################################################################
#                                                               C A R G A R   M O D E L O                                        #
##################################################################################################################################

import pandas as pd
import os
from sklearn.model_selection import train_test_split
from joblib import load
import tkinter as tk
from tkinter import messagebox
import subprocess
import time
import sys
from datetime import datetime
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException
import joblib

# ✅ BASE DIR (CLAVE)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..', '..'))
ARCHIVOS_DIR = os.path.join(PROJECT_ROOT, 'Archivos')
OPERACIONES_DIR = os.path.join(PROJECT_ROOT, '4AbrirOperaciones')



def CARGARMODELO(moneda_seleccionada, evento_codigo): 

    # ✅ Ruta corregida
    ruta_csv = os.path.join(ARCHIVOS_DIR, f"Ap{moneda_seleccionada}.csv")
    data = pd.read_csv(ruta_csv)

    data = data.round(5)

    resultado = cargarmodelo(moneda_seleccionada, data, evento_codigo)

    if resultado == 0:  
        print("")
        print("*                 * ¡¡¡ LONG confirmado. Abriendo operación !!! *                    *")        
        print("")
        eliminar_ordenes_stop_loss(moneda_seleccionada)

        ruta_script4 = os.path.join(OPERACIONES_DIR, 'LONG', 'Abrir_longx_hedge.py')

        try:
            result_script4 = subprocess.Popen([sys.executable, ruta_script4, moneda_seleccionada])
            result_script4.wait()

            if result_script4.returncode == 0:
                sys.exit(0)
            elif result_script4.returncode == 1:
                sys.exit(1)
            elif result_script4.returncode == 3:
                print("NO SE CONCRETÓ LA ENTRADA")
                sys.exit(3)
            elif result_script4.returncode == 4:
                print("Entrada cancelada. Ya había una operación abierta")
                sys.exit(0)

        except FileNotFoundError:
            print("No se encontró el script de ejecución.")
            sys.exit(1)  

    else:
        print("*** No entres ***")
        sys.exit(0)


##################################################################################################################################
# MODELOS
##################################################################################################################################

def cargarmodelo(moneda_seleccionada, data, evento_codigo):

    # 📁 Carpeta base de modelos
    MODELOS_DIR = os.path.join(BASE_DIR, '..', 'Modelos')

    if evento_codigo == 0:
        scaler = joblib.load(os.path.join(MODELOS_DIR, moneda_seleccionada, 'scalerLONG_180.pkl'))
        pca = joblib.load(os.path.join(MODELOS_DIR, moneda_seleccionada, 'pcaLONG_180.pkl'))
        rf_model = joblib.load(os.path.join(MODELOS_DIR, moneda_seleccionada, 'random_forest_long_180.pkl'))

    elif evento_codigo == 1:
        scaler = joblib.load(os.path.join(MODELOS_DIR, moneda_seleccionada, 'scalerSHORT_180.pkl'))
        pca = joblib.load(os.path.join(MODELOS_DIR, moneda_seleccionada, 'pcaSHORT_180.pkl'))
        rf_model = joblib.load(os.path.join(MODELOS_DIR, moneda_seleccionada, 'random_forest_SHORT_180.pkl'))

    elif evento_codigo == 2:
        scaler = joblib.load(os.path.join(MODELOS_DIR, moneda_seleccionada, 'scalerLONG_RSI50.pkl'))
        pca = joblib.load(os.path.join(MODELOS_DIR, moneda_seleccionada, 'pcaLONG_RSI50.pkl'))
        rf_model = joblib.load(os.path.join(MODELOS_DIR, moneda_seleccionada, 'random_forest_long_RSI50.pkl'))

    elif evento_codigo == 3:
        scaler = joblib.load(os.path.join(MODELOS_DIR, moneda_seleccionada, 'scalerSHORT_RSI50.pkl'))
        pca = joblib.load(os.path.join(MODELOS_DIR, moneda_seleccionada, 'pcaSHORT_RSI50.pkl'))
        rf_model = joblib.load(os.path.join(MODELOS_DIR, moneda_seleccionada, 'random_forest_SHORT_RSI50.pkl'))

    elif evento_codigo == 4:
        scaler = joblib.load(os.path.join(MODELOS_DIR, moneda_seleccionada, 'scalerLONG_HAMMER.pkl'))
        pca = joblib.load(os.path.join(MODELOS_DIR, moneda_seleccionada, 'pcaLONG_HAMMER.pkl'))
        rf_model = joblib.load(os.path.join(MODELOS_DIR, moneda_seleccionada, 'random_forest_long_HAMMER.pkl'))

    elif evento_codigo == 5:
        scaler = joblib.load(os.path.join(MODELOS_DIR, moneda_seleccionada, 'scalerSHORT_HAMMER.pkl'))
        pca = joblib.load(os.path.join(MODELOS_DIR, moneda_seleccionada, 'pcaSHORT_HAMMER.pkl'))
        rf_model = joblib.load(os.path.join(MODELOS_DIR, moneda_seleccionada, 'random_forest_SHORT_HAMMER.pkl'))

    elif evento_codigo == 7:
        scaler = joblib.load(os.path.join(MODELOS_DIR, moneda_seleccionada, 'scalerLONG_DV.pkl'))
        pca = joblib.load(os.path.join(MODELOS_DIR, moneda_seleccionada, 'pcaLONG_DV.pkl'))
        rf_model = joblib.load(os.path.join(MODELOS_DIR, moneda_seleccionada, 'random_forest_long_DV.pkl'))

    elif evento_codigo == 8:
        scaler = joblib.load(os.path.join(MODELOS_DIR, moneda_seleccionada, 'scalerSHORT_DV.pkl'))
        pca = joblib.load(os.path.join(MODELOS_DIR, moneda_seleccionada, 'pcaSHORT_DV.pkl'))
        rf_model = joblib.load(os.path.join(MODELOS_DIR, moneda_seleccionada, 'random_forest_SHORT_DV.pkl'))

    else:
        raise ValueError("Código de evento no válido")

    data_nuevo_scaled = scaler.transform(data)
    data_nuevo_pca = pca.transform(data_nuevo_scaled)

    y_proba = rf_model.predict_proba(data_nuevo_pca)

    umbral = obtener_umbral(moneda_seleccionada, evento_codigo)
    y_pred = [0 if probas[0] > umbral else 1 for probas in y_proba]

    return y_pred[0]


##################################################################################################################################
# UMBRALES
##################################################################################################################################

def obtener_umbral(moneda_seleccionada, evento_codigo):

    MODELOS_DIR = os.path.join(BASE_DIR, '..', 'Modelos')

    if evento_codigo == 0:
        archivo = 'modelos_umbrales_long_180.csv'
    elif evento_codigo == 1:
        archivo = 'modelos_umbrales_short_180.csv'
    elif evento_codigo == 2:
        archivo = 'modelos_umbrales_long_RSI50.csv'
    elif evento_codigo == 3:
        archivo = 'modelos_umbrales_short_RSI50.csv'
    elif evento_codigo == 4:
        archivo = 'modelos_umbrales_long_HAMMER.csv'
    elif evento_codigo == 5:
        archivo = 'modelos_umbrales_short_HAMMER.csv'
    elif evento_codigo == 7:
        archivo = 'modelos_umbrales_long_DV.csv'
    elif evento_codigo == 8:
        archivo = 'modelos_umbrales_short_DV.csv'
    else:
        raise ValueError("Evento no válido")

    ruta_umbrales = os.path.join(MODELOS_DIR, archivo)

    df_umbrales = pd.read_csv(ruta_umbrales)

    umbral = df_umbrales.loc[
        df_umbrales['Criptomoneda'] == moneda_seleccionada,
        'Umbral'
    ].values[0]

    return umbral


##################################################################################################################################

if __name__ == "__main__":

    moneda_seleccionada = sys.argv[1]
    evento_codigo = int(sys.argv[2])

    print(f"Analizando {moneda_seleccionada}")
    CARGARMODELO(moneda_seleccionada, evento_codigo)