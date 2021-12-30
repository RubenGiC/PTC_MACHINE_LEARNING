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

import matplotlib.pyplot as plt

import time

#importamos el filtro de warnings
from warnings import simplefilter
#ignuramos todos los futuros warnings
simplefilter(action='ignore', category=FutureWarning)
simplefilter(action='ignore', category=DeprecationWarning)

def clasificadorSVM():

    # Asignamos el numero de las columnas de nuestro conjunto de datos
    colnames = ['perimetro', 'profundidad', 'anchura', 'esPierna']

    try:
        """
        cargamos los datos, por defecto el separador es con (,), asi que lo he 
        cambiado por (;) que es como genera mi csv en caracteristicas.py
        """
        dataset = pd.read_csv("resultados/piernasDataset.csv", names=colnames, sep=';') 
    
        print(dataset)
        
        if(dataset.size > 0):
        
            #separamos por un lado los datos y por otro las etiquetas
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
            
            '''
            El porque he escogido este kernel con sus parametros es porque he estado 
            experimentando con distintos kernels y parametros usando la función buscador
            que lo que hace es entrenar el modelo con un kernel especifico y con diferentes parametros.
            '''
            #buscador(x_train, x_test, y_train, y_test, x, y, 'poly')
            #buscador(x_train, x_test, y_train, y_test, x, y, 'rbf')
            #buscador(x_train, x_test, y_train, y_test, x, y, 'linear')
            
            '''
            SI quiere ver la diferencia entre usar un kernel y otro he creado la función 
            comparación, que entrena y muestra los resultados con los mejores parametros
            que se ajustan mejor a dicho conjunto.
            '''
            comparacion(x_train, x_test, y_train, y_test, x, y)
            
            '''
            Para la modificación de los parametros me he basado en la pagina oficial scikit-learn
            https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html
            '''
            
            print('''Viendo los resultados de los diferentes kernels, a simple vista 
podemos descartar el kernel lineal (linear), ya que divide el conjunto en 2 
usando unicamente una linea recta, llegando a no ser muy precisa, luego entre 
rbf y poly, se ve una clara ventaja en rbf, llegando a afinar mejor nuestro 
clasificador. A parte el tiempo de entrenamiento en poly es mucho más alto que
el de rbf.
  Conclusión el que obtiene un mayor acierto es con el kernel RBF.
          ''')
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
            #0.9767
            svcRBF = clasificadorFinal(x_train, y_train)
            
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
            
            #para comprobar de que el resultado no depende del conjunto test elegido
            #realizare validación cruzada
            svcRBF2 = SVC(kernel='rbf', C=1000000)  #creamos el clasificador
            scores = cross_val_score(svcRBF2, x, y, cv=5)
            
            # exactitud media con intervalo de confianza del 95%
            print("Accuracy 5-cross validation: %0.4f (+/- %0.4f)" % (scores.mean(), scores.std() * 2))
            
            porcentaje = (int)((scores.mean()*10000.0)+0.5)
            
            return True, porcentaje/100
        
        else:
            print('Error el conjunto está vacio')
            return False, 0.0
        
    except Exception:
        print('Error al abrir el archivo resultados/piernas.csv')
    

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
    elif(k=='linear'):
        param_grid={'C':[10, 100],
                    'gamma': [0.001, 0.005, 0.0001, 'scale']}
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
    
#función que crea nuestro modelo y lo entrena
def clasificadorFinal(x_train, y_train):
    
    svcRBF = SVC(kernel='rbf', C=1000000)  #creamos el clasificador
    svcRBF.fit(x_train, y_train) #y entrenamos con los datos training
    
    return svcRBF

def comparacion(x_train, x_test, y_train, y_test, x, y):
        
    print('**************************RBF**************************************')
    inicio = time.time()
    rbf(x_train, x_test, y_train, y_test, x, y)
    print('Tiempo:',(time.time()-inicio))
    inicio = time.time()
    print('**************************POLY*************************************')
    poly(x_train, x_test, y_train, y_test, x, y)#el clasificador poly es el que tarda más aproximadamente 1 minuto
    print('Tiempo:',(time.time()-inicio))
    inicio = time.time()
    print('**************************LINEAR*************************************')
    linear(x_train, x_test, y_train, y_test, x, y)
    print('Tiempo:',(time.time()-inicio))
    print('*******************************************************************')
    

def rbf(x_train, x_test, y_train, y_test, x, y):
    
    print("Clasificación con kernek de base radial con C=1000000 y gamma=scale")
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
    svcRBF2 = SVC(kernel='rbf', C=1000000)  #creamos el clasificador
    scores = cross_val_score(svcRBF2, x, y, cv=5)
    
    # exactitud media con intervalo de confianza del 95%
    print("Accuracy 5-cross validation: %0.4f (+/- %0.4f)" % (scores.mean(), scores.std() * 2))
    
def linear(x_train, x_test, y_train, y_test, x, y):
    
    print("Clasificación con kernek de base linear con C=100 y gamma=0.001")
    '''
    en el caso del linear no se puede mejorar más, ya que es lo que más puede 
    clasificar con una resta lineal.
    '''
    svcL = SVC(kernel='linear', C=100, gamma=0.001)  #creamos el clasificador
    svcL.fit(x_train, y_train) #y entrenamos con los datos training
    
    y_pred = svcL.predict(x_test)
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
    svcL2 = SVC(kernel='linear', C=100, gamma=0.001)  #creamos el clasificador
    scores = cross_val_score(svcL2, x, y, cv=5)
    
    # exactitud media con intervalo de confianza del 95%
    print("Accuracy 5-cross validation: %0.4f (+/- %0.4f)" % (scores.mean(), scores.std() * 2))
    
def poly(x_train, x_test, y_train, y_test, x, y):
    print("Clasificación con kernek de base poly con C=10, gamma=scale y degree=5")
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
    svcP2 = SVC(kernel='poly', degree=5, C=10)  #creamos el clasificador
    scores = cross_val_score(svcP2, x, y, cv=5)
    
    # exactitud media con intervalo de confianza del 95%
    print("Accuracy 5-cross validation: %0.4f (+/- %0.4f)" % (scores.mean(), scores.std() * 2))

#clasificadorSVM()
