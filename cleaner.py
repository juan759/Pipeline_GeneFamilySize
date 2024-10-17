#!/usr/bin/python3

import sys
import subprocess
import os

def clean_gz():
    subprocess.run("rm *.gz", shell=True, executable="/bin/bash")
    subprocess.run("rm .RData", shell=True, executable="/bin/bash")

    print("Removed gz(compressed) files.")


def clean_step5():
    subprocess.run("rm *_1.txt", shell=True, executable="/bin/bash")
    subprocess.run("rm *_2.txt", shell=True, executable="/bin/bash")
    subprocess.run("rm *_3.txt", shell=True, executable="/bin/bash")
    print("Removed unnecesary text files.")

def clean_genomeID():
    subprocess.run("rm genome_index_geneID.txt", shell=True, executable="/bin/bash")
    print("Removed genomes index.")