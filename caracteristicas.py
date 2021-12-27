#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 27 11:52:10 2021

@author: Ruben Girela Castellón
"""

import os
import json
import numpy as np
#import time

def calculaCaracteristicas(files):
    
    #inicio = time.time()
    # mostramos el directorio de trabajo y vemos si existe el dir para salvar los datos
    print("Directorio de trabajo es: ", os.getcwd())
    
    #guardara los clusters con resultados positivos y negativos
    clustersPositivos = []
    clustersNegativos = []
    
    #esto es para diferenciar los archivos con resultados positivos y negativos
    first = True
    
    for file in files:
        #leemos el fichero json
        with open(file, 'r') as f:
         for line in f:
             
             if(first):
                 #y guardamos su contenido
                 clustersPositivos.append(json.loads(line))
             else:
                 #y guardamos su contenido
                 clustersNegativos.append(json.loads(line))
         
        first = False
        
    print(f'positivos: {len(clustersPositivos)} negativos: {len(clustersNegativos)}')
    
    #generamos los archivos .dat
    generaJsonPerimetroProfundidadAnchura(clustersPositivos, True)
    generaJsonPerimetroProfundidadAnchura(clustersNegativos, False)
    
    #generamos el csv que contiene todos los casos positivos y negativos
    generaCSVAll()
    
    #tiempo = time.time() - inicio
    #print('Elapse: ',tiempo)

#función que genera el CSV con todos los datos positivos y negativos
def generaCSVAll():
    files = ['resultados/caracteristicasNoPiernas.dat', 'resultados/caracteristicasPiernas.dat']
    
    #guardo la informacion que necesitamos en un nuevo csv
    fcsv=open("resultados/piernasDataset.csv", "w",encoding="utf8")
    
    #recorro los archivos .dat
    for file in files:
        with open(file,'r') as f:
            for line in f:#leo su contenido
                
                #lo transformo en diccionario
                cluster = json.loads(line)
                
                #creo el formato para el csv
                formato = str(cluster['perimetro'])+';'+str(cluster['profundidad'])+';'+str(cluster['anchura'])+';'+str(cluster['esPierna'])
                #y añado los datos en formato csv
                fcsv.write(formato+'\n')
                
    fcsv.close()

#función que genera los archivos .dat con los datos calculados (profundidad, anchura y perimetro)
def generaJsonPerimetroProfundidadAnchura(clusteres, pierna):
    
    file = 'resultados/caracteristicasNoPiernas.dat'
    p = 0
    
    if(pierna):
        file = 'resultados/caracteristicasPiernas.dat'        
        p=1
        
    #reeditamos o creamos el archivo .dat
    fichero=open(file, "w")
    
    #recorremos los clusters
    for cluster in clusteres:
        
        #calcula la anchura y el perimetro del cluster
        perimetro, anchura = calculaPerimetroYAnchura(cluster)
        
        #print('Perimetro:',perimetro)
        #print('Anchura:',anchura)
        
        #obtenemos la ecuación para calcular la profundidad de un punto con respecto a una recta
        profundidad = calculaProfundidad(
            cluster['PuntosX'][0], 
            cluster['PuntosY'][0], 
            cluster['PuntosX'][-1], 
            cluster['PuntosY'][-1])
        
        #guardara la máxima profundidad    
        max_prof = max([
        profundidad(cluster['PuntosX'][i], cluster['PuntosY'][i]) 
        for i in np.arange(len(cluster['PuntosY']))
        ])
     
        #print(f"Maxima Profundidad = {max_prof}")
        
        #guardamos el perimetro, anchura, profundidad y si es pierna o no
        fichero.write(
            json.dumps({
                'numero_cluster':cluster['numero_cluster'], 
                'perimetro':perimetro, 
                'profundidad':max_prof, 
                'anchura':anchura, 
                'esPierna':p})
            +'\n')
        
    fichero.close()
 
#función que calcula el perimetro y la anchura de un cluster
def calculaPerimetroYAnchura(cluster):
     
    #calculamos el perimetro
    suma_distancias = 0
    
    #distancia = sqrt((x1-x2)²+(y1-y2)²)
    for i in np.arange(len(cluster['PuntosX'])-1):
        
        sumasX = np.power(cluster['PuntosX'][i]-cluster['PuntosX'][i+1],2)
        sumasY = np.power(cluster['PuntosY'][i]-cluster['PuntosY'][i+1],2)
        
        suma_distancias += np.sqrt(sumasX+sumasY)
    
    #calculamos la anchura
    sumasX = np.power(cluster['PuntosX'][0]-cluster['PuntosX'][-1],2)
    sumasY = np.power(cluster['PuntosY'][0]-cluster['PuntosY'][-1],2)
        
    anchura = np.sqrt(sumasX+sumasY)
    
    return suma_distancias, anchura
    
 #función que devuelve la ecuación para calcular la profundidad de un punto con respecto a una recta
def calculaProfundidad(x1,y1,x2,y2):
    
    """
    Para calcular la profundidad de un punto con respecto a una recta necesitamos
    saber la ecuación de dicha recta:
        y = m*x + n;    m*x - y + n = 0
    pero necesitamos para obtener la ecuación la pendiente y el punto donde 
    corta la recta con el eje y:
        
        (Pendiente) m = (y2 - y1)/(x2 - x1)
        
        (punto donde corta la recta con el eje y) 
        n = y - m * (x - 0) = y - m*x
        
    información obtenida de:
        http://es.onlinemschool.com/math/assistance/cartesian_coordinate/p_line1/
        https://es.m.wikipedia.org/wiki/Distancia_de_un_punto_a_una_recta
        
    Para la comprobación:
        https://www.wolframalpha.com/widgets/view.jsp?id=4c74dcfeac90df69aed5c8a90125e696
    """
    
    #calculamos la pendiente de dicha recta
    pendiente = (y2-y1)/(x2-x1)
    
    #calculamos el punto donde corta la recta con el eje y
    punto_rec = y2 - (pendiente*x2)
    
    #calculamos la ecuación de la recta
    recta = lambda x, y: pendiente*x-y+punto_rec
    """
    print('-------------------------------------------------------------------')
    print(f"x2={x2}, y2={y2}")
    print(f"x1={x1}, y1={y1}")
    print(f'Pendiente = {pendiente}')
    print(f'Punto que corta la recta con el eje y = {punto_rec}')
    """
    
    """
    Para calcular la distancia del punto con respecto a la recta:
        d(P,r) = |(m*x - y + n)/sqrt(m²+1)|
    """
    #ya obtenida la recta calculamos la profundidad del punto con respecto a la recta
    return lambda x, y: np.abs(recta(x,y)/np.sqrt(np.power(pendiente,2)+1))