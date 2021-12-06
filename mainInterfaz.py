#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 11:41:44 2021

@author: Ruben Girela Castellón
"""

import tkinter
import numpy as np
import os
import sys

#ed_iter = None

#acciones de los botones
def botonPulsadoSalida():#destruye la ventana al pulsar en salir
    global raiz
    raiz.destroy()
    
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
        
        #guardo la lista de archivos
        self.lista = lista_archivos
        #guardo el root
        self.parent = parent
        #e inicializo el estado a desconectado
        self.estado = 0
        #guardo los estados posibles de la aplicación
        self.estados = ('Estado: No conectado a VREP', 'Estado: Conectado a VREP')
        
        #creo la etiqueta inicial
        etiqueta = tkinter.Label(self.parent, text='Es necesario ejecutar el simulador VREP')
        etiqueta.grid(row=0, column=0)
        
        #creo los botones conectar y desconectar VREP
        b_conect = tkinter.Button(self.parent, text='Conectar con VREP')
        b_conect.grid(row=1,column=0)
        
        b_descon = tkinter.Button(
            self.parent, 
            text='Detener y desconectar VREP', 
            state= tkinter.DISABLED)
        b_descon.grid(row=2,column=0)
        
        #creo el label que mostrara el estado actual en el que se encuentra
        estado = tkinter.Label(self.parent, text=self.estados[self.estado])
        estado.grid(row=3, column=0)
        
        #añado el resto de botones
        b_captura = tkinter.Button(self.parent, text='Capturar', state = tkinter.DISABLED)
        b_captura.grid(row=4, column=0)
        b_agrupar = tkinter.Button(self.parent, text='Agrupar', state = tkinter.DISABLED)
        b_agrupar.grid(row=5, column=0)
        b_extraer = tkinter.Button(
            self.parent, 
            text='Extraer caracteristicas', 
            state = tkinter.DISABLED)
        b_extraer.grid(row=6, column=0)
        b_entrena = tkinter.Button(
            self.parent, 
            text='Entrenar Clasificador', 
            state = tkinter.DISABLED)
        b_entrena.grid(row=7, column=0)
        b_predeci = tkinter.Button(self.parent, text='Predecir', state = tkinter.DISABLED)
        b_predeci.grid(row=8, column=0)
        
        #le indico el root para la acción salir
        raiz = parent
        b_exit = tkinter.Button(self.parent, text='Salir', command=botonPulsadoSalida)
        b_exit.grid(row=9, column=0)
        
        #creo los campos de las columnas 1 y 2
        etiqueta2 = tkinter.Label(self.parent, text='Parámetros:')
        etiqueta2.grid(row=1, column=1)
        
        et_iter = tkinter.Label(self.parent, text='Iteraciones:', anchor="e", justify=tkinter.RIGHT)
        et_iter.grid(sticky=tkinter.E, row=2, column=1)
        ed_iter = tkinter.Entry(self.parent, width=5)
        ed_iter.insert(0,'50')
        ed_iter.grid(row=2, column=2)
        #validarEntero(ed_iter, 'Iteraciones')
        
        et_cer = tkinter.Label(self.parent, text='Cerca:', anchor="e", justify=tkinter.RIGHT)
        et_cer.grid(sticky=tkinter.E, row=3, column=1)
        ed_cer = tkinter.Entry(self.parent, width=5)
        ed_cer.insert(0,'0.5')
        ed_cer.grid(row=3, column=2)
        
        et_medi = tkinter.Label(self.parent, text='Media:', anchor="e", justify=tkinter.RIGHT)
        et_medi.grid(sticky=tkinter.E, row=4, column=1)
        ed_medi = tkinter.Entry(self.parent, width=5)
        ed_medi.insert(0, '1.5')
        ed_medi.grid(row=4, column=2)
        
        et_lejo = tkinter.Label(self.parent, text='Lejos:', anchor="e", justify=tkinter.RIGHT)
        et_lejo.grid(sticky=tkinter.E, row=5, column=1)
        ed_lejo = tkinter.Entry(self.parent, width=5)
        ed_lejo.insert(0, '2.5')
        ed_lejo.grid(row=5, column=2)
        
        et_min = tkinter.Label(
            self.parent, 
            text='Min. Puntos:', 
            anchor="e", 
            justify=tkinter.RIGHT)
        et_min.grid(sticky = tkinter.E, row=6, column=1)
        ed_min = tkinter.Entry(self.parent, width=5)
        ed_min.insert(0,'0')
        ed_min.grid(row=6, column=2)
        
        et_max = tkinter.Label(
            self.parent, 
            text='Max. Puntos:',
            anchor="e", 
            justify=tkinter.RIGHT)
        et_max.grid(sticky=tkinter.E, row=7, column=1)
        ed_max = tkinter.Entry(self.parent, width=5)
        ed_max.insert(0,'0')
        ed_max.grid(row=7, column=2)
        
        et_ub = tkinter.Label(
            self.parent, 
            text='Umbral Distancia:', 
            anchor="e", 
            justify=tkinter.RIGHT)
        et_ub.grid(sticky=tkinter.E, row=8, column=1)
        ed_ub = tkinter.Entry(self.parent, width=5)
        ed_ub.insert(0, '0')
        ed_ub.grid(row=8, column=2)
        
        #creo el boton para aplicar los cambios
        b_change = tkinter.Button(self.parent, text='Cambiar', command=validarDatos)
        b_change.grid(row=9, column=1)
        
        et_fich = tkinter.Label(self.parent, text='Fichero para la captura')
        et_fich.grid(row=1, column=3, rowspan=2)
        
        #y creo y relleno la lista de archivos
        lista_ficheros = tkinter.Listbox(self.parent, width=35, height=12)
        lista_ficheros.grid(row=3, column=3, rowspan=6)
        
        i = 0
        
        for archivo in self.lista:
            lista_ficheros.insert(i, archivo)
            i += 1
        
    
    
#compruebo si esta en el entorno principal, si lo esta ejecuto la aplicación
if __name__=="__main__":
    
    #creo una lista de los archivos a acceder o crear
    lista_archivos = ('positivo1/enPieCerca.json',
                      'positivo2/enPieMedia.json',
                      'positivo3/enPieLejos.json',
                      'positivo4/sentadoCerca.json',
                      'positivo5/sentadoMedia.json',
                      'positivo6/sentadoLejos.json',
                      'negativo1/cilindroMenorCerca.json',
                      'negativo2/cilindroMenorMedia.json',
                      'negativo3/cilindroMenorLejos.json',
                      'negativo4/cilindroMayorCerca.json',
                      'negativo5/cilindroMayorMedia.json',
                      'negativo6/cilindroMayorLejos.json'
                      )
    
    #guardo sus directorios para crearlos si no estan creados
    directorios = ['resultados']
    
    for arch in lista_archivos:
        directorios.append('resultados/'+arch.split('/')[0])
    
    #creo los directorios que no esten creados
    creaDirectorios(directorios)

    #ejecuto la aplicación
    root = tkinter.Tk()
    root.title('Practica PTC Tkinter Robótica')
    root.geometry('700x300')
    
    app = Aplicacion(root, lista_archivos)
    
    root.mainloop()