# cleandata.py by dp24
---
Code Style Check: ![Python application](https://github.com/DLBPointon/gEVAL_cleaner/workflows/Python%20application/badge.svg?branch=master)

Does the Script Run: ![automated_script_runner](https://github.com/DLBPointon/gEVAL_cleaner/workflows/automated_script_runner/badge.svg?branch=master) - Still requires a final check to test for contents of folders.

---
### Usage instructions
./cleandatav3.py ftp://ftp.ensembl.org/pub/release-98/fasta/mesocricetus_auratus/cdna/Mesocricetus_auratus.MesAur1.0.cdna.all.fa.gz ./ cdna

-------------
#### Args

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

--------------

