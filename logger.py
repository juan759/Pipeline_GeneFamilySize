#!/usr/bin/python3

import sys
import os
import datetime


log_directory = "/tmp/Orthofinder/logs"
log_file = "Ejecucion_{:%Y-%m-%d %H:%M:%S}.txt".format(datetime.datetime.now())
log = os.path.join(log_directory, log_file)


def logging(a):
    """
    Función que recibe una cadena y la escribe en un archivo en la dirección de log.

    Parameters
    -------------
    a: str
    Cadena a escribir.

    archivo: str
    Archivo dónde escribir la cadena a.
    """

    # Verifica si el directorio de log existe y, si no, lo crea
    if not os.path.exists(log_directory):
        os.makedirs(log_directory, exist_ok=True)

    # Verifica si el archivo de log existe y, si no, lo crea
    if not os.path.exists(log):
        with open(log, "w") as new_log_file:
            new_log_file.write("Archivo de log creado.\n")

    # Abre el archivo en modo escritura
    with open(log, "a") as file:
        line = "[{:%Y-%m-%d %H:%M:%S}] {}".format(datetime.datetime.now(), a)
        file.write(line + '\n')

    file.close()
