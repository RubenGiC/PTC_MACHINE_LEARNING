#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 16:29:12 2021

@author: Ruben Girela Castellón
"""

import pandas as pd

from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.svm import SVC

import time

#importamos el filtro de warnings
from warnings import simplefilter
#ignuramos todos los futuros warnings
simplefilter(action='ignore', category=FutureWarning)
simplefilter(action='ignore', category=DeprecationWarning)

def clasificadorSVM():

    # Asignamos el numero de las columnas de nuestro conjunto de datos
    colnames = ['perimetro', 'profundidad', 'anchura', 'esPierna']

    """
    cargamos los datos, por defecto el separador es con (,), asi que lo he 
    cambiado por (;) que es como genera mi csv en caracteristicas.py
    """
    dataset = pd.read_csv("resultados/piernasDataset.csv", names=colnames, sep=';') 

    print(dataset)
    
    x = dataset.drop('esPierna', axis=1)
    y = dataset['esPierna']
    
    '''
    Dividimos el conjunto de entrenamiento y de prueba de forma aleatoria
    con random_state fijamos la semmilla del generador aleatorio para que no
    vayan cambiando los resultados entre una ejecución y otra
    '''
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.20, random_state=25)
    
    print('size training:',len(y_train))
    print('size test:',len(y_test))
    
    #buscador(x_train, x_test, y_train, y_test, x, y, 'poly')
    #buscador(x_train, x_test, y_train, y_test, x, y, 'rbf')
    comparacion(x_train, x_test, y_train, y_test, x, y)
    
    
    #Aplicamos el KERNEL RADIAL
    '''
    Parámetros modificados
    
    C: por defecto vale 1.0. Penaliza el error de clasificación de los ejemplos,
       a mayor valor más se ajusta al conjunto de ejemplos.
    gamma: por defecto auto = 1/ num_características
        inversa del tamaño del "radio" del kernel. Una valor grande genera muchos
        conjuntos de radios pequeños, un valor mas pequeño muchos conjuntos de radios grandes
    '''
    print("Clasificación con kernek de base radial con C=1 y gamma=auto")
    #0.9767
    svcRBF = SVC(kernel='rbf', C=1000000)  #creamos el clasificador
    svcRBF.fit(x_train, y_train) #y entrenamos con los datos training
    
    y_pred = svcRBF.predict(x_test)
    acc_test = accuracy_score(y_test, y_pred)
    
    print("Acc_test RBF: (TP+TN)/(T+P)  %0.4f" % acc_test)
    
    print("Matriz de confusión Filas: verdad Columnas: predicción")
    '''
     Cij observaciones que son de clase i pero que se predicen a la clase j.
     La suma por filas son los ejemplos reales que hay de cada clase=soporte.
    ( TN	FP 
      FN	TP )
    '''
    print(confusion_matrix(y_test, y_pred))
    
    '''
    La precisión mide la capacidad del clasificador en no etiquetar como positivo un ejemplo que es negativo.
    El recall mide la capacidad del clasificador para encontrar todos los ejemplos positivos.
    '''
    
    print("Precision= TP / (TP + FP), Recall= TP / (TP + FN)")
    print("f1-score es la media entre precisión y recall")
    print(classification_report(y_test, y_pred))
    
    #para comprobar de que el resultado no depende del conjunto test elegido
    #realizare validación cruzada
    svcRBF2 = SVC(kernel='rbf', C=1000000)  #creamos el clasificador
    scores = cross_val_score(svcRBF2, x, y, cv=5)
    
    # exactitud media con intervalo de confianza del 95%
    print("Accuracy 5-cross validation: %0.4f (+/- %0.4f)" % (scores.mean(), scores.std() * 2))
    
    return True


def buscador(x_train, x_test, y_train, y_test, x, y, k):
    
    if(k=='poly'):
        """
        param_grid={'C':[1,10,100,1000],
                'gamma': [0.001, 0.005, 0.01, 0.1, 'scale'],
                'degree': [3, 4, 5, 6]}
        """
        param_grid={'C':[1, 10],
                'gamma': ['scale'],
                'degree': [4, 5]}
    else:
        param_grid={'C':[10000, 100000, 1000000, 10000000],
            'gamma': [0.001, 0.005, 0.01, 0.1, 'scale', 'auto']}
    
    print("Búsqueda de parámetros en un rango en el caso de "+k)
    
    gscv = GridSearchCV(SVC(kernel=k, class_weight='balanced'), param_grid)
    
    gscv = gscv.fit(x_train, y_train)
    
    print('Mejor estimador encontrado:')
    
    rbf_best = gscv.best_estimator_
    
    print(rbf_best)
    
    #calculamos la predicción
    y_pred = rbf_best.predict(x_test)
    
    acc_test = accuracy_score(y_test, y_pred)
    print("Acc_test: (TP+TN)/(T+P)  %0.4f" % acc_test)
    
    print("Matriz de confusión Filas: verdad Columnas: predicción")
    '''
     Cij observacions que son de clase i pero que se predicen a la clase j.
     La suma por filas son los ejemplos reales que hay de cada clase=soporte.
    ( TN	FP 
      FN	TP )
    '''
    
    print(confusion_matrix(y_test, y_pred))
    
    '''
    La precisión mide la capacidad del clasificador en no etiquetar como positivo un ejemplo que es negativo.
    El recall mide la capacidad del clasificador para encontrar todos los ejemplos positivos.
    '''
    
    print("Precision= TP / (TP + FP), Recall= TP / (TP + FN)")
    print("f1-score es la media entre precisión y recall")
    print(classification_report(y_test, y_pred))
    

def comparacion(x_train, x_test, y_train, y_test, x, y):
        
    print('**************************RBF**************************************')
    inicio = time.time()
    rbf(x_train, x_test, y_train, y_test, x, y)
    print('Tiempo:',(time.time()-inicio))
    inicio = time.time()
    print('**************************POLY*************************************')
    poly(x_train, x_test, y_train, y_test, x, y)
    print('Tiempo:',(time.time()-inicio))
    print('*******************************************************************')
    

def rbf(x_train, x_test, y_train, y_test, x, y):
    
    print("Clasificación con kernek de base radial con C=1 y gamma=auto")
    svcRBF = SVC(kernel='rbf', C=1000000)  #creamos el clasificador
    svcRBF.fit(x_train, y_train) #y entrenamos con los datos training
    
    y_pred = svcRBF.predict(x_test)
    acc_test = accuracy_score(y_test, y_pred)
    
    print("Acc_test RBF: (TP+TN)/(T+P)  %0.4f" % acc_test)
    
    print("Matriz de confusión Filas: verdad Columnas: predicción")
    '''
     Cij observaciones que son de clase i pero que se predicen a la clase j.
     La suma por filas son los ejemplos reales que hay de cada clase=soporte.
    ( TN	FP 
      FN	TP )
    '''
    print(confusion_matrix(y_test, y_pred))
    
    '''
    La precisión mide la capacidad del clasificador en no etiquetar como positivo un ejemplo que es negativo.
    El recall mide la capacidad del clasificador para encontrar todos los ejemplos positivos.
    '''
    
    print("Precision= TP / (TP + FP), Recall= TP / (TP + FN)")
    print("f1-score es la media entre precisión y recall")
    print(classification_report(y_test, y_pred))
    
    #para comprobar de que el resultado no depende del conjunto test elegido
    #realizare validación cruzada
    #0.8413 (+/- 0.1243
    svcRBF2 = SVC(kernel='rbf')  #creamos el clasificador
    scores = cross_val_score(svcRBF2, x, y, cv=5)
    
    # exactitud media con intervalo de confianza del 95%
    print("Accuracy 5-cross validation: %0.4f (+/- %0.4f)" % (scores.mean(), scores.std() * 2))
    
def poly(x_train, x_test, y_train, y_test, x, y):
    print("Clasificación con kernek de base radial con C=1 y gamma=auto")
    #0.6884
    svcP = SVC(kernel='poly', degree=5, C=10)  #creamos el clasificador
    svcP.fit(x_train, y_train) #y entrenamos con los datos training
    
    y_pred = svcP.predict(x_test)
    acc_test = accuracy_score(y_test, y_pred)
    
    print("Acc_test P: (TP+TN)/(T+P)  %0.4f" % acc_test)
    
    print("Matriz de confusión Filas: verdad Columnas: predicción")
    '''
     Cij observaciones que son de clase i pero que se predicen a la clase j.
     La suma por filas son los ejemplos reales que hay de cada clase=soporte.
    ( TN	FP 
      FN	TP )
    '''
    print(confusion_matrix(y_test, y_pred))
    
    '''
    La precisión mide la capacidad del clasificador en no etiquetar como positivo un ejemplo que es negativo.
    El recall mide la capacidad del clasificador para encontrar todos los ejemplos positivos.
    '''
    
    print("Precision= TP / (TP + FP), Recall= TP / (TP + FN)")
    print("f1-score es la media entre precisión y recall")
    print(classification_report(y_test, y_pred))
    
    #para comprobar de que el resultado no depende del conjunto test elegido
    #realizare validación cruzada
    
    #0.6991 (+/- 0.3269)
    svcP2 = SVC(kernel='poly', degree=5)  #creamos el clasificador
    scores = cross_val_score(svcP2, x, y, cv=5)
    
    # exactitud media con intervalo de confianza del 95%
    print("Accuracy 5-cross validation: %0.4f (+/- %0.4f)" % (scores.mean(), scores.std() * 2))

clasificadorSVM()