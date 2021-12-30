#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 19:52:45 2021

@author: Ruben Girela Castellón
"""

import json

#función que lee archivos json y devuelve una lista con el contenido del json
def leerJson(files, del_first_line = False):
    resultados = []
    try:
        for file in files:
                first = del_first_line
                #leemos el fichero json
                with open(file, 'r') as f:
                 for line in f:
                     
                     if(not first):
                         #y guardamos su contenido
                         resultados.append(json.loads(line))
                    
                     first = False
                     
    except FileNotFoundError:
        print('Error hay un archivo que no se ha encontrado')
    except Exception:
        print('Error el archivo no se ha podido abrir')
    return resultados