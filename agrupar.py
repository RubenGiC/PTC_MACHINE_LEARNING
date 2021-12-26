#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 25 20:12:48 2021

@author: Ruben Girela Castellón
"""

import json
import os
import numpy as np

#función que agrupa en clusters los resultados usando el algoritmo (agrupación por distancia de salto)
def agruparDatos(minimo, maximo, umbral, files):
    
    # mostramos el directorio de trabajo y vemos si existe el dir para salvar los datos
    print("Directorio de trabajo es: ", os.getcwd())
    
    #guardaremos los resultados obtenidos del json positivos y negativos
    resultadosPositivos=[]
    resultadosNegativos=[]
    
    for file in files[:6]:
        first = True
        #leemos el fichero json
        with open(file, 'r') as f:
         for line in f:
             
             if(not first):
                 #y guardamos su contenido
                 resultadosPositivos.append(json.loads(line))
            
             first = False
     
    for file in files[6:]:
        first = True
        #leemos el fichero json
        with open(file, 'r') as f:
         for line in f:
             
             if(not first):
                 #y guardamos su contenido
                 resultadosNegativos.append(json.loads(line))
             first = False
         
     #print(resultados)
        
    #guardaremos los clusters
    n_clustersPositivos = 0
    #indicador del cluster
    n_cluster = 1
    
    #cluster que guardara los puntos en el eje X
    PuntosX = []
    #cluster que guardara los puntos en el eje Y
    PuntosY = []
    
    #guardara la distancia entre 2 puntos
    distancia = -1
    
    #accedo o creo el archivo json para guardar los clusters
    ficheroPiernas=open('resultados/clustersPiernas.json', "w")
    
    #recorremos los datos positivos
    for dato in resultadosPositivos[1:]:
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
                
            else:#en caso contrario
                """
                guardo una copia del cluster si llega a un numero minimo de puntos 
                """
                if(len(PuntosX)>=minimo):
                    n_clustersPositivos += 1
                    ficheroPiernas.write(json.dumps({'numero_cluster':n_cluster,'numero_puntos':len(PuntosX), 'PuntosX':PuntosX.copy(), 'PuntosY':PuntosY.copy()})+'\n')
                    
                #y reseteo los valores para el nuevo cluster
                n_cluster += 1
                PuntosX=[dato['PuntosX'][i]]
                PuntosY=[dato['PuntosY'][i]]
                distancia = -1
            #print('X=',dato['PuntosX'][i],'Y=',dato['PuntosY'][i])
        
        #fin = True
    
    ficheroPiernas.close()
    
    #guardaremos los clusters
    n_clustersNegativos = 0
    #indicador del cluster
    n_cluster = 1
    
    #cluster que guardara los puntos en el eje X
    PuntosX = []
    #cluster que guardara los puntos en el eje Y
    PuntosY = []
    
    #guardara la distancia entre 2 puntos
    distancia = -1
    
    #accedo o creo el archivo json para guardar los clusters
    ficheroNoPiernas=open('resultados/clustersNoPiernas.json', "w")
        
    #recorremos los datos negativos
    for dato in resultadosNegativos[1:]:
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
                
            else:#en caso contrario
                """
                guardo una copia del cluster si llega a un numero minimo de puntos 
                """
                if(len(PuntosX)>=minimo):
                    n_clustersNegativos += 1
                    #guardo el cluster tambien en el json
                    ficheroNoPiernas.write(json.dumps({'numero_cluster':n_cluster,'numero_puntos':len(PuntosX), 'PuntosX':PuntosX.copy(), 'PuntosY':PuntosY.copy()})+'\n')
                    
                #y reseteo los valores para el nuevo cluster
                n_cluster += 1
                PuntosX=[dato['PuntosX'][i]]
                PuntosY=[dato['PuntosY'][i]]
                distancia = -1
       
    ficheroNoPiernas.close()
    
    """
    print(clustersPositivos[0])
    print('----------------------------------------------------------------')
    print(clustersPositivos[1])
    """
    
    print('Numero clusters positivos:',n_clustersPositivos)
    print('Numero clusters negativos:',n_clustersNegativos)
    
    return True