#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 20 17:27:35 2021

@author: Ruben Girela Castellón
"""
import vrep
import time
import os
import json
import cv2
import math
import matplotlib.pyplot as plt

"""
FUnción que realiza la captura de los datos del simulador, para ello necesita 
el id del cliente, la ruta del archivo a almacenar los datos, los parametros 
(iteraciones y radio) y si es un caso negativo o positivo.
"""

def capturarDatos(path, clientID, params, caso):
    
    # mostramos el directorio de trabajo y vemos si existe el dir para salvar los datos
    print("Directorio de trabajo es: ", os.getcwd())
    
    #Guardar la referencia de los motores
    _, left_motor_handle=vrep.simxGetObjectHandle(clientID, 'Pioneer_p3dx_leftMotor', vrep.simx_opmode_oneshot_wait)
    _, right_motor_handle=vrep.simxGetObjectHandle(clientID, 'Pioneer_p3dx_rightMotor', vrep.simx_opmode_oneshot_wait)
     
    #Guardar la referencia de la camara
    _, camhandle = vrep.simxGetObjectHandle(clientID, 'Vision_sensor', vrep.simx_opmode_oneshot_wait)
     
    
    #acceder a los datos del laser
    _, datosLaserComp = vrep.simxGetStringSignal(clientID,'LaserData',vrep.simx_opmode_streaming)
    
    #indicamos el tiempo de espeta 0.5 segundos
    segundos=0.5
    #obtenemos el numero maximo de iteraciones
    maxIter=params[0]
    #iteracion a empezar
    iteracion=1
    
    #creamos la cabecera
    cabecera={"TiempoSleep":segundos,
              "MaxIteraciones":maxIter}
    try:
        #accedo o creo el archivo json para guardar los datos del laser
        ficheroLaser=open(path, "w")
    

        #gardamos la cabecera en el archivo
        ficheroLaser.write(json.dumps(cabecera)+'\n')    
    
        seguir=True
        
        #numero de posiciones a trasladarse
        puntos = 5
        
        #si es un caso negativo moveremos un objeto Cilindro
        if(caso<0):
            # obtenermos la referencia del cilindro 1 y 2 para moverla    
            _, obj = vrep.simxGetObjectHandle(clientID, 'Cylinder', vrep.simx_opmode_oneshot_wait)
        
        #en caso contrario es un caso positivo y moveremos un objeto persona
        else:
            # obtenermos la referencia a la persona de pie Bill para moverla    
            _, obj = vrep.simxGetObjectHandle(clientID, 'Bill', vrep.simx_opmode_oneshot_wait)
        
        #con esto indico cada cuantas iteraciones el muñeco se trasladara
        mover = maxIter//puntos
        
        #grado de rotación por cada x iteraciones
        """
        Ejemplo si tenemos 50 iteraciones y tenemos 5 puntos, cada punto tendrá 10 
        iteraciones, de tal forma que girara 360/10 = 36º por cada iteración haciendo 
        los 360º de ese punto y se repetira con el resto.
        """
        rot = 360//mover
        
        #guardo el radio
        radio = params[1]
        
        """
        calculamos el angulo que tendrá cada parte, experimentando vi que tiene 
        una amplitud de 90º el laser del robot y por eso la amplitud es 90º
        """
        ang_part = (90/puntos)
        
        #inicializo el angulo inicial de donde partira (va de izquierda a derecha con respecto al robot)
        angulo = -(ang_part*2)
     
        #recorro las x iteraciones
        while(iteracion<=maxIter and seguir):
            
            #si ha rotado 360º muevo el muñeco
            if(iteracion%mover == 1):
                
                """
                Para calcular la traslación con respecto al radio:
                    x = cos(angulo)/radio
                    y = sin(angulo)/radio
                    
                    este va de -72º a 72º, esto se ha hecho así, porque se va a mover
                    en 5 puntos, con lo cual va de -72º, -36º, 0º, 36º, 72º
                """
                ejeX = math.cos(math.radians(angulo))*radio
                ejeY = math.sin(math.radians(angulo))*radio
                
                print(f'TRASLACIÓN: X={ejeX}, Y={ejeY}')
                
                #Situamos donde queremos a la persona de pie, unidades en metros
                returnCode = vrep.simxSetObjectPosition(clientID,obj,-1,[ejeX,ejeY,0.0],vrep.simx_opmode_oneshot)
                
                #incremento el angulo para la siguiente traslación
                angulo += ang_part
            
            
            #calculo el angulo en radianes para la rotación del muñeco
            #ejeZ = (math.pi*rot*iteracion)/180
            ejeZ =  math.radians(rot*iteracion)
            
            print(f'Rotacion (radianes): {ejeZ}')
            
            #Cambiamos la orientacion, ojo está en radianes: Para pasar de grados a radianes hay que multiplicar por PI y dividir por 180
            returnCode = vrep.simxSetObjectOrientation(clientID, obj, -1, [0.0,0.0,ejeZ], vrep.simx_opmode_oneshot)
            
            time.sleep(segundos) #esperamos un tiempo para que el ciclo de lectura de datos no sea muy rápido
            
            puntosx=[] #listas para recibir las coordenadas x, y z de los puntos detectados por el laser
            puntosy=[]
            returnCode, signalValue = vrep.simxGetStringSignal(clientID,'LaserData',vrep.simx_opmode_buffer) 
           
            datosLaser=vrep.simxUnpackFloats(signalValue)
            for indice in range(0,len(datosLaser),3):
                puntosx.append(datosLaser[indice+1])
                puntosy.append(datosLaser[indice+2])
            
            print("Iteración: ", iteracion)                
            
            name = path.split('.')[0]
            
            try:
                #guardamos las graficas de la primera y ultima iteración
                if(iteracion == 1 or iteracion == maxIter):
                    #pinto los puntos obtenidos
                    plt.clf()    
                    plt.plot(puntosx, puntosy, 'r.')
                    plt.savefig(name+str(iteracion)+".jpg")
            except Exception:
                print('Error no se ha podido crear la grafica',name+str(iteracion)+".jpg")
            
            #Guardamos los puntosx, puntosy en el fichero JSON
            lectura={"Iteracion":iteracion, "PuntosX":puntosx, "PuntosY":puntosy}
            ficheroLaser.write(json.dumps(lectura)+'\n')
            
            #para cortar la captura
            tecla = cv2.waitKey(5) & 0xFF
            if tecla == 27:
                seguir=False
            
            iteracion=iteracion+1
                
            
        #detenemos la simulacion
        #vrep.simxStopSimulation(clientID,vrep.simx_opmode_oneshot_wait)
        ficheroLaser.close()
        
    except FileNotFoundError:
        print('Error el archivo',path,'no se ha encontrado')
    
    return seguir

#Este es para el modo predecir 
def capturarDirecto(path, clientID):
    
    # mostramos el directorio de trabajo y vemos si existe el dir para salvar los datos
    #print("Directorio de trabajo es: ", os.getcwd())
    
    #Guardar la referencia de los motores
    _, left_motor_handle=vrep.simxGetObjectHandle(clientID, 'Pioneer_p3dx_leftMotor', vrep.simx_opmode_oneshot_wait)
    _, right_motor_handle=vrep.simxGetObjectHandle(clientID, 'Pioneer_p3dx_rightMotor', vrep.simx_opmode_oneshot_wait)
     
    #Guardar la referencia de la camara
    _, camhandle = vrep.simxGetObjectHandle(clientID, 'Vision_sensor', vrep.simx_opmode_oneshot_wait)
     
    
    #acceder a los datos del laser
    _, datosLaserComp = vrep.simxGetStringSignal(clientID,'LaserData',vrep.simx_opmode_streaming)
    
    #indicamos el tiempo de espeta 0.5 segundos
    segundos=0.5
    #obtenemos el numero maximo de iteraciones
    maxIter=1
    
    #creamos la cabecera
    cabecera={"TiempoSleep":segundos,
              "MaxIteraciones":maxIter}
    
    try:
        #accedo o creo el archivo json para guardar los datos del laser
        ficheroLaser=open(path, "w")
    
        #gardamos la cabecera en el archivo
        ficheroLaser.write(json.dumps(cabecera)+'\n')
        
        puntosx=[] #listas para recibir las coordenadas x, y z de los puntos detectados por el laser
        puntosy=[]
        
        while(len(puntosx)==0):
            puntosx=[] #listas para recibir las coordenadas x, y z de los puntos detectados por el laser
            puntosy=[]
            time.sleep(segundos) #esperamos un tiempo para que el ciclo de lectura de datos no sea muy rápido
            
            
            returnCode, signalValue = vrep.simxGetStringSignal(clientID,'LaserData',vrep.simx_opmode_buffer) 
           
            datosLaser=vrep.simxUnpackFloats(signalValue)
            for indice in range(0,len(datosLaser),3):
                puntosx.append(datosLaser[indice+1])
                puntosy.append(datosLaser[indice+2])
            
            #Guardamos los puntosx, puntosy en el fichero JSON
            lectura={"Iteracion":1, "PuntosX":puntosx, "PuntosY":puntosy}
            #ficheroLaser.write('{}\n'.format(json.dumps(lectura)))
            ficheroLaser.write(json.dumps(lectura)+'\n')            
            
        #detenemos la simulacion
        #vrep.simxStopSimulation(clientID,vrep.simx_opmode_oneshot_wait)
        ficheroLaser.close()
        
    except FileNotFoundError:
        print('Error el archivo',path,'no se ha encontrado')
    except Exception:
        print('Error el archivo',path,' no se ha podido abrir')
        
    return True