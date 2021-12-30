#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 13:43:01 2021

@author: Ruben Girela Castellón
"""

import pandas as pd

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.svm import SVC

import matplotlib.pyplot as plt

#importamos el filtro de warnings
from warnings import simplefilter
#ignuramos todos los futuros warnings
simplefilter(action='ignore', category=FutureWarning)
simplefilter(action='ignore', category=DeprecationWarning)

from captura import capturarDirecto
from agrupar import agruparDatos
from caracteristicas import calculaCaracteristicas
from funciones_globales import leerJson
from clasificarSVM import clasificadorFinal

import numpy as np

#función que entrena el modelo y predice nuevos datos
def modelo(clientID, minimo, maximo, umbral):

    # Asignamos el numero de las columnas de nuestro conjunto de datos
    colnames = ['perimetro', 'profundidad', 'anchura', 'esPierna']

    try:
        """
        cargamos los datos, por defecto el separador es con (,), asi que lo he 
        cambiado por (;) que es como genera mi csv en caracteristicas.py
        """
        dataset = pd.read_csv("resultados/piernasDataset.csv", names=colnames, sep=';') 
        
        #separamos por un lado los datos y por otro las etiquetas
        x = dataset.drop('esPierna', axis=1)
        y = dataset['esPierna']
        
        '''
        Dividimos el conjunto de entrenamiento y de prueba de forma aleatoria
        con random_state fijamos la semmilla del generador aleatorio para que no
        vayan cambiando los resultados entre una ejecución y otra
        '''
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.20, random_state=25)
        
        print('CLASIFICADOR FINAL (RBF)********************************************')
        
        #Aplicamos el KERNEL RADIAL
        '''
        Parámetros modificados
        
        C: por defecto vale 1.0. Penaliza el error de clasificación de los ejemplos,
           a mayor valor más se ajusta al conjunto de ejemplos. Experimentando le he
           puesto 1000000 ya que viendo obtengo un mayor porcentaje de aciertos
        gamma: por defecto scale = 1/ (num_características * X.var()).
            Una valor grande genera muchos conjuntos de radios pequeños, un valor 
            mas pequeño muchos conjuntos de radios grandes
        '''
        print("Clasificación con kernek de base radial con C=1000000 y gamma=scale")
        svcRBF =clasificadorFinal(x_train, y_train)
        
        #predice el conjunto test
        y_pred = svcRBF.predict(x_test)
        #y calculamos el numero de aciertos que acierta
        acc_test = accuracy_score(y_test, y_pred)
        
        print("Acc_test RBF: (TP+TN)/(T+P)  %0.4f" % acc_test)
        
        print("Matriz de confusión Filas: verdad Columnas: predicción")
        '''
         Cij observaciones que son de clase i pero que se predicen a la clase j.
         La suma por filas son los ejemplos reales que hay de cada clase=soporte.
        ( TN	FP 
          FN	TP )
        '''
        
        #calculamos la matriz de confusión
        cm = confusion_matrix(y_test, y_pred)
        
        #dibujamos la matriz
        '''
        labels = ['No pierna', 'Pierna']
        fig = plt.figure()
        ax = fig.add_subplot(111)
        cax = ax.matshow(cm)
        plt.title('Confusion matrix of the classifier')
        fig.colorbar(cax)
        ax.set_xticklabels([''] + labels)
        ax.set_yticklabels([''] + labels)
        plt.xlabel('Predicted')
        plt.ylabel('True')
        plt.show()
        '''
        
        print(cm)
        
        '''
        La precisión mide la capacidad del clasificador en no etiquetar como positivo un ejemplo que es negativo.
        El recall mide la capacidad del clasificador para encontrar todos los ejemplos positivos.
        '''
        
        print("Precision= TP / (TP + FP), Recall= TP / (TP + FN)")
        print("f1-score es la media entre precisión y recall")
        print(classification_report(y_test, y_pred))
        
        #capturamos los datos del robot
        seguir= capturarDirecto('resultados/prediccion/test.json', clientID)
        
        #si ha ido bien agrupa los datos en clusteres
        if(seguir):
            seguir = agruparDatos(minimo, maximo, umbral, ['resultados/prediccion/test.json'], True)
        else:
            print('Error en capturar los datos')
            
        #si ha ido bien extrae las caracteristicas
        if(seguir):
            seguir = calculaCaracteristicas(['resultados/prediccion/clustersTest.json'], True)
        else:
            print('Error en agrupar los datos')
            
        if(seguir):#si ha ido bien predice dichos datos nuevos
            
            # Asignamos el numero de las columnas de nuestro conjunto de datos
            colnames = ['perimetro', 'profundidad', 'anchura']
        
            """
            cargamos los datos, por defecto el separador es con (,), asi que lo he 
            cambiado por (;) que es como genera mi csv en caracteristicas.py
            """
            dataset = pd.read_csv("resultados/prediccion/dataset.csv", names=colnames, sep=';') 
            
            print('datos X')
            print(dataset)
            
            #predice el conjunto test
            y_pred = svcRBF.predict(dataset)
            
            print('Predicción: ')
            print(y_pred)
            
            #obtengo los clusters para clasificarlos
            clusteres = leerJson(['resultados/prediccion/clustersTest.json'])
            
            #almacenare los centroides de cada 2 objetos iguales o 1 objeto igual (si es un cilindro)
            piernas = {'x':[], 'y':[]}
            nopiernas = {'x':[], 'y':[]}
            centroides = {'x':[], 'y':[]}
            
            #umbral de distancia entre 2 objetos (2 piernas o 2 cilindros)
            umb = 0.39
            
            #recorremos todos los clusters
            for i in np.arange(len(y_pred)):
                   
                #si la posicion es > 0, es decir de 1 para arriba
                if(i>0):
                    #recorro las posiciones 0 hasta n-1
                    for e in np.arange(i):
                        #comparo si la predicción es igual (2 piernas o 2 cilindros)
                        if(y_pred[i] == y_pred[e]):
                            #si lo son calculo su distancia
                            sumasX = np.power(clusteres[e]['PuntosX'][-1]-clusteres[i]['PuntosX'][0],2)
                            sumasY = np.power(clusteres[e]['PuntosY'][-1]-clusteres[i]['PuntosY'][0],2)
                            distancia = np.sqrt(sumasX+sumasY)
                            
                            #si la discancia es <= al umbral (0.39)
                            if(distancia <= umb):
                                print('¿pierna (1 si)?', y_pred[i])
                                print('Posiciones: ',e, i)
                                print('distancias:',distancia)
                                
                                #calculo el centro de ambos clusteres en X e Y
                                
                                centroide1 = (clusteres[e]['PuntosX'][0]+clusteres[e]['PuntosX'][-1])/2
                                centroide2 = (clusteres[i]['PuntosX'][0]+clusteres[i]['PuntosX'][-1])/2
                                
                                print('centroide X: (',centroide1,'-',centroide2,')/2 =',(centroide1+centroide2)/2)
                                
                                centroides['x'].append((centroide1+centroide2)/2)
                                
                                centroide1 = (clusteres[e]['PuntosY'][0]+clusteres[e]['PuntosY'][-1])/2
                                centroide2 = (clusteres[i]['PuntosY'][0]+clusteres[i]['PuntosY'][-1])/2
                                
                                print('centroide Y: (',centroide1,'-',centroide2,')/2 =',(centroide1+centroide2)/2)
                                
                                centroides['y'].append((centroide1 + centroide2)/2)
                
                #separo los clusters que son piernas de las que no son piernas
                if(y_pred[i]==1):
                    piernas['x'] += clusteres[i]['PuntosX']
                    piernas['y'] += clusteres[i]['PuntosY']
                else:
                    nopiernas['x'] += clusteres[i]['PuntosX']
                    nopiernas['y'] += clusteres[i]['PuntosY']
                
            '''
            #imprimo los puntos que son piernas y no piernas
            print('Piernas:')
            print(piernas)
            print('No Piernas:')
            print(nopiernas)
            '''
            try:
                #pinto los puntos obtenidos
                plt.clf()    
                plt.scatter(piernas['x'], piernas['y'], c='red', s=5.0)
                plt.scatter(nopiernas['x'], nopiernas['y'], c='blue', s=5.0)
                plt.scatter(centroides['x'], centroides['y'], c='green', s=5.0)
                plt.legend(['Piernas', 'No piernas'])
                #plt.savefig("resultados/prediccion/predecido.jpg")
                plt.savefig("resultados/prediccion/predecido.jpg")
            except Exception:
                print('Error no se ha podido crear la grafica resultados/prediccion/predecido.jpg')
                return False
                
    except Exception:
        print('Error al abrir el archivo resultados/piernas.csv')
        return False
        
    return True

