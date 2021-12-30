#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 25 20:12:48 2021

@author: Ruben Girela Castellón
"""

import json
import os
import numpy as np

from funciones_globales import leerJson

#función que agrupa en clusters los resultados usando el algoritmo (agrupación por distancia de salto)
def agruparDatos(minimo, maximo, umbral, files, test=False):
    
    # mostramos el directorio de trabajo y vemos si existe el dir para salvar los datos
    #print("Directorio de trabajo es: ", os.getcwd())
    
    #si es el modo predecir
    if(test):
        resultadosTest = leerJson(files, del_first_line = True)
        
        n_clusters = clustersJson('resultados/prediccion/clustersTest.json', resultadosTest, maximo, minimo, umbral)
        print('Numero de clusters Test:',n_clusters)
        
        #si estan vacios los clusters no ha podido agrupar los datos
        if(n_clusters == 0):
            return False
    else:
        #guardaremos los resultados obtenidos del json positivos y negativos
        resultadosPositivos=leerJson(files[:6], del_first_line = True)
        resultadosNegativos=leerJson(files[6:], del_first_line = True)
        
        n_clustersPositivos = clustersJson('resultados/clustersPiernas.json', resultadosPositivos, maximo, minimo, umbral)
        n_clustersNegativos = clustersJson('resultados/clustersNoPiernas.json', resultadosNegativos, maximo, minimo, umbral)
    
        print('Numero clusters positivos:',n_clustersPositivos)
        print('Numero clusters negativos:',n_clustersNegativos)
        
        #si estan vacios los clusters no ha podido agrupar los datos
        if(n_clustersPositivos ==0 or n_clustersNegativos == 0):
            return False
    
    return True

def clustersJson(path, resultados, maximo, minimo, umbral):
    
    #guardaremos los clusters
    n_clusters_total = 0
    #indicador del cluster
    n_cluster = 1
    
    #cluster que guardara los puntos en el eje X
    PuntosX = []
    #cluster que guardara los puntos en el eje Y
    PuntosY = []
    
    #guardara la distancia entre 2 puntos
    distancia = -1
    
    try:
        #accedo o creo el archivo json para guardar los clusters
        fichero=open(path, "w")
        
        #esto se hace para el ultimo cluster que no se comprueba
        ultimo = False
        
        #recorremos los datos positivos
        for dato in resultados:
            for i in np.arange(len(dato['PuntosX'])):
                
                """
                Si el cluster tiene al menos 1 punto calculamos la distancia:
                    distancia = sqrt((x1-x2)²+(y1-y2)²)
                
                siendo (x1,y1) el ultimo punto guardado en el cluster y (x2,y2) el
                nuevo punto a meter
                """
                if(len(PuntosX)>0):
                    sumasX = np.power(PuntosX[-1]-dato['PuntosX'][i],2)
                    sumasY = np.power(PuntosY[-1]-dato['PuntosY'][i],2)
                    distancia = np.sqrt(sumasX+sumasY)
                
                """
                if(not fin):
                    
                    print('x:',dato['PuntosX'][i])
                    print('y',dato['PuntosY'][i])
                    if(len(PuntosX)>0):
                        print('distancia:',distancia)
                """
                    
                #si no supera el numero maximo de puntos un cluster y la distancia no supera el umbral
                if(len(PuntosX)<maximo and distancia<umbral):
                    #guardo ese nuevo punto en el cluster
                    PuntosX.append(dato['PuntosX'][i])
                    PuntosY.append(dato['PuntosY'][i])
                    ultimo = True
                    
                else:#en caso contrario
                    '''
                    print('PUNTOS X')
                    print(PuntosX)
                    print('PUNTOS Y')
                    print(PuntosY)
                    '''
                    """
                    guardo una copia del cluster si llega a un numero minimo de puntos 
                    """
                    if(len(PuntosX)>=minimo):
                        n_clusters_total += 1
                        fichero.write(json.dumps({'numero_cluster':n_cluster,'numero_puntos':len(PuntosX), 'PuntosX':PuntosX.copy(), 'PuntosY':PuntosY.copy()})+'\n')
                        ultimo = False
                        
                    #y reseteo los valores para el nuevo cluster
                    n_cluster += 1
                    PuntosX=[dato['PuntosX'][i]]
                    PuntosY=[dato['PuntosY'][i]]
                    distancia = -1
                #print('X=',dato['PuntosX'][i],'Y=',dato['PuntosY'][i])
            
            #fin = True
            
        if(ultimo and len(PuntosX)>=minimo):
            n_clusters_total += 1
            fichero.write(json.dumps({'numero_cluster':n_cluster,'numero_puntos':len(PuntosX), 'PuntosX':PuntosX.copy(), 'PuntosY':PuntosY.copy()})+'\n')
        
        fichero.close()
        
        """
        print(clusters[0])
        print('----------------------------------------------------------------')
        print(clusters[1])
        """
    
    except FileNotFoundError:
        print('Error el archivo',path,'no se ha encontrado')
    except Exception:
        print('Error el archivo',path,' no se ha podido abrir')
    
    return n_clusters_total
    