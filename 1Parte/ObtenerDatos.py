import requests
import pandas as pd
from datetime import datetime, timezone, timedelta
import numpy as np 
import pandas_ta as ta
import sys
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..'))
ARCHIVOS_DIR = os.path.join(PROJECT_ROOT, 'Archivos')

def crearDataFrame(moneda_seleccionada,factor, eventos_confirmados):

    # Define los parámetros de la solicitud
    symbol = f'{moneda_seleccionada}USDT' ################## <-
    ##################################### <-
    interval = '5m'
    limit = 1000

    # Establece la zona horaria de Ciudad de México
    tz_mexico = timezone(timedelta(hours=-6))
    # Calcula las fechas de inicio y fin en la zona horaria de Ciudad de México
    current_time = datetime.now(tz=tz_mexico)



    """if current_time.hour == 0 and current_time.minute >= 0 and current_time.minute < 5:
        end_time = (current_time - timedelta(days=1)).replace(hour=23, minute=55, second=0, microsecond=0)"""
    if  current_time.minute >= 0 and current_time.minute < 5:
         end_time = current_time.replace(minute=0, second=0, microsecond=0)
    elif current_time.minute >= 5 and current_time.minute < 10:
            end_time = current_time.replace(minute=5, second=0, microsecond=0)
    elif current_time.minute >= 10 and current_time.minute < 15:
            end_time = current_time.replace(minute=10, second=0, microsecond=0)             
    elif current_time.minute >= 15 and current_time.minute < 10:
            end_time = current_time.replace(minute=15, second=0, microsecond=0)
    elif current_time.minute >= 20 and current_time.minute < 25:
            end_time = current_time.replace(minute=20, second=0, microsecond=0)
    elif current_time.minute >= 25 and current_time.minute < 30:
            end_time = current_time.replace(minute=25, second=0, microsecond=0)
    elif current_time.minute >= 30 and current_time.minute < 35:
            end_time = current_time.replace(minute=30, second=0, microsecond=0)
    elif current_time.minute >= 35 and current_time.minute < 40:
            end_time = current_time.replace(minute=35, second=0, microsecond=0)
    elif current_time.minute >= 40 and current_time.minute < 45:
            end_time = current_time.replace(minute=40, second=0, microsecond=0)
    elif current_time.minute >= 45 and current_time.minute < 50:
            end_time = current_time.replace(minute=45, second=0, microsecond=0)
    elif current_time.minute >= 50 and current_time.minute < 55:
            end_time = current_time.replace(minute=50, second=0, microsecond=0)
    elif current_time.minute >= 55 and current_time.minute < 60:
            end_time = current_time.replace(minute=55, second=0, microsecond=0)


    start_time = int((end_time - timedelta(minutes=5 * 1000)).timestamp() * 1000)   ################ SIEMPRE AJUSTA timedelta(minutes=5 * 200). 200 ES EL NUMERO DE VELAS QUE PIDES
    end_time = int(end_time.timestamp() * 1000)


    # Creamos un DataFrame vacío para almacenar todos los datos
    df_total = pd.DataFrame()    




    # Realiza la solicitud a la API de Binance Futures
    url = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}&startTime={start_time}&endTime={end_time}&limit={limit}'
    response = requests.get(url)

        # Procesa los datos de la respuesta
    if response.status_code == 200:
        data = response.json()
        print(f"Datos descargados con éxito.")
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
        df_total = pd.concat([df_total, df], ignore_index=True)

        df_total['timestamp'] = pd.to_datetime(df_total['timestamp'], unit='ms', utc=True).dt.tz_convert(tz_mexico).dt.tz_localize(None)
        df_total['close_time'] = pd.to_datetime(df_total['close_time'], unit='ms', utc=True).dt.tz_convert(tz_mexico).dt.tz_localize(None)

        df_total.columns = ['Fecha/Hora de Apertura', 'Precio de Apertura', 'Precio Máximo', 'Precio Mínimo', 'Precio de Cierre', 'Volumen', 'Fecha/Hora de Cierre', 'Volumen en Divisa de Cotización', 'Número de Operaciones', 'Volumen de Compra Base', 'Volumen de Compra Divisa de Cotización', 'Ignorar']

        df_total['Mes'] = df_total['Fecha/Hora de Apertura'].dt.month
        df_total['Dia'] = df_total['Fecha/Hora de Apertura'].dt.day
        df_total['Hora'] = df_total['Fecha/Hora de Apertura'].dt.hour
        df_total['Minuto'] = df_total['Fecha/Hora de Apertura'].dt.minute
        df_total['DiaSemana'] = df_total['Fecha/Hora de Apertura'].dt.dayofweek + 1

        df_total['Precio de Apertura'] = df_total['Precio de Apertura'].astype(float)*factor
        df_total['Precio Máximo'] = df_total['Precio Máximo'].astype(float)*factor
        df_total['Precio Mínimo'] = df_total['Precio Mínimo'].astype(float)*factor
        df_total['Precio de Cierre'] = df_total['Precio de Cierre'].astype(float)*factor
        df_total['Volumen'] = df_total['Volumen'].astype(float)

        df_total.drop(columns=['Ignorar', 'Volumen en Divisa de Cotización', 'Volumen de Compra Base', 'Volumen de Compra Divisa de Cotización', 'Número de Operaciones'], inplace=True)


# Reordenar las columnas
    df_total = df_total[['Mes', 'Dia', 'Hora', 'Minuto', 'DiaSemana', 'Fecha/Hora de Apertura', 'Precio de Apertura', 'Precio Máximo', 'Precio Mínimo', 'Precio de Cierre', 'Volumen', 'Fecha/Hora de Cierre']]



    # Calcula los indicadores técnicos para df_total
    df_total['SMA20'] = ta.sma(df_total['Precio de Cierre'], length=20).round(2)
    df_total['SMA8'] = ta.sma(df_total['Precio de Cierre'], length=8).round(2)
    df_total['SMA100'] = ta.sma(df_total['Precio de Cierre'], length=100).round(2)
    df_total['RSI'] = ta.rsi(df_total['Precio de Cierre'], length=14).round(5)
    df_total['Color'] = obtenerColordeVela(df_total)
    df_total['Cuerpo2'] = crearCuerpoVela2(df_total).round(0)   
    df_total['MechaAlta2'] = obtenerMechaAlta2(df_total).round(0) 
    df_total['MechaBaja2'] = obtenerMechaBaja2(df_total).round(0) 
    df_total['RSI_50bins']= RSI_100bins(df_total)    
     
    # Pendientes de SMAs
    #df_total['PendienteSMA100'] = getPendienteSMA100(df_total)
    #df_total['PendienteSMA8'] = getPendienteSMA8(df_total)
    #df_total['PendienteSMA20'] = getPendienteSMA20(df_total)

    #Confirmación de velas de poder
    df_total['Martillo_Alcista'] = Martillo_Alcista(df_total).round(0)
    df_total['Martillo_Bajista'] = Martillo_Bajista(df_total).round(0)
    df_total['RSI_Alcista'] = RSI_Alcista(df_total).round(0)
    df_total['RSI_Bajista'] = RSI_Bajista(df_total).round(0)
    df_total['Toro_180'] = Toro_180(df_total).round(0)
    df_total['Oso_180'] = Oso_180(df_total).round(0) 
    df_total['DV_Alcista']= DV_Alcista(df_total)
    df_total['DV_Bajista']= DV_Bajista(df_total)  
    # Cálculo del ATR en diferentes periodos
    df_total['ATR4'] = (calcular_atr(df_total, period=4)).round(5)
    df_total['ATR14'] = (calcular_atr(df_total, period=14)).round(5)
    df_total['ATR20'] = (calcular_atr(df_total, period=20)).round(5)
    df_total['ATR21'] = (calcular_atr(df_total, period=21)).round(5) 
    # Cálculo del ATR en porcentaje
    df_total['ATR4_%'] = ((df_total['ATR4'] / df_total['Precio de Cierre']) * 100).round(5)
    df_total['ATR14_%'] = ((df_total['ATR14'] / df_total['Precio de Cierre']) * 100).round(5)
   
    
    
    
    # ZONA PARA VALIDAR PATRONES #      # ZONA PARA VALIDAR PATRONES #      # ZONA PARA VALIDAR PATRONES #      # ZONA PARA VALIDAR PATRONES #
         
    patron_180_Buy = patron_confirmacion180_Buy(df_total)
    if patron_180_Buy:
        eventos_confirmados.append("Toro_180")

    patron_180_Sell= patron_confirmacion180_Sell(df_total)
    if patron_180_Sell:
        eventos_confirmados.append("Oso_180")

    patron_RSI50_Buy = patron_confirmacion_RSI50_Buy(df_total)
    if patron_RSI50_Buy:
        eventos_confirmados.append("RSI50_Alcista")  

    patron_RSI50_Sell= patron_confirmacion_RSI50_Sell(df_total)    
    if patron_RSI50_Sell:
        eventos_confirmados.append("RSI50_Bajista")

    patron_HAMMER_Buy = patron_confirmacion_HAMMER_Buy(df_total)
    if patron_HAMMER_Buy:
        eventos_confirmados.append("HAMMER_Alcista")  

    patron_HAMMER_Sell= patron_confirmacion_HAMMER_Sell(df_total)    
    if patron_HAMMER_Sell:
        eventos_confirmados.append("HAMMER_Bajista")

    patron_DV_Buy = patron_confirmacion_DV_Buy(df_total)
    if patron_DV_Buy:
        eventos_confirmados.append("DV_Alcista")  

    patron_DV_Sell= patron_confirmacion_DV_Sell(df_total)    
    if patron_DV_Sell:
        eventos_confirmados.append("DV_Bajista")        


    # ZONA PARA VALIDAR PATRONES #      # ZONA PARA VALIDAR PATRONES #      # ZONA PARA VALIDAR PATRONES #      # ZONA PARA VALIDAR PATRONES #
                                  
    
        # Eliminar las primeras 70 filas de datos
    df_total = df_total.iloc[970:]
    # Reiniciar los índices del DataFrame
    df_total.reset_index(drop=True, inplace=True)




    #    F  U   N   C   I   O   N   E   S       D   E       2  _   B   A   C   K       T   E   S   T   I   N   G        #
    # Capturar posiciones de las velas
    df_total['pos_close'] = pos_close(df_total) 
    df_total['pos_MA20'] = pos_MA20(df_total) 

    #    D   R   O   P   S       D   E       C   R   E   A   R       D   A   T   A   S   E   T   S       #
    df_total = df_total.drop(columns=['Volumen'])
    df_total = df_total.drop(columns=['RSI'])
    df_total = df_total.drop(columns=['Cuerpo2'])
    df_total = df_total.drop(columns=['MechaAlta2'])
    df_total = df_total.drop(columns=['MechaBaja2'])
    df_total = df_total.drop(columns=['ATR4'])

    #    D   R   O   P   S       D   E       2  _   B   A   C   K       T   E   S   T   I   N   G           #
    df_total = df_total.drop(columns=['Mes'])
    df_total = df_total.drop(columns=['Dia'])
    df_total = df_total.drop(columns=['Hora'])
    df_total = df_total.drop(columns=['Minuto'])
    df_total = df_total.drop(columns=['DiaSemana'])
    df_total = df_total.drop(columns=['Fecha/Hora de Apertura'])
    df_total = df_total.drop(columns=['Precio de Apertura'])
    df_total = df_total.drop(columns=['Precio Máximo'])
    df_total = df_total.drop(columns=['Precio Mínimo'])
    df_total = df_total.drop(columns=['Precio de Cierre'])
    df_total = df_total.drop(columns=['Fecha/Hora de Cierre'])
    df_total = df_total.drop(columns=['Martillo_Alcista'])
    df_total = df_total.drop(columns=['Martillo_Bajista'])
    df_total = df_total.drop(columns=['RSI_Alcista'])
    df_total = df_total.drop(columns=['RSI_Bajista'])
    df_total = df_total.drop(columns=['Toro_180'])
    df_total = df_total.drop(columns=['Oso_180'])
    df_total = df_total.drop(columns=['DV_Alcista'])
    df_total = df_total.drop(columns=['DV_Bajista'])
    df_total = df_total.drop(columns=['Color'])

    df_total = df_total.drop(columns=['SMA8'])
    df_total = df_total.drop(columns=['SMA20'])
    df_total = df_total.drop(columns=['SMA100'])
    df_total = df_total.drop(columns=['ATR14'])
    df_total = df_total.drop(columns=['ATR21'])
    df_total = df_total.drop(columns=['ATR20'])


    return df_total,eventos_confirmados, patron_180_Buy, patron_180_Sell, patron_RSI50_Buy, patron_RSI50_Sell, patron_HAMMER_Buy, patron_HAMMER_Sell, patron_DV_Buy, patron_DV_Sell






def crearDataFrameLARGE(moneda_seleccionada,factor):

    # Define los parámetros de la solicitud
    symbol = f'{moneda_seleccionada}USDT' ################## <-
    ##################################### <-
    interval = '2h'
    limit = 1000

    # Establece la zona horaria de Ciudad de México
    tz_mexico = timezone(timedelta(hours=-6))
    # Calcula las fechas de inicio y fin en la zona horaria de Ciudad de México

    current_time = datetime.now(tz=tz_mexico)
    # Verificamos si la hora está entre 0 y 6
    if current_time.hour >= 0 and current_time.hour < 2:
        end_time = (current_time - timedelta(days=1)).replace(hour=22, minute=0, second=0, microsecond=0)
    elif current_time.hour >= 2 and current_time.hour < 4:
        end_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
    elif current_time.hour >= 4 and current_time.hour < 6:
        end_time = current_time.replace(hour=2, minute=0, second=0, microsecond=0)
    elif current_time.hour >= 6 and current_time.hour < 8:
        end_time = current_time.replace(hour=4, minute=0, second=0, microsecond=0)
    elif current_time.hour >= 8 and current_time.hour < 10:
        end_time = current_time.replace(hour=6, minute=0, second=0, microsecond=0)
    elif current_time.hour >= 10 and current_time.hour < 12:
        end_time = current_time.replace(hour=8, minute=0, second=0, microsecond=0)
    elif current_time.hour >= 12 and current_time.hour < 14:
        end_time = current_time.replace(hour=10, minute=0, second=0, microsecond=0)
    elif current_time.hour >= 14 and current_time.hour < 16:
        end_time = current_time.replace(hour=12, minute=0, second=0, microsecond=0)
    elif current_time.hour >= 16 and current_time.hour < 18:
        end_time = current_time.replace(hour=14, minute=0, second=0, microsecond=0)
    elif current_time.hour >= 18 and current_time.hour < 20:
        end_time = current_time.replace(hour=16, minute=0, second=0, microsecond=0)
    elif current_time.hour >= 20 and current_time.hour < 22:
        end_time = current_time.replace(hour=18, minute=0, second=0, microsecond=0)
    elif current_time.hour >= 22 and current_time.hour < 24:
        end_time = current_time.replace(hour=20, minute=0, second=0, microsecond=0)    
    # Calcular el tiempo de inicio basándose en la última vela completa

    start_time = end_time - timedelta(hours=2 * (limit - 1))

    # Convertir los tiempos a milisegundos desde la época Unix
    start_time = int(start_time.timestamp() * 1000)
    end_time = int(end_time.timestamp() * 1000)


    # Creamos un DataFrame vacío para almacenar todos los datos
    df_total = pd.DataFrame()    




    # Realiza la solicitud a la API de Binance Futures
    url = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}&startTime={start_time}&endTime={end_time}&limit={limit}'
    response = requests.get(url)

        # Procesa los datos de la respuesta
    if response.status_code == 200:
        data = response.json()

        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
        df_total = pd.concat([df_total, df], ignore_index=True)

        df_total['timestamp'] = pd.to_datetime(df_total['timestamp'], unit='ms', utc=True).dt.tz_convert(tz_mexico).dt.tz_localize(None)
        df_total['close_time'] = pd.to_datetime(df_total['close_time'], unit='ms', utc=True).dt.tz_convert(tz_mexico).dt.tz_localize(None)

        df_total.columns = ['Fecha/Hora de Apertura', 'Precio de Apertura', 'Precio Máximo', 'Precio Mínimo', 'Precio de Cierre', 'Volumen', 'Fecha/Hora de Cierre', 'Volumen en Divisa de Cotización', 'Número de Operaciones', 'Volumen de Compra Base', 'Volumen de Compra Divisa de Cotización', 'Ignorar']

        df_total['Mes'] = df_total['Fecha/Hora de Apertura'].dt.month
        df_total['Dia'] = df_total['Fecha/Hora de Apertura'].dt.day
        df_total['Hora'] = df_total['Fecha/Hora de Apertura'].dt.hour
        df_total['Minuto'] = df_total['Fecha/Hora de Apertura'].dt.minute
        df_total['DiaSemana'] = df_total['Fecha/Hora de Apertura'].dt.dayofweek + 1

        df_total['Precio de Apertura'] = df_total['Precio de Apertura'].astype(float)*factor
        df_total['Precio Máximo'] = df_total['Precio Máximo'].astype(float)*factor
        df_total['Precio Mínimo'] = df_total['Precio Mínimo'].astype(float)*factor
        df_total['Precio de Cierre'] = df_total['Precio de Cierre'].astype(float)*factor
        df_total['Volumen'] = df_total['Volumen'].astype(float)

        df_total.drop(columns=['Ignorar', 'Volumen en Divisa de Cotización', 'Volumen de Compra Base', 'Volumen de Compra Divisa de Cotización', 'Número de Operaciones'], inplace=True)


# Reordenar las columnas
    df_total = df_total[['Mes', 'Dia', 'Hora', 'Minuto', 'DiaSemana', 'Fecha/Hora de Apertura', 'Precio de Apertura', 'Precio Máximo', 'Precio Mínimo', 'Precio de Cierre', 'Volumen', 'Fecha/Hora de Cierre']]



    # Calcula los indicadores técnicos para df_total
    df_total['SMA20'] = ta.sma(df_total['Precio de Cierre'], length=20).round(2)
    df_total['SMA8'] = ta.sma(df_total['Precio de Cierre'], length=8).round(2)
    df_total['SMA100'] = ta.sma(df_total['Precio de Cierre'], length=100).round(2)
    df_total['RSI'] = ta.rsi(df_total['Precio de Cierre'], length=14).round(5)
    df_total['Color'] = obtenerColordeVela(df_total)
    df_total['Cuerpo2'] = crearCuerpoVela2(df_total).round(0)   
    df_total['MechaAlta2'] = obtenerMechaAlta2(df_total).round(0) 
    df_total['MechaBaja2'] = obtenerMechaBaja2(df_total).round(0) 
    df_total['RSI_50bins']= RSI_100bins(df_total)    
     
    # Pendientes de SMAs
    #df_total['PendienteSMA100'] = getPendienteSMA100(df_total)
    #df_total['PendienteSMA8'] = getPendienteSMA8(df_total)
    #df_total['PendienteSMA20'] = getPendienteSMA20(df_total)

    #Confirmación de velas de poder
    df_total['Martillo_Alcista'] = Martillo_Alcista(df_total).round(0)
    df_total['Martillo_Bajista'] = Martillo_Bajista(df_total).round(0)
    df_total['RSI_Alcista'] = RSI_Alcista(df_total).round(0)
    df_total['RSI_Bajista'] = RSI_Bajista(df_total).round(0)
    df_total['Toro_180'] = Toro_180(df_total).round(0)
    df_total['Oso_180'] = Oso_180(df_total).round(0) 
    df_total['DV_Alcista']= DV_Alcista(df_total)
    df_total['DV_Bajista']= DV_Bajista(df_total)  
    # Cálculo del ATR en diferentes periodos
    df_total['ATR4'] = (calcular_atr(df_total, period=4)).round(5)
    df_total['ATR14'] = (calcular_atr(df_total, period=14)).round(5)
    #df_total['ATR21'] = calcular_atr(df_total, period=22)
    # Cálculo del ATR en porcentaje
    df_total['ATR4_%'] = ((df_total['ATR4'] / df_total['Precio de Cierre']) * 100).round(5)
    df_total['ATR14_%'] = ((df_total['ATR14'] / df_total['Precio de Cierre']) * 100).round(5)
   
    
   
        # Eliminar las primeras 70 filas de datos
    df_total = df_total.iloc[970:]
    # Reiniciar los índices del DataFrame
    df_total.reset_index(drop=True, inplace=True)



    #    F  U   N   C   I   O   N   E   S       D   E       2  _   B   A   C   K       T   E   S   T   I   N   G        #
    df_total['pos_close'] = pos_close(df_total) 
    df_total['pos_MA20'] = pos_MA20(df_total) 

    #    D   R   O   P   S       D   E       C   R   E   A   R       D   A   T   A   S   E   T   S       #
    df_total = df_total.drop(columns=['Volumen'])
    df_total = df_total.drop(columns=['RSI'])
    df_total = df_total.drop(columns=['Cuerpo2'])
    df_total = df_total.drop(columns=['MechaAlta2'])
    df_total = df_total.drop(columns=['MechaBaja2'])
    df_total = df_total.drop(columns=['ATR4'])
    df_total = df_total.drop(columns=['ATR14'])

    #    D   R   O   P   S       D   E       2  _   B   A   C   K       T   E   S   T   I   N   G           #
    df_total = df_total.drop(columns=['Mes'])
    df_total = df_total.drop(columns=['Dia'])
    df_total = df_total.drop(columns=['Hora'])
    df_total = df_total.drop(columns=['Minuto'])
    df_total = df_total.drop(columns=['DiaSemana'])
    df_total = df_total.drop(columns=['Fecha/Hora de Apertura'])
    df_total = df_total.drop(columns=['Precio de Apertura'])
    df_total = df_total.drop(columns=['Precio Máximo'])
    df_total = df_total.drop(columns=['Precio Mínimo'])
    df_total = df_total.drop(columns=['Precio de Cierre'])
    df_total = df_total.drop(columns=['Fecha/Hora de Cierre'])
    df_total = df_total.drop(columns=['Martillo_Alcista'])
    df_total = df_total.drop(columns=['Martillo_Bajista'])
    df_total = df_total.drop(columns=['RSI_Alcista'])
    df_total = df_total.drop(columns=['RSI_Bajista'])
    df_total = df_total.drop(columns=['Toro_180'])
    df_total = df_total.drop(columns=['Oso_180'])
    df_total = df_total.drop(columns=['DV_Alcista'])
    df_total = df_total.drop(columns=['DV_Bajista'])
    df_total = df_total.drop(columns=['Color'])

    df_total = df_total.drop(columns=['SMA8'])
    df_total = df_total.drop(columns=['SMA20'])
    df_total = df_total.drop(columns=['SMA100']) 
     

    return df_total



"""+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +  +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   ++  +   +   +   +   """
"""+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +  +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   ++  +   +   +   +   """
"""+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +  +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   ++  +   +   +   +   """
def patron_confirmacion180_Buy(datos_current):
    patron_confirmacion180_Buy = False    
    if (datos_current['Toro_180'].iloc[-1] == 1) and (datos_current['RSI_Alcista'].iloc[-1] == 0)and (datos_current['Martillo_Alcista'].iloc[-1] == 0) and (datos_current['DV_Alcista'].iloc[-1] == 0):
                print(" Se detecto Toro_180")
                patron_confirmacion180_Buy = True

    return patron_confirmacion180_Buy    

def patron_confirmacion180_Sell(datos_current):
    patron_confirmacion180_Sell = False
    if (datos_current['Oso_180'].iloc[-1] == 1) and (datos_current['RSI_Bajista'].iloc[-1] == 0)and (datos_current['Martillo_Bajista'].iloc[-1] == 0) and (datos_current['DV_Bajista'].iloc[-1] == 0):
            print(" Se detecto Oso_180")
            patron_confirmacion180_Sell = True

    return patron_confirmacion180_Sell     


def patron_confirmacion_RSI50_Buy(datos_current):
    patron_confirmacion180_Buy = False    
    if (datos_current['RSI_Alcista'].iloc[-1] == 1):
                print(" Se detecto RSI_Alcista")
                patron_confirmacion180_Buy = True
 
    return patron_confirmacion180_Buy    

def patron_confirmacion_RSI50_Sell(datos_current):
    patron_confirmacion180_Sell = False
    if (datos_current['RSI_Bajista'].iloc[-1] == 1): 
            print(" Se detecto RSI_Bajista")
            patron_confirmacion180_Sell = True

    return patron_confirmacion180_Sell 



def patron_confirmacion_HAMMER_Buy(datos_current):
    patron_confirmacion180_Buy = False    
    if  (datos_current['Martillo_Alcista'].iloc[-1] == 1)and(datos_current['Toro_180'].iloc[-1] == 0) and (datos_current['RSI_Alcista'].iloc[-1] == 0) and (datos_current['DV_Alcista'].iloc[-1] == 0):            
                print(" Se detecto Martillo_Alcista")
                patron_confirmacion180_Buy = True

    return patron_confirmacion180_Buy    

def patron_confirmacion_HAMMER_Sell(datos_current):
    patron_confirmacion180_Sell = False
    if  (datos_current['Martillo_Bajista'].iloc[-1] == 1)and(datos_current['Oso_180'].iloc[-1] == 0) and (datos_current['RSI_Bajista'].iloc[-1] == 0) and (datos_current['DV_Bajista'].iloc[-1] == 0):
            print(" Se detecto Martillo_Bajista")
            patron_confirmacion180_Sell = True

    return patron_confirmacion180_Sell 



def patron_confirmacion_DV_Buy(datos_current):
    patron_confirmacion180_Buy = False    
    if (datos_current['DV_Alcista'].iloc[-1] == 1) and (datos_current['RSI_Alcista'].iloc[-1] == 0)and (datos_current['Martillo_Alcista'].iloc[-1] == 0) and (datos_current['Toro_180'].iloc[-1] == 0):            
                print(" Se detecto DV_Alcista")
                patron_confirmacion180_Buy = True

    return patron_confirmacion180_Buy    

def patron_confirmacion_DV_Sell(datos_current):
    patron_confirmacion180_Sell = False
    if (datos_current['DV_Bajista'].iloc[-1] == 1) and (datos_current['RSI_Bajista'].iloc[-1] == 0)and (datos_current['Martillo_Bajista'].iloc[-1] == 0) and (datos_current['Oso_180'].iloc[-1] == 0):
            print(" Se detecto DV_Bajista")
            patron_confirmacion180_Sell = True

    return patron_confirmacion180_Sell 

"""+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +  +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   ++  +   +   +   +   """
"""+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +  +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   ++  +   +   +   +   """
"""+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +  +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   ++  +   +   +   +   """


def mechaganadora(df_total):

    # Calcula la diferencia entre el precio de cierre y el precio de apertura
    diferencia = df_total['MechaAlta2'] - df_total['MechaBaja2'] 
    
    # Asigna 1 si la diferencia es mayor que 0 (verde), 0 si la diferencia es igual a 0 (neutral) y -1 si la diferencia es menor que 0 (rojo)
    ganador = np.where(diferencia > 0, -1, np.where(diferencia < 0, 1, 0))
    
    return ganador


def rebote_verde(df_total):
    color_actual = df_total['Color']
    color_anterior = df_total['Color'].shift(1)
    color_anteanterior = df_total['Color'].shift(2)
    cierre_actual = df_total['Precio de Cierre']
    maximo_anterior = df_total['Precio Máximo'].shift(1)
    confirmacion = np.where(
        (color_anteanterior == -1) &
        (color_anterior == 1) &
        (color_actual == 1) &
        (cierre_actual > maximo_anterior),
        1,
        0
    )
    return confirmacion 


def rebote_rojo(df_total):
    color_actual = df_total['Color']
    color_anterior = df_total['Color'].shift(1)
    color_anteanterior = df_total['Color'].shift(2)
    cierre_actual = df_total['Precio de Cierre']
    minimo_anterior = df_total['Precio Mínimo'].shift(1)
    confirmacion = np.where(
        (color_anteanterior == 1) &
        (color_anterior == -1) &
        (color_actual == -1) &
        (cierre_actual < minimo_anterior),
        1,
        0
    )
    return confirmacion 


 # Funciones para crear columnas nuevas para enseñarle al algoritmo los eventos de entrada de importancia
def Martillo_Alcista(df_total):
    mecha_bajista = df_total['MechaAlta2']
    # Obtenemos valor de la mecha alcista
    mecha_alcista = df_total['MechaBaja2']
    #Obtener Color
    color = df_total['Color'] 
    # Obtenemos cuerpo2 de la vela
    cuerpo = df_total['Cuerpo2'] 
    # Usamos np.where para verificar las condiciones vectorizadas
    hammer_confirmacion = np.where(
        (mecha_alcista > mecha_bajista) &  # Usamos & para comparar arrays
        (mecha_alcista > cuerpo) & 
        (color == 1) & 
        (mecha_alcista >= 55),
        1,  # Si se cumplen todas las condiciones, devuelve 1
        0   # Si no se cumplen, devuelve 0
    )
    return hammer_confirmacion  


def Martillo_Bajista(df_total):
    mecha_bajista = df_total['MechaAlta2']
    # Obtenemos valor de la mecha alcista
    mecha_alcista = df_total['MechaBaja2'] 
    #Obtener Color
    color = df_total['Color']     
    # Obtenemos cuerpo2 de la vela
    cuerpo = df_total['Cuerpo2'] 
    # Usamos np.where para verificar las condiciones vectorizadas
    hammer_confirmacion = np.where(
        (mecha_alcista < mecha_bajista) &  # Usamos & para comparar arrays
        (mecha_bajista > cuerpo) & 
        (color == -1) & 
        (mecha_bajista >= 55),
        1,  # Si se cumplen todas las condiciones, devuelve 1
        0   # Si no se cumplen, devuelve 0
    )
    return hammer_confirmacion  


def RSI_Alcista(df_total):
    RSI_valor_actual = df_total['RSI']
    RSI_valor_anterior = df_total['RSI'].shift(1)

    # Usamos np.where para verificar las condiciones vectorizadas
    RSI_confirmacion = np.where(
        (RSI_valor_anterior <= 50.5) &  # Usamos & para comparar arrays
        (RSI_valor_actual >= 51.5), 
        1,  # Si se cumplen todas las condiciones, devuelve 1
        0   # Si no se cumplen, devuelve 0
    )
    return RSI_confirmacion  

def RSI_Bajista(df_total):
    RSI_valor_actual = df_total['RSI']
    RSI_valor_anterior = df_total['RSI'].shift(1)

    # Usamos np.where para verificar las condiciones vectorizadas
    RSI_confirmacion = np.where(
        (RSI_valor_anterior >= 49.5) &  # Usamos & para comparar arrays
        (RSI_valor_actual <= 48.5), 
        1,  # Si se cumplen todas las condiciones, devuelve 1
        0   # Si no se cumplen, devuelve 0
    )
    return RSI_confirmacion 



def Toro_180(df_total):
    cierre_actual = df_total['Precio de Cierre']
    maximo_anterior = df_total['Precio Máximo'].shift(1)
    color_actual = df_total['Color']
    color_anterior = df_total['Color'].shift(1)
    # Usamos np.where para verificar las condiciones vectorizadas
    confirmacion_180 = np.where(
        (cierre_actual > maximo_anterior) &  # Usamos & para comparar arrays
        (color_anterior == -1) &
        (color_actual == 1), 
        1,  # Si se cumplen todas las condiciones, devuelve 1
        0   # Si no se cumplen, devuelve 0
    )
    return confirmacion_180 


def Oso_180(df_total):
    cierre_actual = df_total['Precio de Cierre']
    minimo_anterior = df_total['Precio Mínimo'].shift(1)
    color_actual = df_total['Color']
    color_anterior = df_total['Color'].shift(1)
    # Usamos np.where para verificar las condiciones vectorizadas
    confirmacion_180 = np.where(
        (cierre_actual < minimo_anterior) &  # Usamos & para comparar arrays
        (color_anterior == 1) &
        (color_actual == -1),  
        1,  # Si se cumplen todas las condiciones, devuelve 1
        0   # Si no se cumplen, devuelve 0
    )
    return confirmacion_180 




def DV_Alcista(df_total):
    cierre_actual = df_total['Precio de Cierre']
    maximo_anterior = df_total['Precio Máximo'].shift(1)
    color_actual = df_total['Color']
    color_anterior = df_total['Color'].shift(1)
    # Usamos np.where para verificar las condiciones vectorizadas
    confirmacion_180 = np.where(
        (cierre_actual > maximo_anterior) &  # Usamos & para comparar arrays
        (color_anterior == 1) &
        (color_actual == 1), 
        1,  # Si se cumplen todas las condiciones, devuelve 1
        0   # Si no se cumplen, devuelve 0
    )
    return confirmacion_180 


def DV_Bajista(df_total):
    cierre_actual = df_total['Precio de Cierre']
    minimo_anterior = df_total['Precio Mínimo'].shift(1)
    color_actual = df_total['Color']
    color_anterior = df_total['Color'].shift(1)
    # Usamos np.where para verificar las condiciones vectorizadas
    confirmacion_180 = np.where(
        (cierre_actual < minimo_anterior) &  # Usamos & para comparar arrays
        (color_anterior == -1) &
        (color_actual == -1),  
        1,  # Si se cumplen todas las condiciones, devuelve 1
        0   # Si no se cumplen, devuelve 0
    )
    return confirmacion_180 


def LVL_Pwr_Green(df_total):
    poder_verde = df_total['Cuerpo_AVG_GREEN']
    poder_rojo = df_total['Cuerpo_AVG_RED']
    diferencia = (poder_verde - poder_rojo) / poder_verde

    # Invertimos el orden de las condiciones para que las más específicas se evalúen primero
    condiciones = [
        (diferencia > 0.5),  # Evaluar primero la condición más restrictiva
        (diferencia > 0.4),
        (diferencia > 0.3),
        (diferencia > 0.2),
        (poder_verde > poder_rojo)  # Esta condición se evaluará al final
    ]

    valores = [5, 4, 3, 2, 1]  # Valores correspondientes a las condiciones, también invertidos

    # np.select aplica las condiciones y devuelve el valor correspondiente
    nivel = np.select(condiciones, valores, default=0)

    return nivel


def LVL_Pwr_Red(df_total):
    poder_verde = df_total['Cuerpo_AVG_GREEN']
    poder_rojo = df_total['Cuerpo_AVG_RED']
    diferencia = (poder_rojo-poder_verde)/poder_rojo

    condiciones = [
        (diferencia > 0.5),  # Evaluar primero la condición más restrictiva
        (diferencia > 0.4),
        (diferencia > 0.3),
        (diferencia > 0.2),
        (poder_verde > poder_rojo)  # Esta condición se evaluará al final
    ]

    valores = [5, 4, 3, 2, 1]  # Valores correspondientes a las condiciones, también invertidos

    # np.select aplica las condiciones y devuelve el valor correspondiente
    nivel = np.select(condiciones, valores, default=0)

    return nivel



#                           ///////////////////////////////////////////////////////////////////////////////////////////////////////////////                         #

def obtenerColordeVela(df_total):  
    # Calcula la diferencia entre el precio de cierre y el precio de apertura
    diferencia = df_total['Precio de Cierre'] - df_total['Precio de Apertura'] 
    
    # Asigna 1 si la diferencia es mayor que 0 (verde), 0 si la diferencia es igual a 0 (neutral) y -1 si la diferencia es menor que 0 (rojo)
    color = np.where(diferencia > 0, 1, np.where(diferencia < 0, -1, 0))
    
    return color






def obtenerMechaAlta(df_total):
    rangoTotalVela = df_total['Precio Máximo'] - df_total['Precio Mínimo']
    dif_aperturacierre = df_total['Precio de Cierre'] - df_total['Precio de Apertura']
    # Usando operaciones vectorizadas
    mecha = ((df_total['Precio Máximo'] - df_total['Precio de Cierre']) / rangoTotalVela) * 100
    mecha_alternativa = ((df_total['Precio Máximo'] - df_total['Precio de Apertura']) / rangoTotalVela) * 100
    # Asignar valores basados en la condición
    mecha = mecha.where(dif_aperturacierre >= 0, mecha_alternativa)
    # Reemplazar NaNs con 0
    mecha = mecha.fillna(0)

    # Definir los límites de los 50 bins
    bin_edges = [i * (100 / 50) for i in range(51)]  # 51 puntos para 50 intervalos
    bin_numbers = list(range(1, 51))  # Números de bin de 1 a 50

    # Asignar cada valor a su bin correspondiente
    mecha = pd.cut(mecha, bins=bin_edges, labels=bin_numbers, include_lowest=True).astype(int)    
    return mecha


def obtenerMechaBaja(df_total):
    rangoTotalVela = df_total['Precio Máximo'] - df_total['Precio Mínimo']
    dif_aperturacierre = df_total['Precio de Cierre'] - df_total['Precio de Apertura']    
    # Usando operaciones vectorizadas
    mecha = ((df_total['Precio de Cierre'] - df_total['Precio Mínimo'])/rangoTotalVela)*100
    mecha_alternativa = ((df_total['Precio de Apertura'] - df_total['Precio Mínimo'])/rangoTotalVela)*100  
    # Asignar valores basados en la condición
    mecha = mecha.where(dif_aperturacierre <= 0, mecha_alternativa) 
    # Reemplazar NaNs con 0
    mecha = mecha.fillna(0)

    # Definir los límites de los 50 bins
    bin_edges = [i * (100 / 50) for i in range(51)]  # 51 puntos para 50 intervalos
    bin_numbers = list(range(1, 51))  # Números de bin de 1 a 50

    # Asignar cada valor a su bin correspondiente
    mecha = pd.cut(mecha, bins=bin_edges, labels=bin_numbers, include_lowest=True).astype(int)       
    return mecha





def obtenerMechaAlta2(df_total):
    rangoTotalVela = df_total['Precio Máximo'] - df_total['Precio Mínimo']
    dif_aperturacierre = df_total['Precio de Cierre'] - df_total['Precio de Apertura']
    # Usando operaciones vectorizadas
    mecha = ((df_total['Precio Máximo'] - df_total['Precio de Cierre']) / rangoTotalVela) * 100
    mecha_alternativa = ((df_total['Precio Máximo'] - df_total['Precio de Apertura']) / rangoTotalVela) * 100
    # Asignar valores basados en la condición
    mecha = mecha.where(dif_aperturacierre >= 0, mecha_alternativa)
    # Reemplazar NaNs con 0
    mecha = mecha.fillna(0)


    return mecha


def obtenerMechaBaja2(df_total):
    rangoTotalVela = df_total['Precio Máximo'] - df_total['Precio Mínimo']
    dif_aperturacierre = df_total['Precio de Cierre'] - df_total['Precio de Apertura']    
    # Usando operaciones vectorizadas
    mecha = ((df_total['Precio de Cierre'] - df_total['Precio Mínimo'])/rangoTotalVela)*100
    mecha_alternativa = ((df_total['Precio de Apertura'] - df_total['Precio Mínimo'])/rangoTotalVela)*100  
    # Asignar valores basados en la condición
    mecha = mecha.where(dif_aperturacierre <= 0, mecha_alternativa) 
    # Reemplazar NaNs con 0
    mecha = mecha.fillna(0)

    
    return mecha













def getPendienteSMA100(imagen):
    # Usamos np.where para comparar la fila actual con la fila anterior
    pendienteSMA100 = np.where(
        imagen['SMA100'] > imagen['SMA100'].shift(1),  # Condición
        1,  # Si es mayor, retorna 1
        np.where(  # Si no es mayor
            imagen['SMA100'] < imagen['SMA100'].shift(1),  # Otra condición
            -1,  # Si es menor, retorna -1
            0  # Si son iguales, retorna 0
        )
    )
    return pendienteSMA100



def getPendienteSMA8(imagen):
    # Usamos np.where para comparar la fila actual con la fila anterior
    pendienteSMA8 = np.where(
        imagen['SMA8'] > imagen['SMA8'].shift(1),  # Condición
        1,  # Si es mayor, retorna 1
        np.where(  # Si no es mayor
            imagen['SMA8'] < imagen['SMA8'].shift(1),  # Otra condición
            -1,  # Si es menor, retorna -1
            0  # Si son iguales, retorna 0
        )
    )
    return pendienteSMA8

def getPendienteSMA20(imagen):
    # Usamos np.where para comparar la fila actual con la fila anterior
    pendienteSMA20 = np.where(
        imagen['SMA20'] > imagen['SMA20'].shift(1),  # Condición
        1,  # Si es mayor, retorna 1
        np.where(  # Si no es mayor
            imagen['SMA20'] < imagen['SMA20'].shift(1),  # Otra condición
            -1,  # Si es menor, retorna -1
            0  # Si son iguales, retorna 0
        )
    )
    return pendienteSMA20


def Cuerpo_50bins(df_total):
    # Calcular diferencias y rango total
    dif_aperturacierre = df_total['Precio de Cierre'] - df_total['Precio de Apertura']
    rangoTotalVela = df_total['Precio Máximo'] - df_total['Precio Mínimo']

    # Usando operaciones vectorizadas
    cuerpoverde = ((df_total['Precio de Cierre'] - df_total['Precio de Apertura']) / rangoTotalVela) * 100
    cuerporojo = ((df_total['Precio de Apertura'] - df_total['Precio de Cierre']) / rangoTotalVela) * 100

    # Asignar valores basados en la condición
    cuerpoverde = cuerpoverde.where(dif_aperturacierre >= 0, cuerporojo)

    # Reemplazar NaNs con 0
    cuerpoverde = cuerpoverde.fillna(0)

    # Ajustar los límites de los 50 bins para evitar que las fronteras se toquen
    bin_edges = [i * (100 / 50) for i in range(51)]  # 51 puntos para 50 intervalos
    bin_edges[0] -= 0.0001  # Ajustar el límite inferior del primer bin
    bin_edges[-1] += 0.0001  # Ajustar el límite superior del último bin

    bin_numbers = list(range(1, 51))  # Números de bin de 1 a 50

    # Asignar cada valor a su bin correspondiente
    cuerpo_bins = pd.cut(cuerpoverde, bins=bin_edges, labels=bin_numbers, include_lowest=True).astype(int)
    
    return cuerpo_bins




def crearCuerpoVela2(df_total):
    # Calcular diferencias y rango total
    dif_aperturacierre = df_total['Precio de Cierre'] - df_total['Precio de Apertura']
    rangoTotalVela = df_total['Precio Máximo'] - df_total['Precio Mínimo']

    # Usando operaciones vectorizadas
    cuerpoverde = ((df_total['Precio de Cierre'] - df_total['Precio de Apertura']) / rangoTotalVela) * 100
    cuerporojo = ((df_total['Precio de Apertura'] - df_total['Precio de Cierre']) / rangoTotalVela) * 100

    # Asignar valores basados en la condición
    cuerpoverde = cuerpoverde.where(dif_aperturacierre >= 0, cuerporojo)

    # Reemplazar NaNs con 0
    cuerpoverde = cuerpoverde.fillna(0)


    return cuerpoverde




# Definir la función RSI_50bins con rango ajustado
def RSI_100bins(df_total):
    """
    Asigna un bin (1 a 50) al valor del RSI basado en un rango estático de 8 a 91,
    dividido en 50 bins sin fronteras tocadas.
    """
    # Definir el rango estático (8 a 91) y dividirlo en 50 bins
    bin_edges = [8 + i * ((91 - 8) / 100) for i in range(101)]  # 51 puntos para 50 bins

    # Ajustar los bordes superiores excepto el último para evitar colisión
    bin_edges = [edge if i == 0 else edge - 1e-9 for i, edge in enumerate(bin_edges)]

    # Etiquetas de los bins (1 a 50)
    bin_numbers = list(range(1, 101))

    # Asegurarse de que los valores de RSI están dentro del rango 8-91
    df_total['RSI'] = df_total['RSI'].clip(lower=8, upper=91)

    # Asignar cada valor de RSI a su bin correspondiente
    rsi_bins = pd.cut(
        df_total['RSI'],  # Columna RSI del DataFrame
        bins=bin_edges,  # Bordes de los bins ajustados
        labels=bin_numbers,  # Etiquetas de los bins
        include_lowest=True  # Incluir el valor más bajo en el primer bin
    )

    # Reemplazar cualquier NaN con un valor por defecto (opcional, como el primer bin)
    rsi_bins = rsi_bins.cat.add_categories([0]).fillna(0).astype(int)  # Convertir etiquetas a enteros

    return rsi_bins








def MechaBajista_50bins(df_total):
    rangoTotalVela = df_total['Precio Máximo'] - df_total['Precio Mínimo']
    dif_aperturacierre = df_total['Precio de Cierre'] - df_total['Precio de Apertura']
    # Usando operaciones vectorizadas
    mecha = ((df_total['Precio Máximo'] - df_total['Precio de Cierre']) / rangoTotalVela) * 100
    mecha_alternativa = ((df_total['Precio Máximo'] - df_total['Precio de Apertura']) / rangoTotalVela) * 100
    # Asignar valores basados en la condición
    mecha = mecha.where(dif_aperturacierre >= 0, mecha_alternativa)
    # Reemplazar NaNs con 0
    mecha = mecha.fillna(0)

    # Ajustar los límites de los 50 bins para evitar que las fronteras se toquen
    bin_edges = [i * (100 / 50) for i in range(51)]  # 51 puntos para 50 intervalos
    bin_edges[0] -= 0.0001  # Ajustar el límite inferior del primer bin
    bin_edges[-1] += 0.0001  # Ajustar el límite superior del último bin

    bin_numbers = list(range(1, 51))  # Números de bin de 1 a 50

    # Asignar cada valor a su bin correspondiente
    mecha_bins = pd.cut(mecha, bins=bin_edges, labels=bin_numbers, include_lowest=True).astype(int)
    
    return mecha_bins


def MechaAlcista_50bins(df_total):
    rangoTotalVela = df_total['Precio Máximo'] - df_total['Precio Mínimo']
    dif_aperturacierre = df_total['Precio de Cierre'] - df_total['Precio de Apertura']    
    # Usando operaciones vectorizadas
    mecha = ((df_total['Precio de Cierre'] - df_total['Precio Mínimo'])/rangoTotalVela)*100
    mecha_alternativa = ((df_total['Precio de Apertura'] - df_total['Precio Mínimo'])/rangoTotalVela)*100  
    # Asignar valores basados en la condición
    mecha = mecha.where(dif_aperturacierre <= 0, mecha_alternativa) 
    # Reemplazar NaNs con 0
    mecha = mecha.fillna(0)

    # Ajustar los límites de los 50 bins para evitar que las fronteras se toquen
    bin_edges = [i * (100 / 50) for i in range(51)]  # 51 puntos para 50 intervalos
    bin_edges[0] -= 0.0001  # Ajustar el límite inferior del primer bin
    bin_edges[-1] += 0.0001  # Ajustar el límite superior del último bin

    bin_numbers = list(range(1, 51))  # Números de bin de 1 a 50

    # Asignar cada valor a su bin correspondiente
    mecha_bins = pd.cut(mecha, bins=bin_edges, labels=bin_numbers, include_lowest=True).astype(int)
    
    return mecha_bins


def calcular_atr(df, period):
    """
    Calcula el Average True Range (ATR) manualmente.
    
    :param df: DataFrame con las columnas 'Precio Máximo', 'Precio Mínimo' y 'Precio de Cierre'
    :param period: Número de periodos para el cálculo del ATR
    :return: Serie de ATR calculada manualmente
    """
    high_low = df['Precio Máximo'] - df['Precio Mínimo']
    high_close = np.abs(df['Precio Máximo'] - df['Precio de Cierre'].shift(1))
    low_close = np.abs(df['Precio Mínimo'] - df['Precio de Cierre'].shift(1))

    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

    atr = true_range.rolling(window=period).mean()  # Promedio simple del TR
    return atr




def obtenerAltura(imagen): # Esta función nos dice a que altura está una determinada vela en el cuadro/pantalla
    # Valor máximo de la columna 'Precio Máximo'

    precio_maximo = imagen['Precio Máximo'].max()
    # Valor mínimo de la columna 'Precio Mínimo'
    precio_minimo = imagen['Precio Mínimo'].min()
    rangoDatos = precio_maximo - precio_minimo
    ranguitoDatoActual = imagen['Precio Máximo'] - precio_minimo
    alturaActual = (ranguitoDatoActual/rangoDatos)*100
    return alturaActual





def Altura_20(imagen):
    # Primero sacamos la volatilidad de todo el dataframe 30
    precio_maximo = imagen['Precio Máximo'].max()
    # Valor mínimo de la columna 'Precio Mínimo'
    precio_minimo = imagen['Precio Mínimo'].min()
    rangoDatos = precio_maximo - precio_minimo

    AlturaSMA = imagen['SMA20'] - precio_minimo
    alturaActual = (AlturaSMA/rangoDatos)*100
    return alturaActual



def Altura_8(imagen):
    # Primero sacamos la volatilidad de todo el dataframe 30
    precio_maximo = imagen['Precio Máximo'].max()
    # Valor mínimo de la columna 'Precio Mínimo'
    precio_minimo = imagen['Precio Mínimo'].min()
    rangoDatos = precio_maximo - precio_minimo

    AlturaSMA = imagen['SMA8'] - precio_minimo
    alturaActual = (AlturaSMA/rangoDatos)*100
    return alturaActual

def Altura_4(imagen):
    # Primero sacamos la volatilidad de todo el dataframe 30
    precio_maximo = imagen['Precio Máximo'].max()
    # Valor mínimo de la columna 'Precio Mínimo'
    precio_minimo = imagen['Precio Mínimo'].min()
    rangoDatos = precio_maximo - precio_minimo

    AlturaSMA = imagen['SMA4'] - precio_minimo
    alturaActual = (AlturaSMA/rangoDatos)*100
    return alturaActual


def Elefanteverde(df):
    # 1. Calcular el valor promedio de la columna "Volatilidad"
    volatilidad_promedio = df['Volatilidad'].mean()

    # 2. Comparar el valor de "Volatilidad" de la fila actual con 2 veces el promedio
    # y también verificar si el 'Color' es 1
    return df.apply(lambda row: 1 if (row['Volatilidad'] > 1.5 * volatilidad_promedio and row['Color'] == 1) else 0, axis=1)

def Elefanterojo(df):
    # 1. Calcular el valor promedio de la columna "Volatilidad"
    volatilidad_promedio = df['Volatilidad'].mean()

    # 2. Comparar el valor de "Volatilidad" de la fila actual con 2 veces el promedio
    # y también verificar si el 'Color' es 1
    return df.apply(lambda row: 1 if (row['Volatilidad'] > 1.5 * volatilidad_promedio and row['Color'] == -1) else 0, axis=1)



def Apertura(imagen_current):
    #Definimos la altura total del df
    altura_max = imagen_current['Precio Máximo'].max()
    altura_min = imagen_current['Precio Mínimo'].min()
    rangoDatos = altura_max - altura_min

    #Definimos altura del precio de apertura
    altura_apertura = imagen_current['Precio de Apertura']
    rango_chico = (altura_apertura-altura_min)

    # Calculamos la altura proporcional
    apertura = (rango_chico/rangoDatos)*100
    return apertura

def Maximo(imagen_current):
    #Definimos la altura total del df
    altura_max = imagen_current['Precio Máximo'].max()
    altura_min = imagen_current['Precio Mínimo'].min()
    rangoDatos = altura_max - altura_min

    #Definimos altura del precio de apertura
    altura_apertura = imagen_current['Precio Máximo']
    rango_chico = (altura_apertura-altura_min)

    # Calculamos la altura proporcional
    apertura = (rango_chico/rangoDatos)*100
    return apertura

def Minimo(imagen_current):
    #Definimos la altura total del df
    altura_max = imagen_current['Precio Máximo'].max()
    altura_min = imagen_current['Precio Mínimo'].min()
    rangoDatos = altura_max - altura_min

    #Definimos altura del precio de apertura
    altura_apertura = imagen_current['Precio Mínimo']
    rango_chico = (altura_apertura-altura_min)

    # Calculamos la altura proporcional
    apertura = (rango_chico/rangoDatos)*100
    return apertura





def Contc_20(imagen_current):
    maximo = imagen_current['Precio Máximo']
    minimo = imagen_current['Precio Mínimo']
    cierre = imagen_current['Precio de Cierre']
    apertura = imagen_current['Precio de Apertura']
    ma20 =  imagen_current['SMA20']

    # Usamos np.where
    contacto_tipo = np.where(
        (maximo > ma20) &
        (minimo > ma20) &
        (cierre > ma20) &
        (apertura > ma20),  # Condición
        1,  # Si todo es mayor a SMA20, retorna 1
        np.where(  # Si no es mayor
            (maximo < ma20) &
            (minimo < ma20) &
            (cierre < ma20) &
            (apertura < ma20),  # Condición
            -1, # Si todo es menor a SMA20, retorna -1
             0  # Si no, regresa cero, pues hay contacto en esta SMA20
        )
    )
    return contacto_tipo    

def Contc_8(imagen_current):
    maximo = imagen_current['Precio Máximo']
    minimo = imagen_current['Precio Mínimo']
    cierre = imagen_current['Precio de Cierre']
    apertura = imagen_current['Precio de Apertura']
    ma20 =  imagen_current['SMA8']

    # Usamos np.where
    contacto_tipo = np.where(
        (maximo > ma20) &
        (minimo > ma20) &
        (cierre > ma20) &
        (apertura > ma20),  # Condición
        1,  # Si todo es mayor a SMA20, retorna 1
        np.where(  # Si no es mayor
            (maximo < ma20) &
            (minimo < ma20) &
            (cierre < ma20) &
            (apertura < ma20),  # Condición
            -1, # Si todo es menor a SMA20, retorna -1
             0  # Si no, regresa cero, pues hay contacto en esta SMA20
        )
    )
    return contacto_tipo   

def Contc_4(imagen_current):
    maximo = imagen_current['Precio Máximo']
    minimo = imagen_current['Precio Mínimo']
    cierre = imagen_current['Precio de Cierre']
    apertura = imagen_current['Precio de Apertura']
    ma20 =  imagen_current['SMA4']

    # Usamos np.where
    contacto_tipo = np.where(
        (maximo > ma20) &
        (minimo > ma20) &
        (cierre > ma20) &
        (apertura > ma20),  # Condición
        1,  # Si todo es mayor a SMA20, retorna 1
        np.where(  # Si no es mayor
            (maximo < ma20) &
            (minimo < ma20) &
            (cierre < ma20) &
            (apertura < ma20),  # Condición
            -1, # Si todo es menor a SMA20, retorna -1
             0  # Si no, regresa cero, pues hay contacto en esta SMA20
        )
    )
    return contacto_tipo   


def la_mayor_verde(dataframe):
    # Calcula el valor máximo en 'Volatilidad' donde 'Color' == 1
    max_volatilidad_verde = dataframe[dataframe['Color'] == 1]['Volatilidad'].max()
    
    # Usamos np.where para crear una nueva columna con el resultado
    resultado = np.where(
        (dataframe['Volatilidad'] == max_volatilidad_verde) & (dataframe['Color'] == 1),
        1,
        0
    )
    return resultado 

def la_mayor_roja(dataframe):
    # Calcula el valor máximo en 'Volatilidad' donde 'Color' == -1
    max_volatilidad_verde = dataframe[dataframe['Color'] == -1]['Volatilidad'].max()
    
    # Usamos np.where para crear una nueva columna con el resultado
    resultado = np.where(
        (dataframe['Volatilidad'] == max_volatilidad_verde) & (dataframe['Color'] == -1),
        1,
        0
    )
    return resultado 




#############################################################################################
# Definir la función RSI_50bins




def Cierre(imagen_current):
    #Definimos la altura total del df
    altura_max = imagen_current['Precio Máximo'].max()
    altura_min = imagen_current['Precio Mínimo'].min()
    rangoDatos = altura_max - altura_min

    #Definimos altura del precio de apertura
    altura_apertura = imagen_current['Precio de Cierre']
    rango_chico = (altura_apertura-altura_min)

    # Calculamos la altura proporcional
    apertura = (rango_chico/rangoDatos)*100

    apertura = apertura.fillna(0)

    # Ajustar los límites de los 50 bins para evitar que las fronteras se toquen
    bin_edges = [i * (100 / 50) for i in range(51)]  # 51 puntos para 50 intervalos
    bin_edges[0] -= 0.0001  # Ajustar el límite inferior del primer bin
    bin_edges[-1] += 0.0001  # Ajustar el límite superior del último bin

    bin_numbers = list(range(1, 51))  # Números de bin de 1 a 50

    # Asignar cada valor a su bin correspondiente
    apertura_bins = pd.cut(apertura, bins=bin_edges, labels=bin_numbers, include_lowest=True).astype(int)
    
    return apertura_bins





 



################################################################################################################################




def obtenerVolatilidad_Por_Vela(imagen): #
    # Primero sacamos la volatilidad de todo el dataframe 30
    precio_maximo = imagen['Precio Máximo'].max()
    precio_minimo = imagen['Precio Mínimo'].min()
    rangoDatos = precio_maximo - precio_minimo
    Volatilidad_dataframe = (rangoDatos/precio_maximo)*100

    #Obtener tamaño de la vela actual
    vela_actual_largo = imagen['Precio Máximo'] - imagen['Precio Mínimo']
    variacion_vela = (vela_actual_largo / imagen['Precio Máximo'] )

    #Obtener la volatilidad final
    Volatilidad = (variacion_vela / Volatilidad_dataframe)*10000
    return Volatilidad


def obtenerMechaAlta(imagen):
    # Primero sacamos el rango de todo el dataframe
    precio_maximo = imagen['Precio Máximo'].max()
    precio_minimo = imagen['Precio Mínimo'].min()
    rangoDatos = precio_maximo - precio_minimo    

    # Ahora averiguamos si se trata de una vela alcista o bajista. Si el cierre es mayor a la apertura, es vela verde, si no, es roja
    dif_aperturacierre = imagen['Precio de Cierre'] - imagen['Precio de Apertura']

    # Usando operaciones vectorizadas creamos dos posibles mechas. "mecha" es para velas alcistas y "mecha_alternativa" para velas bajistas
    mecha = ((imagen['Precio Máximo'] - imagen['Precio de Cierre']) / rangoDatos) * 100
    mecha_alternativa = ((imagen['Precio Máximo'] - imagen['Precio de Apertura']) / rangoDatos) * 100
    # Asignar valores basados en la condición
    mecha = mecha.where(dif_aperturacierre >= 0, mecha_alternativa)
    # Reemplazar NaNs con 0
    mecha = mecha.fillna(0)

    return mecha


def obtenerMechaBaja(df_total):
    # Primero sacamos el rango de todo el dataframe
    precio_maximo = df_total['Precio Máximo'].max()
    precio_minimo = df_total['Precio Mínimo'].min()
    rangoDatos = precio_maximo - precio_minimo    

    # Ahora averiguamos si se trata de una vela alcista o bajista. Si el cierre es mayor a la apertura, es vela verde, si no, es roja
    dif_aperturacierre = df_total['Precio de Cierre'] - df_total['Precio de Apertura']


    # Usando operaciones vectorizadas
    mecha = ((df_total['Precio de Cierre'] - df_total['Precio Mínimo'])/rangoDatos)*100
    mecha_alternativa = ((df_total['Precio de Apertura'] - df_total['Precio Mínimo'])/rangoDatos)*100  
    # Asignar valores basados en la condición
    mecha = mecha.where(dif_aperturacierre <= 0, mecha_alternativa) 
    # Reemplazar NaNs con 0
    mecha = mecha.fillna(0)
    
    return mecha


def obtenerMechaBaja(df_total):
    # Primero sacamos el rango de todo el dataframe
    precio_maximo = df_total['Precio Máximo'].max()
    precio_minimo = df_total['Precio Mínimo'].min()
    rangoDatos = precio_maximo - precio_minimo    

    # Ahora averiguamos si se trata de una vela alcista o bajista. Si el cierre es mayor a la apertura, es vela verde, si no, es roja
    dif_aperturacierre = df_total['Precio de Cierre'] - df_total['Precio de Apertura']


    # Usando operaciones vectorizadas
    mecha = ((df_total['Precio de Cierre'] - df_total['Precio Mínimo'])/rangoDatos)*100
    mecha_alternativa = ((df_total['Precio de Apertura'] - df_total['Precio Mínimo'])/rangoDatos)*100  
    # Asignar valores basados en la condición
    mecha = mecha.where(dif_aperturacierre <= 0, mecha_alternativa) 
    # Reemplazar NaNs con 0
    mecha = mecha.fillna(0)
    
    return mecha



def obtenerCuerpo(df_total):
    # Primero sacamos el rango de todo el dataframe
    precio_maximo = df_total['Precio Máximo'].max()
    precio_minimo = df_total['Precio Mínimo'].min()
    rangoDatos = precio_maximo - precio_minimo       

    # Ahora averiguamos si se trata de una vela alcista o bajista. Si el cierre es mayor a la apertura, es vela verde, si no, es roja
    dif_aperturacierre = df_total['Precio de Cierre'] - df_total['Precio de Apertura']


    # Usando operaciones vectorizadas
    cuerpoverde = ((df_total['Precio de Cierre'] - df_total['Precio de Apertura']) / rangoDatos) * 100
    cuerporojo = ((df_total['Precio de Apertura'] - df_total['Precio de Cierre']) / rangoDatos) * 100

    # Asignar valores basados en la condición
    cuerpoverde = cuerpoverde.where(dif_aperturacierre >= 0, cuerporojo)

    # Reemplazar NaNs con 0
    cuerpoverde = cuerpoverde.fillna(0)

    return cuerpoverde


def obtenerTamano(df_total):
    # Primero sacamos el rango de todo el dataframe
    precio_maximo = df_total['Precio Máximo'].max()
    precio_minimo = df_total['Precio Mínimo'].min()
    rangoDatos = precio_maximo - precio_minimo 

    # Obtenemos el rango de la vela actual
    dif_aperturacierre = df_total['Precio Máximo'] - df_total['Precio Mínimo']   

    # Obtenemos el porcentaje de la vale actual con respecto a todo el rango
    tamano = (dif_aperturacierre / rangoDatos) * 100   

    return tamano



def pos_open(df_total):
    """
    Asigna un bin (1 a 500) al valor de 'Precio de Apertura' basado en el rango dinámico
    de 'Precio Mínimo' y 'Precio Máximo', asegurando que los límites de los bins no se toquen.
    
    :param df_total: DataFrame con los datos.
    :return: Serie con los bins asignados.
    """
    # Obtener el rango dinámico de los datos
    precio_maximo = df_total['Precio Máximo'].max()
    precio_minimo = df_total['Precio Mínimo'].min()
    rangoDatos = precio_maximo - precio_minimo
    
    # Definir los bordes de los bins (501 puntos para 500 bins)
    bin_edges = [precio_minimo + i * (rangoDatos / 500) for i in range(501)]
    
    # Ajustar los límites de los bins para evitar colisiones
    bin_edges[0] -= 0.0001   # Ajuste del límite inferior
    bin_edges[-1] += 0.0001  # Ajuste del límite superior
    
    # Etiquetas de los bins (1 a 500)
    bin_numbers = list(range(1, 501))

    # Asegurar que los valores están dentro del rango
    df_total['Precio de Apertura'] = df_total['Precio de Apertura'].clip(lower=precio_minimo, upper=precio_maximo)

    # Asignar cada valor al bin correspondiente
    bins_assigned = pd.cut(
        df_total['Precio de Apertura'],  # Columna de datos
        bins=bin_edges,    # Bordes ajustados de los bins
        labels=bin_numbers,  # Etiquetas numéricas de bins
        include_lowest=True,  # Incluir el límite inferior
        right=False  # Evitar que un valor se asigne a dos bins a la vez
    )
    
    # Convertir a enteros y manejar valores NaN
    bins_assigned = bins_assigned.cat.add_categories([0]).fillna(0).astype(int)
    
    return bins_assigned



def pos_close(df_total):
    """
    Asigna un bin (1 a 500) al valor de 'Precio de Apertura' basado en el rango dinámico
    de 'Precio Mínimo' y 'Precio Máximo', asegurando que los límites de los bins no se toquen.
    
    :param df_total: DataFrame con los datos.
    :return: Serie con los bins asignados.
    """
    # Obtener el rango dinámico de los datos
    precio_maximo = df_total['Precio Máximo'].max()
    precio_minimo = df_total['Precio Mínimo'].min()
    rangoDatos = precio_maximo - precio_minimo
    
    # Definir los bordes de los bins (501 puntos para 500 bins)
    bin_edges = [precio_minimo + i * (rangoDatos / 500) for i in range(501)]
    
    # Ajustar los límites de los bins para evitar colisiones
    bin_edges[0] -= 0.0001   # Ajuste del límite inferior
    bin_edges[-1] += 0.0001  # Ajuste del límite superior
    
    # Etiquetas de los bins (1 a 500)
    bin_numbers = list(range(1, 501))

    # Asegurar que los valores están dentro del rango
    df_total['Precio de Cierre'] = df_total['Precio de Cierre'].clip(lower=precio_minimo, upper=precio_maximo)

    # Asignar cada valor al bin correspondiente
    bins_assigned = pd.cut(
        df_total['Precio de Cierre'],  # Columna de datos
        bins=bin_edges,    # Bordes ajustados de los bins
        labels=bin_numbers,  # Etiquetas numéricas de bins
        include_lowest=True,  # Incluir el límite inferior
        right=False  # Evitar que un valor se asigne a dos bins a la vez
    )
    
    # Convertir a enteros y manejar valores NaN
    bins_assigned = bins_assigned.cat.add_categories([0]).fillna(0).astype(int)
    
    return bins_assigned



def pos_high(df_total):
    """
    Asigna un bin (1 a 500) al valor de 'Precio de Apertura' basado en el rango dinámico
    de 'Precio Mínimo' y 'Precio Máximo', asegurando que los límites de los bins no se toquen.
    
    :param df_total: DataFrame con los datos.
    :return: Serie con los bins asignados.
    """
    # Obtener el rango dinámico de los datos
    precio_maximo = df_total['Precio Máximo'].max()
    precio_minimo = df_total['Precio Mínimo'].min()
    rangoDatos = precio_maximo - precio_minimo
    
    # Definir los bordes de los bins (501 puntos para 500 bins)
    bin_edges = [precio_minimo + i * (rangoDatos / 500) for i in range(501)]
    
    # Ajustar los límites de los bins para evitar colisiones
    bin_edges[0] -= 0.0001   # Ajuste del límite inferior
    bin_edges[-1] += 0.0001  # Ajuste del límite superior
    
    # Etiquetas de los bins (1 a 500)
    bin_numbers = list(range(1, 501))

    # Asegurar que los valores están dentro del rango
    df_total['Precio Máximo'] = df_total['Precio Máximo'].clip(lower=precio_minimo, upper=precio_maximo)

    # Asignar cada valor al bin correspondiente
    bins_assigned = pd.cut(
        df_total['Precio Máximo'],  # Columna de datos
        bins=bin_edges,    # Bordes ajustados de los bins
        labels=bin_numbers,  # Etiquetas numéricas de bins
        include_lowest=True,  # Incluir el límite inferior
        right=False  # Evitar que un valor se asigne a dos bins a la vez
    )
    
    # Convertir a enteros y manejar valores NaN
    bins_assigned = bins_assigned.cat.add_categories([0]).fillna(0).astype(int)
    
    return bins_assigned



def pos_low(df_total):
    """
    Asigna un bin (1 a 500) al valor de 'Precio de Apertura' basado en el rango dinámico
    de 'Precio Mínimo' y 'Precio Máximo', asegurando que los límites de los bins no se toquen.
    
    :param df_total: DataFrame con los datos.
    :return: Serie con los bins asignados.
    """
    # Obtener el rango dinámico de los datos
    precio_maximo = df_total['Precio Máximo'].max()
    precio_minimo = df_total['Precio Mínimo'].min()
    rangoDatos = precio_maximo - precio_minimo
    
    # Definir los bordes de los bins (501 puntos para 500 bins)
    bin_edges = [precio_minimo + i * (rangoDatos / 500) for i in range(501)]
    
    # Ajustar los límites de los bins para evitar colisiones
    bin_edges[0] -= 0.0001   # Ajuste del límite inferior
    bin_edges[-1] += 0.0001  # Ajuste del límite superior
    
    # Etiquetas de los bins (1 a 500)
    bin_numbers = list(range(1, 501))

    # Asegurar que los valores están dentro del rango
    df_total['Precio Mínimo'] = df_total['Precio Mínimo'].clip(lower=precio_minimo, upper=precio_maximo)

    # Asignar cada valor al bin correspondiente
    bins_assigned = pd.cut(
        df_total['Precio Mínimo'],  # Columna de datos
        bins=bin_edges,    # Bordes ajustados de los bins
        labels=bin_numbers,  # Etiquetas numéricas de bins
        include_lowest=True,  # Incluir el límite inferior
        right=False  # Evitar que un valor se asigne a dos bins a la vez
    )
    
    # Convertir a enteros y manejar valores NaN
    bins_assigned = bins_assigned.cat.add_categories([0]).fillna(0).astype(int)
    
    return bins_assigned



def pos_MA8(df_total):
    """
    Asigna un bin (1 a 500) al valor de 'Precio de Apertura' basado en el rango dinámico
    de 'Precio Mínimo' y 'Precio Máximo', asegurando que los límites de los bins no se toquen.
    
    :param df_total: DataFrame con los datos.
    :return: Serie con los bins asignados.
    """
    # Obtener el rango dinámico de los datos
    precio_maximo = df_total['Precio Máximo'].max()
    precio_minimo = df_total['Precio Mínimo'].min()
    rangoDatos = precio_maximo - precio_minimo
    
    # Definir los bordes de los bins (501 puntos para 500 bins)
    bin_edges = [precio_minimo + i * (rangoDatos / 500) for i in range(501)]
    
    # Ajustar los límites de los bins para evitar colisiones
    bin_edges[0] -= 0.0001   # Ajuste del límite inferior
    bin_edges[-1] += 0.0001  # Ajuste del límite superior
    
    # Etiquetas de los bins (1 a 500)
    bin_numbers = list(range(1, 501))

    # Asegurar que los valores están dentro del rango
    df_total['SMA8'] = df_total['SMA8'].clip(lower=precio_minimo, upper=precio_maximo)

    # Asignar cada valor al bin correspondiente
    bins_assigned = pd.cut(
        df_total['SMA8'],  # Columna de datos
        bins=bin_edges,    # Bordes ajustados de los bins
        labels=bin_numbers,  # Etiquetas numéricas de bins
        include_lowest=True,  # Incluir el límite inferior
        right=False  # Evitar que un valor se asigne a dos bins a la vez
    )
    
    # Convertir a enteros y manejar valores NaN
    bins_assigned = bins_assigned.cat.add_categories([0]).fillna(0).astype(int)
    
    return bins_assigned



def pos_MA20(df_total):
    """
    Asigna un bin (1 a 500) al valor de 'Precio de Apertura' basado en el rango dinámico
    de 'Precio Mínimo' y 'Precio Máximo', asegurando que los límites de los bins no se toquen.
    
    :param df_total: DataFrame con los datos.
    :return: Serie con los bins asignados.
    """
    # Obtener el rango dinámico de los datos
    precio_maximo = df_total['Precio Máximo'].max()
    precio_minimo = df_total['Precio Mínimo'].min()
    rangoDatos = precio_maximo - precio_minimo
    
    # Definir los bordes de los bins (501 puntos para 500 bins)
    bin_edges = [precio_minimo + i * (rangoDatos / 500) for i in range(501)]
    
    # Ajustar los límites de los bins para evitar colisiones
    bin_edges[0] -= 0.0001   # Ajuste del límite inferior
    bin_edges[-1] += 0.0001  # Ajuste del límite superior
    
    # Etiquetas de los bins (1 a 500)
    bin_numbers = list(range(1, 501))

    # Asegurar que los valores están dentro del rango
    df_total['SMA20'] = df_total['SMA20'].clip(lower=precio_minimo, upper=precio_maximo)

    # Asignar cada valor al bin correspondiente
    bins_assigned = pd.cut(
        df_total['SMA20'],  # Columna de datos
        bins=bin_edges,    # Bordes ajustados de los bins
        labels=bin_numbers,  # Etiquetas numéricas de bins
        include_lowest=True,  # Incluir el límite inferior
        right=False  # Evitar que un valor se asigne a dos bins a la vez
    )
    
    # Convertir a enteros y manejar valores NaN
    bins_assigned = bins_assigned.cat.add_categories([0]).fillna(0).astype(int)
    
    return bins_assigned



def pos_MA100(df_total):
    """
    Asigna un bin (1 a 500) al valor de 'Precio de Apertura' basado en el rango dinámico
    de 'Precio Mínimo' y 'Precio Máximo', asegurando que los límites de los bins no se toquen.
    
    :param df_total: DataFrame con los datos.
    :return: Serie con los bins asignados.
    """
    # Obtener el rango dinámico de los datos
    precio_maximo = df_total['Precio Máximo'].max()
    precio_minimo = df_total['Precio Mínimo'].min()
    rangoDatos = precio_maximo - precio_minimo
    
    # Definir los bordes de los bins (501 puntos para 500 bins)
    bin_edges = [precio_minimo + i * (rangoDatos / 500) for i in range(501)]
    
    # Ajustar los límites de los bins para evitar colisiones
    bin_edges[0] -= 0.0001   # Ajuste del límite inferior
    bin_edges[-1] += 0.0001  # Ajuste del límite superior
    
    # Etiquetas de los bins (1 a 500)
    bin_numbers = list(range(1, 501))

    # Asegurar que los valores están dentro del rango
    df_total['SMA100'] = df_total['SMA100'].clip(lower=precio_minimo, upper=precio_maximo)

    # Asignar cada valor al bin correspondiente
    bins_assigned = pd.cut(
        df_total['SMA100'],  # Columna de datos
        bins=bin_edges,    # Bordes ajustados de los bins
        labels=bin_numbers,  # Etiquetas numéricas de bins
        include_lowest=True,  # Incluir el límite inferior
        right=False  # Evitar que un valor se asigne a dos bins a la vez
    )
    
    # Convertir a enteros y manejar valores NaN
    bins_assigned = bins_assigned.cat.add_categories([0]).fillna(0).astype(int)
    
    return bins_assigned





if __name__ == "__main__":

    # Captura los argumentos
    moneda_seleccionada = sys.argv[1]
    factor = sys.argv[2]  
    # Convertir factor a un número entero
    factor = int(factor)
    
    
    """moneda_seleccionada = "SAND"
    factor = 10000     """
    
    
    # Usar las variables
    #moneda_seleccionada= 'ETH'
    #factor = 10
    #print(f"Moneda seleccionada: {moneda_seleccionada}")
    #print(f"Factor: {factor}") 


    #Lista para iterar sobre los eventos de entrada confirmados
    eventos_confirmados = []

    datos,eventos_confirmados,confirmacion180BUY, confirmacion180SELL, patron_RSI50_Buy, patron_RSI50_Sell, patron_HAMMER_Buy, patron_HAMMER_Sell, patron_DV_Buy, patron_DV_Sell = crearDataFrame(moneda_seleccionada,factor, eventos_confirmados)

    # Guardamos todos los datos en un archivo de CSV
    datos.to_csv(os.path.join(ARCHIVOS_DIR, f'{moneda_seleccionada}Data.csv'), index=False)        


   


    datosLarge = crearDataFrameLARGE(moneda_seleccionada,factor)
    # Guardamos todos los datos en un archivo de CSV
    datosLarge.to_csv(os.path.join(ARCHIVOS_DIR, f'{moneda_seleccionada}Data_Large.csv'), index=False) 

    if eventos_confirmados:  # Se ejecutará solo si la lista no está vacía
        print(f"Los eventos confirmados para {moneda_seleccionada} son: {eventos_confirmados}")
        print("Inicia proceso de análisis...")
        ruta_script2 = os.path.join(PROJECT_ROOT, '2Aplanar', 'Aplanador.py')         
        for evento in eventos_confirmados:           
            if evento == "Toro_180":
                evento_entrada = 0
                try:
                    # Ejecutar el script y pasar las variables moneda_seleccionada y factor como argumentos
                    result_script2 = subprocess.Popen(
                        [sys.executable, ruta_script2, moneda_seleccionada, str(evento_entrada)]
                    )
                    # Esperar a que el script termine de ejecutarse
                    result_script2.wait() 
                    if result_script2.returncode == 1:
                        eventos_confirmados.clear()
                        sys.exit(1) 
                    elif result_script2.returncode == 3:
                        sys.exit(3)                                                   
                except FileNotFoundError:
                    print("El archivo correspondiente a la moneda seleccionada no se encontró.")                
            elif evento == "Oso_180":
                evento_entrada = 1
                try:
                    # Ejecutar el script y pasar las variables moneda_seleccionada y factor como argumentos
                    result_script2 = subprocess.Popen(
                        [sys.executable, ruta_script2, moneda_seleccionada, str(evento_entrada)]
                    )
                    # Esperar a que el script termine de ejecutarse
                    result_script2.wait() 
                    if result_script2.returncode == 1:
                        eventos_confirmados.clear()
                        sys.exit(1) 
                    elif result_script2.returncode == 3:
                        sys.exit(3)                                                   
                except FileNotFoundError:
                    print("El archivo correspondiente a la moneda seleccionada no se encontró.")  
            elif evento == "RSI50_Alcista":
                evento_entrada = 2
                try:
                    # Ejecutar el script y pasar las variables moneda_seleccionada y factor como argumentos
                    result_script2 = subprocess.Popen(
                        [sys.executable, ruta_script2, moneda_seleccionada, str(evento_entrada)]
                    )
                    # Esperar a que el script termine de ejecutarse
                    result_script2.wait() 
                    if result_script2.returncode == 1:
                        eventos_confirmados.clear()
                        sys.exit(1) 
                    elif result_script2.returncode == 3:
                        sys.exit(3)                                                   
                except FileNotFoundError:
                    print("El archivo correspondiente a la moneda seleccionada no se encontró.")  
            elif evento == "RSI50_Bajista":
                evento_entrada = 3
                try:
                    # Ejecutar el script y pasar las variables moneda_seleccionada y factor como argumentos
                    result_script2 = subprocess.Popen(
                        [sys.executable, ruta_script2, moneda_seleccionada, str(evento_entrada)]
                    )
                    # Esperar a que el script termine de ejecutarse
                    result_script2.wait() 
                    if result_script2.returncode == 1:
                        eventos_confirmados.clear()
                        sys.exit(1) 
                    elif result_script2.returncode == 3:
                        sys.exit(3)                                                   
                except FileNotFoundError:
                    print("El archivo correspondiente a la moneda seleccionada no se encontró.")      
            elif evento == "HAMMER_Alcista":
                evento_entrada = 4
                try:
                    # Ejecutar el script y pasar las variables moneda_seleccionada y factor como argumentos
                    result_script2 = subprocess.Popen(
                        [sys.executable, ruta_script2, moneda_seleccionada, str(evento_entrada)]
                    )
                    # Esperar a que el script termine de ejecutarse
                    result_script2.wait() 
                    if result_script2.returncode == 1:
                        eventos_confirmados.clear()
                        sys.exit(1) 
                    elif result_script2.returncode == 3:
                        sys.exit(3)                                                   
                except FileNotFoundError:
                    print("El archivo correspondiente a la moneda seleccionada no se encontró.")  
            elif evento == "HAMMER_Bajista":
                evento_entrada = 5
                try:
                    # Ejecutar el script y pasar las variables moneda_seleccionada y factor como argumentos
                    result_script2 = subprocess.Popen(
                        [sys.executable, ruta_script2, moneda_seleccionada, str(evento_entrada)]
                    )
                    # Esperar a que el script termine de ejecutarse
                    result_script2.wait() 
                    if result_script2.returncode == 1:
                        eventos_confirmados.clear()
                        sys.exit(1) 
                    elif result_script2.returncode == 3:
                        sys.exit(3)                                                   
                except FileNotFoundError:
                    print("El archivo correspondiente a la moneda seleccionada no se encontró.")   
#
            elif evento == "DV_Alcista":
                evento_entrada = 7
                try:
                    # Ejecutar el script y pasar las variables moneda_seleccionada y factor como argumentos
                    result_script2 = subprocess.Popen(
                        [sys.executable, ruta_script2, moneda_seleccionada, str(evento_entrada)]
                    )
                    # Esperar a que el script termine de ejecutarse
                    result_script2.wait() 
                    if result_script2.returncode == 1:
                        eventos_confirmados.clear()
                        sys.exit(1) 
                    elif result_script2.returncode == 3:
                        sys.exit(3)                                                   
                except FileNotFoundError:
                    print("El archivo correspondiente a la moneda seleccionada no se encontró.")  
            elif evento == "DV_Bajista":
                evento_entrada = 8
                try:
                    # Ejecutar el script y pasar las variables moneda_seleccionada y factor como argumentos
                    result_script2 = subprocess.Popen(
                        [sys.executable, ruta_script2, moneda_seleccionada, str(evento_entrada)]
                    )
                    # Esperar a que el script termine de ejecutarse
                    result_script2.wait() 
                    if result_script2.returncode == 1:
                        eventos_confirmados.clear()
                        sys.exit(1) 
                    elif result_script2.returncode == 3:
                        sys.exit(3)                                                   
                except FileNotFoundError:
                    print("El archivo correspondiente a la moneda seleccionada no se encontró.") 
    else:
        print("No se detectó ningun evento de entrada para analizar.")