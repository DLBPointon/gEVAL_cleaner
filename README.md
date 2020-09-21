# clean_gEVAL_data.py by dp24
---
In-Depth changes are found in the Wiki section.

---
### Usage instructions

./clean_data.py {FTP} {SAVE} {FTP_TYPE [ncbi|ens]} {pep, cds, cdna} [-NAME] [--debug] [--clean]
-NAME is required when using ncbi data due to their naming scheme.


Ensembl Example:

./cleaning_gEVAL_data.py ftp://ftp.ensembl.org/pub/release-99/fasta/mesocricetus_auratus/cdna/Mesocricetus_auratus.MesAur1.0.cdna.all.fa.gz ./ ens cdna


NCBI Example:

./cleaning_gEVAL_data.py https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/184/155/GCF_000184155.1_FraVesHawaii_1.0/GCF_000184155.1_FraVesHawaii_1.0_protein.faa.gz ./ ncbi pep -NAME Fragaria_Vesca 

-------------------------------------------------------------


Positional Arguments:
|ARGUMENT|EXPLANATION| 
|---|---|
|  FTP  | This argument is to be used when using an ftp address for this script|
|  SAVE | Save location for the downloaded files|
|{ens,ncbi}| Specify the FTP|
|{cds,cdna,pep,rna}|The type of DATA contained in the file|
---------

Optional Arguments:

|ARGUMENT|EXPLANATION| 
|---|---|
|-h, --help |show this help message and exit.|
| -NAME NAME, --organism_ncbi NAME | If using ncbi FTP, then the organisms name must be provided due to how they name their files |
|-v, --version|show program's version number and exit|
|-c, --clean|Specifying this argument allows the script to clean all un-necessary files after use|
|-d, --debug |Specifying this argument allows debug prints to workand creates a log file documenting everything the script does.|
--------

---
### Acknowledgements

Seqclean has not been written by my self, it was pridced by the Dana-Farber Cancer Institute and used in GRIT operations.
