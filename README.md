# cleandata.py by dp24
---
Code Style Check: ![Python application](https://github.com/DLBPointon/gEVAL_cleaner/workflows/Python%20application/badge.svg?branch=master)
Does the Script Run: ![automated_script_runner](https://github.com/DLBPointon/gEVAL_cleaner/workflows/automated_script_runner/badge.svg?branch=master) - Still requires a final check to test for contents of folders.

---
### Usage instructions
./cleandatav3.py -TYPE cdna -FTP ftp://ftp.ensembl.org/pub/release-98/fasta/mesocricetus_auratus/cdna/Mesocricetus_auratus.MesAur1.0.cdna.all.fa.gz -SAVE ./test

-------------
#### Args

- t = -TYPE 	cdna, pep, cds.
- s = -SAVE 	Save location for the file structure.
- f = -FTP 	Full ftp address.
- c = --clean 	Clean all unneeded files.
--------------

