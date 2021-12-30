#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 11:41:44 2021

@author: Ruben Girela Castellón
"""

import tkinter
import numpy as np
import os
import vrep
from captura import capturarDatos
from agrupar import agruparDatos
from caracteristicas import calculaCaracteristicas
from clasificarSVM import clasificadorSVM
import predecir

#ed_iter = None

#parametros [iteraciones, cerca, medio, lejos, minpuntos, maxpuntos, umbral distancia]
'''
La distancia cerca es 0.8 porque en 0.5 movia el robot y la lectura lo leia mál
'''
params = [50, 0.8, 1.5, 2.5, 3, 41, 0.06]

#guardo los estados posibles de la aplicación
estados = ('Estado: No conectado a VREP', 'Estado: Conectado a VREP')

clientID = -1 #id del emulador vrep

capturado = []#comprobador de capturar los 12 ficheros

global ficheroCapturar

#creo una lista de los archivos a acceder o crear
lista_archivos = ('resultados/positivo1/enPieCerca.json',
                  'resultados/positivo2/enPieMedia.json',
                  'resultados/positivo3/enPieLejos.json',
                  'resultados/positivo4/sentadoCerca.json',
                  'resultados/positivo5/sentadoMedia.json',
                  'resultados/positivo6/sentadoLejos.json',
                  'resultados/negativo1/cilindroMenorCerca.json',
                  'resultados/negativo2/cilindroMenorMedia.json',
                  'resultados/negativo3/cilindroMenorLejos.json',
                  'resultados/negativo4/cilindroMayorCerca.json',
                  'resultados/negativo5/cilindroMayorMedia.json',
                  'resultados/negativo6/cilindroMayorLejos.json'
                  )


#acciones de los botones
def botonPulsadoSalida():#destruye la ventana al pulsar en salir
    global raiz
    #si esta desconectado
    if(clientID == -1):
        #pregungo si quiere salir
        salir=tkinter.messagebox.askyesno(
            'Exit app',
            '¿Está seguro que desea salir?'
            )
        #si es si termina
        if(salir):
            raiz.destroy()
    else:
        #muestro el mensaje de que se debe desconectar el vrep
        tkinter.messagebox.showwarning(
            'Conect VREP',
            'Debe de desconectar VREP antes de salir'
            )
    
def conectVREP():
    global estado, b_descon, b_conect, b_captura
    
    vrep.simxFinish(-1) #Terminar todas las conexiones
    """
    esto lo hago para indicar que no es una variable local de dicha función, sino 
    que modifique la variable fuera de dicha funcion
    """
    #Iniciar una nueva conexion en el puerto 19999 (direccion por defecto)
    globals()['clientID']=vrep.simxStart('127.0.0.1',19999,True,True,5000,5) 
     
    #si no se ha establecido conexion dara error
    if clientID == -1:
        tkinter.messagebox.showerror(
            'Error Conect VREP',
            'No esta conectado el VREP\n(DEBE INICIAR EL SIMULADOR)'
            )
    else:
        #muestro el mensaje de que se ha conectado correctamente
        tkinter.messagebox.showinfo(
            'Conect VREP',
            'Se ha conectado correctamente al VREP'
            )
        #cambio el estado
        estado.set(estados[1])
        #activa el boton de desconectar
        b_descon.config(state="normal")
        #desactivo el boton de conectar
        b_conect.config(state=tkinter.DISABLED)
        #y activo el boton de capturar
        b_captura.config(state="normal")
        
        if(os.path.exists('resultados/piernasDataset.csv') and clientID != -1):
            b_predeci.config(state='normal')
    
#habilita todos los botones
def debugAc():
    global b_descon, b_conect, b_captura, b_agrupar, b_extraer, b_entrena, b_predeci
    
    b_captura.config(state="normal")
    b_descon.config(state="normal")
    b_conect.config(state="normal")
    b_agrupar.config(state="normal")
    b_extraer.config(state="normal")
    b_entrena.config(state="normal")
    b_predeci.config(state="normal")
    
def disconectVREP():
    global estado, b_descon, b_conect, b_captura
    
    vrep.simxFinish(-1) #Terminar todas las conexiones
    globals()['clientID']=-1 #borro el ide del cliente modificandolo a -1
    
    #muestro el mensaje de que se ha desconectado correctamente
    tkinter.messagebox.showinfo(
        'Conect VREP',
        'Se ha desconectado correctamente del VREP'
        )
    #cambio el estado
    estado.set(estados[0])
    #activa el boton de desconectar
    b_descon.config(state=tkinter.DISABLED)
    b_conect.config(state="normal")
    b_captura.config(state=tkinter.DISABLED)
    b_predeci.config(state=tkinter.DISABLED)
    
def capture():
    global lbox_ficheros, b_agrupar
    
    #obtengo la posición del fichero seleccionado
    pos=lbox_ficheros.curselection()    
    
    if(clientID == -1):
        tkinter.messagebox.showerror(
            'Error Conect VREP',
            'Debe conectar con VREP'
            )
    else:
        if(len(pos)==0):
            #muestro el mensaje de que debe elegir un archivo para capturar
            tkinter.messagebox.showwarning(
                'Capturar',
                'Debe elegir un archivo de la lista'
                )
        else:
            """
            #como devuelve una tupla y solo puede seleccionar 1 archivo, cojo el
            de la primera posición
            """
            pos = pos[0]
            
            msg="Editado el archivo "+lista_archivos[pos]
            escrito = False
            
            #compruebo si existe el archivo
            if(not os.path.exists(lista_archivos[pos])):
                #si no existe, pregunto si quiere crear el archivo
                sino=tkinter.messagebox.askyesno(
                    'Crear JSON',
                    'El archivo '+lista_archivos[pos]+' no esta creado, ¿Quiere crearlo?'
                    )
                msg = "Creado el archivo "+lista_archivos[pos]
            else:
                #si existe, pregunto si quiere sobreescribir el archivo
                sino=tkinter.messagebox.askyesno(
                    'Editar JSON',
                    'El archivo '+lista_archivos[pos]+' existe, ¿Quiere reescribirlo?'
                    )
                    
            #si es si crea o edita el archivo
            if(sino):
                
                #con esto indico si es un caso positivo o negativo
                caso = 1
                
                #guardamos las iteraciones y el radio
                parametros = [params[0]]
                
                if(pos in [0,3,6,9]):
                    parametros.append(params[1])
                elif(pos in [1,4,7,10]):
                    parametros.append(params[2])
                else:
                    parametros.append(params[3])
                    
                #indico que estamos en un caso negativo
                if(pos > 5):
                    caso = -1
                
                """
                LLamara a Capturar.py que le pasará el fichero a reescribir o crear
                donde capturara los datos del simulador, cuando termine, si ha 
                terminado con exito habilitara el boton agrupar, para ello devolvera un booleano
                """
                escrito = capturarDatos(lista_archivos[pos], clientID, parametros, caso)
                
                if(escrito):
                    print(msg)
            
            if(escrito):
                if(not pos in capturado):
                    globals()['capturado'].append(pos)
                if(len(capturado) == len(lista_archivos)):
                    b_agrupar.config(state='normal')
    
def agrupar():
    
    global b_extraer
    
    """
    generara los ficheros con los clusters positivos y negativos, tomando como 
    ejemplo los json capturados con el boton capturar
    """
    agrup = agruparDatos(params[4], params[5], params[6], lista_archivos)
    
    #si se a agrupado bien activara el boton extraer
    if(agrup):
        b_extraer.config(state='normal')
        
        #muestro el mensaje de que se ha agrupado correctamente
        tkinter.messagebox.showinfo(
            'Agrupar',
            'Se han generado correctamente los clusters'
            )
        
        #comprueba si existen los archivos clustersNoPiernas.json y clustersPiernas.json
        #si existe activa el boton Extraer caracteristicas
        
        file1 = 'resultados/clustersNoPiernas.json'
        file2 = 'resultados/clustersPiernas.json'
        
        if(os.path.exists(file1) and os.path.exists(file2)):
            b_extraer.config(state='normal')
    else:
        #muestro el mensaje de que se ha producido un error
        tkinter.messagebox.showwarning(
            'Agrupar',
            'Hay un error al agrupar los datos'
            )
        
        
def extraer():
    terminado = calculaCaracteristicas(['resultados/clustersPiernas.json','resultados/clustersNoPiernas.json'])
    
    if(terminado):
        #muestro el mensaje de que se ha extraido correctamente
        tkinter.messagebox.showinfo(
            'Extraer',
            'Se han extraido correctamente los datos'
            )
        if(os.path.exists('resultados/piernasDataset.csv')):
            b_entrena.config(state='normal')
    else:
        #muestro el mensaje de que se ha producido un error
        tkinter.messagebox.showwarning(
            'Extraer',
            'Hay un error al extraer los datos'
            )
            
    
def entrenar():
    terminado, acierto = clasificadorSVM()
    
    if(terminado):
        #muestro el mensaje de que se ha entrenado correctamente
        tkinter.messagebox.showinfo(
            'Entrenamiento',
            'Se han entrenado correctamente, ha conseguido un '+str(acierto)+'% de acierto'
            )
        if(os.path.exists('resultados/piernasDataset.csv') and clientID != -1):
            b_predeci.config(state='normal')
    else:
        #muestro el mensaje de que se ha producido un error
        tkinter.messagebox.showwarning(
            'Entrenamiento',
            'Hay un error al entrenar con el clasificador'
            )
        
def predecir2():
    
    if(clientID == -1):
        tkinter.messagebox.showerror(
            'Error Conect VREP',
            'Debe conectar con VREP'
            )
    else:
        terminado = predecir.modelo(clientID, params[4], params[5], params[6])
        
        if(terminado):
            #muestro el mensaje de que se ha entrenado correctamente
            tkinter.messagebox.showinfo(
                'Predicción',
                'Se han predecido correctamente. Vea la grafica en resultados/prediccion/predecido.jpg'
                )
        else:
            #muestro el mensaje de que se ha producido un error
            tkinter.messagebox.showwarning(
                'Predicción',
                'Hay un error al predecir'
                )
    
#función que comprueba que los datos son correctos al pulsar cambiar
def validarDatos():
    #recibo los objetos del tkinter creados antes
    global ed_iter, ed_cer, ed_medi, ed_lejo, ed_min, ed_max, ed_ub
    
    #y guardo su contenido
    contenido = [
        ed_iter.get(), 
        ed_cer.get(), 
        ed_medi.get(), 
        ed_lejo.get(), 
        ed_min.get(),
        ed_max.get(),
        ed_ub.get()]
    
    #creo una tupla por si algun campo no es correcto, que especifique cual es
    campos = ('Cerca', 'Media', 'Lejos', 'Min. Puntos', 'Max. Puntos', 'Umbral Distancia')
    
    #variable que contendra el campo donde da error
    error_campo = ''
    
    
    try:
        #si el contenido no esta vacio
        if(len(contenido[0])>0):
            #compruebo que es un entero y >=0
            assert contenido[0].isdigit(), 'Error tiene que ser numerico y entero, en el campo iteraciones'
        
        #como el resto puede contener decimales los recorro igual
        for i in np.arange(1,len(contenido)):
            #guardo el campo por si da error
            error_campo = campos[i-1]
            #si no esta vacio
            if(len(contenido[i])>0):
                #lo transformo a flotante
                contenido[i] = float(contenido[i])
                
        params = contenido.copy()
        print("Iteraciones:",params[0])
        print("Cerca:",params[1])
        print("Media:",params[2])
        print("Lejos:",params[3])
        print("Min. puntos:",params[4])
        print("Max. puntos:",params[5])
        print("Umbral dinstancia:",params[6])
        
    #si no es un entero y positivo el campo Iteraciones
    except AssertionError as error:
        #imprimo el error, indicando el campo
        print(error)
        #y le muestro el error al usuario
        tkinter.messagebox.showerror(
            'Error Datos',
            error
            )
    #para el resto de campos
    except ValueError as e:
        #imprimo el error, indicando el campo
        print(f"Error tipo ({error_campo}): {e}")
        #y le muestro el error al usuario
        tkinter.messagebox.showerror(
            'Error Datos',
            'Error tiene que ser numerico el campo '+error_campo
            )
        
def creaDirectorios(directorios):
    
    #y para guardar directorios en una ruta especifica
    for i in np.arange(len(directorios)):
        
        #si no esta creado el directorio lo crea
        if (not os.path.isdir(directorios[i])):
            #creamos los directorios
            os.mkdir(directorios[i])
            #con esto cambiamos el directorio de trabajo
            #os.chdir(directorios[i])
            #print("Cambiando el directorio de trabajo: ", os.getcwd())
        
        else:#en caso contrario muestro un mensaje de error
            #sys.exit("Error: ya existe el directorio "+ directorio)
            print("Error: ya existe el directorio "+ directorios[i])
        
#clase que crea la interfaz y usa la funcionalidad de la aplicación
class Aplicacion():
    
    #inicializo la ventana
    def __init__(self, parent, lista_archivos):
        
        #para la acción de salir
        global raiz
        #para la acción aplicarle los cambios
        global ed_iter, ed_cer, ed_medi, ed_lejo, ed_min, ed_max, ed_ub
        #para cambiar el estado
        global estado
        #para cambiar la configuración de los botones
        global b_descon, b_conect, b_captura, b_agrupar, b_extraer, b_entrena, b_predeci
        #para la acción capturar
        global lbox_ficheros
        
        #guardo la lista de archivos
        self.lista = lista_archivos
        
        #creo una lista visual que se mostrara en tkinter, ya que los archivos 
        #estaran guardados en una carpeta llamada resultados
        self.list_visual = []
        
        for i in self.lista:
            l = i.split('/')
            self.list_visual.append(l[1]+'/'+l[2])
        
        #guardo el root
        self.parent = parent
        
        #creo la etiqueta inicial
        etiqueta = tkinter.Label(self.parent, text='Es necesario ejecutar el simulador VREP')
        etiqueta.grid(row=0, column=0)
        
        #creo los botones conectar y desconectar VREP
        b_conect = tkinter.Button(self.parent, text='Conectar con VREP', command=conectVREP)
        b_conect.grid(row=1,column=0)
        
        b_descon = tkinter.Button(
            self.parent, 
            text='Detener y desconectar VREP', 
            state= tkinter.DISABLED,
            command=disconectVREP)
        b_descon.grid(row=2,column=0)
        
        #inicio el estado a desconectado
        estado = tkinter.StringVar()
        estado.set(estados[0])
        
        #creo el label que mostrara el estado actual en el que se encuentra
        estado_l = tkinter.Label(self.parent, textvariable=estado)
        estado_l.grid(row=3, column=0)
        
        #añado el resto de botones
        b_captura = tkinter.Button(self.parent, text='Capturar', state = tkinter.DISABLED, command=capture)
        b_captura.grid(row=4, column=0)
        b_agrupar = tkinter.Button(self.parent, text='Agrupar', state = tkinter.DISABLED, command=agrupar)
        b_agrupar.grid(row=5, column=0)
        b_extraer = tkinter.Button(
            self.parent, 
            text='Extraer caracteristicas', 
            state = tkinter.DISABLED, 
            command=extraer)
        b_extraer.grid(row=6, column=0)
        b_entrena = tkinter.Button(
            self.parent, 
            text='Entrenar Clasificador', 
            state = tkinter.DISABLED,
            command = entrenar)
        b_entrena.grid(row=7, column=0)
        b_predeci = tkinter.Button(self.parent, text='Predecir', state = tkinter.DISABLED, command=predecir2)
        b_predeci.grid(row=8, column=0)
        
        #le indico el root para la acción salir
        raiz = parent
        b_exit = tkinter.Button(self.parent, text='Salir', command=botonPulsadoSalida)
        b_exit.grid(row=9, column=0)
        
        #le indico el root para la acción DEBUG
        raiz = parent
        b_debug = tkinter.Button(self.parent, text='DEBUG', command=debugAc)
        b_debug.grid(row=10, column=0)
        
        #creo los campos de las columnas 1 y 2
        etiqueta2 = tkinter.Label(self.parent, text='Parámetros:')
        etiqueta2.grid(row=1, column=1)
        
        et_iter = tkinter.Label(self.parent, text='Iteraciones:', anchor="e", justify=tkinter.RIGHT)
        et_iter.grid(sticky=tkinter.E, row=2, column=1)
        ed_iter = tkinter.Entry(self.parent, width=5)
        ed_iter.insert(0,params[0])
        ed_iter.grid(row=2, column=2)
        #validarEntero(ed_iter, 'Iteraciones')
        
        et_cer = tkinter.Label(self.parent, text='Cerca:', anchor="e", justify=tkinter.RIGHT)
        et_cer.grid(sticky=tkinter.E, row=3, column=1)
        ed_cer = tkinter.Entry(self.parent, width=5)
        ed_cer.insert(0,params[1])
        ed_cer.grid(row=3, column=2)
        
        et_medi = tkinter.Label(self.parent, text='Media:', anchor="e", justify=tkinter.RIGHT)
        et_medi.grid(sticky=tkinter.E, row=4, column=1)
        ed_medi = tkinter.Entry(self.parent, width=5)
        ed_medi.insert(0, params[2])
        ed_medi.grid(row=4, column=2)
        
        et_lejo = tkinter.Label(self.parent, text='Lejos:', anchor="e", justify=tkinter.RIGHT)
        et_lejo.grid(sticky=tkinter.E, row=5, column=1)
        ed_lejo = tkinter.Entry(self.parent, width=5)
        ed_lejo.insert(0, params[3])
        ed_lejo.grid(row=5, column=2)
        
        et_min = tkinter.Label(
            self.parent, 
            text='Min. Puntos:', 
            anchor="e", 
            justify=tkinter.RIGHT)
        et_min.grid(sticky = tkinter.E, row=6, column=1)
        ed_min = tkinter.Entry(self.parent, width=5)
        ed_min.insert(0,params[4])
        ed_min.grid(row=6, column=2)
        
        et_max = tkinter.Label(
            self.parent, 
            text='Max. Puntos:',
            anchor="e", 
            justify=tkinter.RIGHT)
        et_max.grid(sticky=tkinter.E, row=7, column=1)
        ed_max = tkinter.Entry(self.parent, width=5)
        ed_max.insert(0,params[5])
        ed_max.grid(row=7, column=2)
        
        et_ub = tkinter.Label(
            self.parent, 
            text='Umbral Distancia:', 
            anchor="e", 
            justify=tkinter.RIGHT)
        et_ub.grid(sticky=tkinter.E, row=8, column=1)
        ed_ub = tkinter.Entry(self.parent, width=5)
        ed_ub.insert(0, params[6])
        ed_ub.grid(row=8, column=2)
        
        #creo el boton para aplicar los cambios
        b_change = tkinter.Button(self.parent, text='Cambiar', command=validarDatos)
        b_change.grid(row=9, column=1)
        
        et_fich = tkinter.Label(self.parent, text='Fichero para la captura')
        et_fich.grid(row=1, column=3, rowspan=2)
        
        #y creo y relleno la lista de archivos
        lbox_ficheros = tkinter.Listbox(self.parent, width=35, height=12)
        lbox_ficheros.grid(row=3, column=3, rowspan=6)
        
        #añado los archivos en la lista
        lbox_ficheros.insert(0, *self.list_visual)
        

        #comprueba si existe el archivo, si esta creado el archivo lo añade a la lista de capturados
        pos = 0
        for file in lista_archivos:
            
            if(not pos in capturado and os.path.exists(file)):
                globals()['capturado'].append(pos)
            pos += 1
        #si existen todos los archivos habilito el boton de agrupar
        if(len(capturado) == len(lista_archivos)):
            b_agrupar.config(state='normal')
    
        #comprueba si existen los archivos clustersNoPiernas.json y clustersPiernas.json
        #si existe activa el boton Extraer caracteristicas
        
        file1 = 'resultados/clustersNoPiernas.json'
        file2 = 'resultados/clustersPiernas.json'
        
        if(os.path.exists(file1) and os.path.exists(file2)):
            b_extraer.config(state='normal')
            
        if(os.path.exists('resultados/piernasDataset.csv')):
            b_entrena.config(state='normal')
            
        if(os.path.exists('resultados/piernasDataset.csv') and clientID != -1):
            b_predeci.config(state='normal')
    
#compruebo si esta en el entorno principal, si lo esta ejecuto la aplicación
if __name__=="__main__":
    
    #guardo sus directorios para crearlos si no estan creados
    directorios = ['resultados']
    
    for arch in lista_archivos:
        directorios.append(arch.split('/')[0]+'/'+arch.split('/')[1])
        
    directorios.append('resultados/prediccion')
    
    #creo los directorios que no esten creados
    creaDirectorios(directorios)

    #ejecuto la aplicación
    root = tkinter.Tk()
    root.title('Practica PTC Tkinter Robótica')
    root.geometry('700x300')
    
    app = Aplicacion(root, lista_archivos)
    
    root.mainloop()
    
    #print(os.getcwd())