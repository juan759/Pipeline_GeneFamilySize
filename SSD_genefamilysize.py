#!/usr/bin/python3

import sys
import subprocess
import urllib.request
import os
import logger as logort
import cleaner as cl
import csv

def usage():
    print("[+]Como usarlo: python3 Orthofinder_better.py --format-list <csv o txt> --url-list <URL_LIST_FILE> --ortho-three <PATH_to_tree>")
    print("[+]--url-list <URL_LIST_FILE>.txt: Path a la lista de links https para obtener los genomas.")
    print("[+]--ortho-three <PATH_to_tree>.tre: Parametro opcional para procesar árbol ortológico.")
    sys.exit(1)

def welcome_message():
    print("---------------------------------------")
    print("[++]Bienvenido al Pipeline para OrthoFinder.[++]")
    print("---------------------------------------")
    print("[+]Bajando las url que vienen en el archivo csv:")
    print("[+]Ejemplo de url valida:https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/004/115/215/GCF_004115215.1_mOrnAna1.p.v1/GCF_004115215.1_mOrnAna1.p.v1_translated_cds.faa.gz")
    print("Registros temporales de ejecución se pueden encontrar en /tmp/Orthofinder/logs")
    print("---------------------------------------------------------")

def check_dependency(tool_name):
    """
    Función auxiliar para la verificación de la instalación de una herramienta en el sistema.

    Parameters
    ------------
    tool_name: str
    El nombre de la herramienta a verificar su instalación.
    """
    try:
        subprocess.run([tool_name, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print("[+] {} está instalado.".format(tool_name))
    except subprocess.CalledProcessError:
        print("[ERROR] {} no está instalado o no es posible usarlo.".format(tool_name))
    
def check_awk():
    try:
        subprocess.run(["awk","-W","version"],stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print("[+] awk está instalado")
    except subprocess.CalledProcessError:
        print("awk no está instalado")

def check_dependencies():
    """
    Función que verifica la instalación de varias herramientas en el sistema.
    """
    print("[/] Checando herramientas... [\]")
    
    tools_to_check = ["samtools", "grep", "curl", "gzip"]

    for tool in tools_to_check:
        check_dependency(tool)
    check_awk()
    logort.logging("Verificación de herramientas terminada iniciando descargas...")

def download_file(url):
    """
    Función que descarga un archivo mediante una petición HTTP.

    Parameters
    -----------
    url:str.
    El link al archivo a descargar en línea.
    """
    output_file = url.split("/")[-1]
    urllib.request.urlretrieve(url, output_file)
    logort.logging(f"Archivo descargado: {output_file}")
    return output_file

def obtener_nombres_csv(csv_file):
    """
    Función para renombrar archivos.

    Parameters 
    -----------
    downloaded: list(str)
    Lista de archivos descargados, se obtienen del parametro en consola "--url-list".

    Return
    ----------
    downloaded: list(str)
    Lista de los archivos con los nombre nuevos obtenidos del usuario.
    """
    csv_names = [] # Lista para almacenar los valores de la columna 'NCBI Link'
    with open(csv_file) as csvf:
        csv_reader = csv.DictReader(csvf)
        unamed=1
        for row in csv_reader:
            try:
                if row['Names']=="":
                    csv_names.append(f"unamed{unamed}".strip())
                    unamed += 1
                    continue
                csv_names.append(row['Names'].strip())
            except KeyError:
                logort.logging("La columna 'Names' no existe en el archivo CSV.")
                print("Revisar logs.")
                exit(0)
    return csv_names

def corrije_download(downloaded,nombres_correctos):
    """
    Función que renombra los archivos descargados de NCBI a nombres que el usuario requiera.

    Parameters
    --------------
    downloaded: list(str)
    Lista de archivos descargados, se obtienen del parametros en consola "--url-list".

    nombres_correctos: list(str)
    Lista de nombres con los que el usuario quiere renombrar los archivos descargados.
    
    """
    nombres = []
    for i in range(len(downloaded)):
        print(f"Renombrando archivo {downloaded[i]} a {nombres_correctos[i]}")
        nombres.append(f"{nombres_correctos[i]}.faa")
        os.rename(downloaded[i],f"{nombres_correctos[i]}.faa.gz")
        subprocess.run(f"gzip -d {nombres_correctos[i]}.faa.gz",shell=True,executable="/bin/bash")
    return nombres

def process_csv(csv_file):
    """
    función equivalente a open(file,'r').readlines() pero para un archivo csv con una columna de urls.

    Parameters
    -----------------------
    csv_file:file

    Return 
    ------------------------
    csv_urls:list(str)
    """
    csv_urls = [] # Lista para almacenar los valores de la columna 'NCBI Link'
    with open(csv_file) as csvf:
        csv_reader = csv.DictReader(csvf)
        for row in csv_reader:
            try:
                csv_urls.append(row['NCBI Link'])
            except KeyError:
                logort.logging("La columna 'NCBI Link' no existe en el archivo CSV.")
                print("Revisar logs.")
                exit(0)
                
    return csv_urls

def pasos_samtools(downloaded):
    """
    Función que aplica samtools a una lista de archivos faa.

    Parameters
    -----------
    downloaded: list(str).
    Lista de archivos.

    Return
    -----------
    downloaded: list(str).
    Lista de archivos tras aplicarles samtools.
    """
    print("------------------------------------------------------------")
    print("[+]Ahora, rextraemos los índices para cada genoma...")
    for i in downloaded:
        subprocess.run(f"samtools faidx {i}", shell=True, executable="/bin/bash")
    return downloaded

def grep_and_awk(downloaded):
    """
    Función que aplica awk y grep a una lista de archivos para obtener información relevante..

    Parameters
    -----------
    downloaded: list(str).
    Lista de archivos.

    Return
    -----------
    downloaded: list(str).
    Lista de archivos tras aplicarles grep y awk.
    """
    print("------------------------------------------------------------")
    print("[+]Ahora aplicaremos grep para obtener la información de cada gen...")
    for i in downloaded:
        subprocess.run(f"grep -Eo 'gene=[[:alnum:]]*|protein_id=[^]]*|lcl[^[:blank:]]*|db_xref=[^]]*' {i} > {i}_1.txt", shell=True, executable="/bin/bash")

    patterns = [
        "awk -v ADD='protein_id=NA' -v PATTERN1='db_xref=' -v PATTERN2='lcl[[:punct:]]' 'L { print L; if((L ~ PATTERN1) && ($0 ~ PATTERN2)) print ADD }; { L=$0 } END { print L }'",
        "awk -v ADD='gene=NA' -v PATTERN1='lcl[[:punct:]]' -v PATTERN2='db_xref=' 'L { print L; if((L ~ PATTERN1) && ($0 ~ PATTERN2)) print ADD }; { L=$0 } END { print L }'"
    ]

    for i, pattern in enumerate(patterns, start=2):
        for j in downloaded:
            subprocess.run(f"{pattern} {j}_{i - 1}.txt > {j}_{i}.txt", shell=True, executable="/bin/bash")

        escaped_n = "\n".encode('unicode_escape').decode("utf-8")
        for k in downloaded:
            subprocess.run(f"awk 'ORS=NR%4?\" \":\"{escaped_n}\"' {k}_{i}.txt > {k}_df.txt", shell=True, executable="/bin/bash")
    cl.clean_step5()

def check_format(index):
    """
    Función para revisar que el format del archivo con los links de entrada sea válido.

    Parameters
    ----------------------------
    index:int

    Return
    ----------------------------
    sys.argv[index]:int
    
    """
    formatos = ["csv","txt"]
    if sys.argv[index] in formatos:
        return sys.argv[index]
    else:
        logort.logging("El archivo de donde se extraen los links no es un formato de entrada válido.")
        print("Aquí")
        usage()

def extract_indices(downloaded):
    """
    Función que aplica awk a una lista de archivos para obtener índices dentro de genes.

    Parameters
    -----------
    downloaded: list(str).
    Lista de archivos.

    Return
    -----------
    downloaded: list(str).
    Lista de archivos tras aplicarles awk múltiples veces.
    """
    print("------------------------------------------------------------")
    print("[+]Extrayendo los índices para filtrar por genes y mapearlos con sus ID's...")
    for i in downloaded:
        subprocess.run(f"awk '{{print $1,$2,$3,$4}}' {i}_df.txt > genome_index_geneID.txt", shell=True, executable="/bin/bash")

    escaped_t = "\t".encode('unicode_escape').decode("utf-8")
    for i in downloaded:
        subprocess.run(f"awk -v OFS='{escaped_t}' '$1=$1' genome_index_geneID.txt > genome_index_geneID_tab.txt", shell=True, executable="/bin/bash")
    
    #Clean unnecesary files for further steps.
    cl.clean_genomeID()

def run_r_script(downloaded):
    """
    Función que ejecuta un script en R con múltiples archivos para obtener información estadistica de los archivos.

    Parameters
    -----------
    downloaded: list(str).
    Lista de archivos.
    """
    print("------------------------------------------------------------")
    print("[+]Extrayendo las secuencias más largas...")
    subprocess.run("R CMD BATCH 8.Script_LargestSecs_Allsppecies.R", shell=True, executable="/bin/bash")
    for i in downloaded:
        subprocess.run(f"xargs samtools faidx {i} < {i}.faiLS.txt > {i}.LS.fasta",shell=True,executable="/bin/bash")

def orthofinder(tree):
    """
    Función que corre el proyecto OrthoFinder de github para crear árboles.

    Parameters
    -----------
    tree: file
    Archivo que contiene el árbol para ejecutar OrthoFinder con él.
    """
    print("------------------------------------------------------------")
    print("Ejecutando Orthofinder...")
    subprocess.run("ulimit -n 20000", shell=True, executable="/bin/bash")

    if not tree:
        subprocess.run("python3 OrthoFinder/orthofinder.py -t 12 -f ./", shell=True, executable="/bin/bash")
    else:
        subprocess.run(f"python3 OrthoFinder/orthofinder.py -t 12 -f ./ -s {tree}", shell=True, executable="/bin/bash")

def main(url_list, tree):

    #Mensaje de inicio al programa general.
    welcome_message()
    #Función que verifica el entorno necesario para que el programa funcione.
    check_dependencies()
    cl.delRData()


    #Función que descarga los archivo faa de internet y los guarda.
    print("------------------------------------------------------------")
    print("Descargando los arhivos de NCBI puede tardar mucho tiempo... ")
    download = [download_file(url.strip()) for url in process_csv(url_list)]
    logort.logging("Descargados todos los archivos, continuando...")

    #Función que renombra los archivos descargados de internet, con nombres que el usuario quiera poner.
    print("------------------------------------------------------------")
    print("Modificando el nombre de los archivos de NCBI... ")
    downloaded = corrije_download(download,obtener_nombres_csv(url_list))
    logort.logging("Modificados todos los archivos con los nombres que el usuario quiera, continuando...")

    #Función que aplica samtools a los archivos con nombres distintos para procesar su información.
    print("------------------------------------------------------------")
    print("Aplicando samtools a los archivos... ")
    downloaded = pasos_samtools(downloaded)
    logort.logging("Se terminó de aplicar samtools a los archivos renombrados.")

    # Función que aplica grep y awk a los archivos renombrados para obtener indices de genes relevantes.
    print("------------------------------------------------------------")
    print("Aplicando grep y awk a los archivos...")
    grep_and_awk(downloaded)
    logort.logging("Se terminó de aplicar grep y awk a los archivos...")

    #Función que aplica grep y awk de nuevo para obtener indices relevantes.
    print("------------------------------------------------------------")
    print("Obteniendo índices necesarios... ")
    extract_indices(downloaded)
    logort.logging("Se obtuvieron los índices necesarios, continuando...")

    #Se termina de ejecutar el archivo de R.
    print("------------------------------------------------------------")
    print("Obteniendo las secuencias más largas... ")
    run_r_script(downloaded)
    logort.logging("Se ejecutó el archivo en R...")
    
    # #Se ejecuta orthofinder sobre los archivos creados y relevantes.
    # logort.logging("Se ejecuta orthofinder...")
    # orthofinder(tree)
    # logort.logging("Se ejecutó correctamente orthofinder...")

if __name__ == "__main__":
    if "--url-list" not in sys.argv:
        print("[+]Falta parámetro --url-list")
        print("-------------------------------------")
        usage()
    url_list_index = sys.argv.index("--url-list") + 1
    url_list = sys.argv[url_list_index]

    tree_index = sys.argv.index("--ortho-three") + 1 if "--ortho-three" in sys.argv else None
    tree = sys.argv[tree_index] if tree_index is not None and tree_index + 1 < len(sys.argv) else None
    try:
        main(url_list, tree)
    except Exception as e:
        print("------------------------------------------------------------")
        print("Exception detected please review /tmp/Orthifinder/logs for more information")
        logort.logging(e)