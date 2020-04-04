# cleandata.py by dp24
---
Code Style Check: ![Python application](https://github.com/DLBPointon/gEVAL_cleaner/workflows/Python%20application/badge.svg?branch=master)

Does the Script Run: ![automated_script_runner](https://github.com/DLBPointon/gEVAL_cleaner/workflows/automated_script_runner/badge.svg?branch=master) - Still requires a final check to test for contents of folders.

---
### Usage instructions

PLEASE BE AWARE THAT THIS RELEASE IS SPECIFIC FOR __***ensemblgenomes.org release-46***___ AND ___***ensembl.org release-99***__

./cleandatav3.py {FTP} {SAVE} {pep, cds, cdna, all}
                 [--clean] [--debug] [--time]

FTP can be either:
- The full ftp address for example:
        ftp://ftp.ensemblgenomes.org/pub/release-46/plants/fasta/arabidopsis_thaliana/cdna/
        Arabidopsis_thaliana.TAIR10.cdna.all.fa.gz

- Or organism name + org type in the style of:
        arabidopsis_thaliana+plants
        
This +plants refers to the ensemblgenomes directory

so this can be:

+plants

+metazoa

+protists

+fungi

+bacteria

If org is not in ensemblgenomes then use:

+ensembl

This will tell the script so search ftp.ensembl.org not ftp.ensemblgenomes.org

./cleandatav3.py ftp://ftp.ensembl.org/pub/release-98/fasta/mesocricetus_auratus/cdna/Mesocricetus_auratus.MesAur1.0.cdna.all.fa.gz ./test cdna

or

./cleandata mesocricetus_auratus+ensembl ./test cdna

This creates a such cleaner look when calling the script.

-------------

positional arguments:
  FTP                 This argument is to be used when using an ftp address
                      for this script
  SAVE                Save location for the downloaded files
  {cds,cdna,pep,all}  The type of DATA contained in the file

optional arguments:
  -h, --help          show this help message and exit
  -v, --version       show program's version number and exit
  -c, --clean         Specifying this argument allows the script to clean all
                      un-necessary files after use
  -d, --debug         Specifying this argument allows debug prints to work and
                      show everything the script is doing
  -t, --time          A flag to check the run time of the script


