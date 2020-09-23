# cleaning_gEVAL_data.py by dp24
---
In-Depth changes are found in the Wiki section.

---
### Usage instructions

./cleaning_gEVAL_data.py {FTP} {SAVE} {FTP_TYPE [ncbi|ens]} {pep, cds, cdna} [-NAME] [-d, --debug] [-c, --clean] [-ep, --override_entryper]

-NAME is required when using ncbi data due to their naming scheme.


Ensembl Example:

./cleaning_gEVAL_data.py ftp://ftp.ensembl.org/pub/release-99/fasta/mesocricetus_auratus/cdna/Mesocricetus_auratus.MesAur1.0.cdna.all.fa.gz ./ ens cdna


NCBI Example:

./cleaning_gEVAL_data.py https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/184/155/GCF_000184155.1_FraVesHawaii_1.0/GCF_000184155.1_FraVesHawaii_1.0_protein.faa.gz ./ ncbi pep -NAME Fragaria_Vesca 

-------------------------------------------------------------
USE CASE FOR THE SCRIPT
1, The aim of this script is to take an input FASTA file
(whether cdna, cds, pep or rna) from ensembl or ncbi.

2, This is downloaded and Unzipped.

3, If Data type is cdna, seqclean is called (may have to
be modified for data sets with high N count).

4, File is read and Headers are split away from the
sequence and massaged into an easy read format.

5, New headers and sequence are merged and counted.
Once the count reaches a set number (for each data type)
a file is produced.

6, Finally folders can be cleaned and debug logs can be read
if needed.
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
|-ep, --override_entryper | Overrides to hard coded options to split various data types (defaults are cdna/5000, pep/200 and everything else 3000). |
--------

### Contacts

If you have any questions then contact:

dp24@sanger.ac.uk

or 

grit@sanger.ac.uk

Alternatively leave an issue on this repo.



---
### Acknowledgements

Seqclean has not been written by my self, it was produced by the Dana-Farber Cancer Institute and used in GRIT operations.
