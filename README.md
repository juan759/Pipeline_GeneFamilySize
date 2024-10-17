# Pipeline_GeneFamilySize
## Introduction
This project encompasses a comprehensive pipeline designed to facilitate the creation process of obtaining the size of family genes. It involves providing a list of URLs to download genomes from NCBI and subsequently generate family trees and process genes.
## Installation
### Local
Clone the repository to your machine and start using the project, the main function is located at "SSD_genefamilysize.py". Ensure the system has python>=3.9.x.

The tools necessary for the pipeline to run smoothly are samtools, awk, grep, curl, gzip and the project Orthofinder(https://github.com/davidemms/OrthoFinder.git).

NOTE:Using this installation method you might need to change the working directory for the R script to the full path or wherever you downloaded the project or where you are going to save the python files. You might need to change the path of the command that executes the orthofinder project this is in the line 208(if you want to use a specific .tre file) or line 210(if you don't want to use any specific .tre file).

### Docker
Alternatively you can clone the repository, and use the Dockerfile attached to build an image and use the project inside that image.

For this you will need to first create an image with the docker file:

```
sudo docker build . -t orthofind
```

then after the image has been created over the dockerfile you can spawn an interactive tty shell with /bin/bash. This is possible  because the Docker image works on an Ubuntu Image:

```
sudo docker run --name orthofind --interactive --tty orthofind /bin/bash
```

this will spawn a new shell and you will be able to find the files for the project in the "/home/orthofind" directory.

## Usage
Run the Python script. If any required flags or parameters are missing, the script will print the usage and examples. While running, the script will print the stage it currently is and the process it is currently running. The url list must be a '.csv' file. Any other file extension can't be used and processed by the tool.

### Url list by a CSV file
The .csv file must contain the columns "Names" and "NCBI Link", and this last column only includes the url's for the specific ".gz" genome files from the NCBI database. The "Names" column will contain the name of the species the ".gz" belongs to. Any other column will be ignored. An example can be found in the "genomes.csv" file.

The script accepts two parameters, one optional and one required:

--url-list(Required): A text or csv file containing URLs for the NCBI genomes to be downloaded.

--ortho-tree(Optional): A tree file (in the "tre" format) specifying the tree to be utilized in the processing.

# Usage Examples:
```
python3 SSD_genefamilysize.py --url-list genomes.csv
```
```
python3 SSD_genefamilysize.py --url-list genomes.csv --format-list csv --ortho-three Mammalia_tree_130spp_plosOne_timetree_addedTips.tre
```
