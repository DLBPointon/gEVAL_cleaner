# clean_data.py by dp24
---
Code Style Check:![Python application](https://github.com/DLBPointon/gEVAL_cleaner/workflows/Python%20application/badge.svg?branch=master)

Does the Script Run - long commands:![automated_script_runner](https://github.com/DLBPointon/gEVAL_cleaner/workflows/automated_script_runner/badge.svg?branch=master) - Still requires a final check to test for contents of folders.

Does the Script Run - short commands: ![Short FTP - Still needs work](https://github.com/DLBPointon/gEVAL_cleaner/workflows/Short%20FTP%20-%20Still%20needs%20work/badge.svg?branch=master) - Still requires a final check to test for contents of folders.

In-Depth changes are found in the Wiki section.

---
### Usage instructions

PLEASE BE AWARE THAT THIS RELEASE IS SPECIFIC FOR __***ensemblgenomes.org release-46***___ AND ___***ensembl.org release-99***__

-------------------------------------------------------------
USAGE INSTRUCTIONS

./clean_data.py {FTP} {SAVE} {pep, cds, cdna}
                 [--clean]

Any number of TYPE flag may be specified e.g.
pep, cds and cdna can all be called.
- Example:
./clean_data.py arabidopsis_thaliana+plants ./save pep cds cdna

FTP can be either:
- The full ftp address for example:
        ftp://ftp.ensemblgenomes.org/pub/release-46/
        plants/fasta/arabidopsis_thaliana/cdna/
        Arabidopsis_thaliana.TAIR10.cdna.all.fa.gz

- Or organism name + org type in the style of:
        arabidopsis_thaliana+plants

This +plants refers to the ensemblgenomes directory so this can be:
- +plants
- +metazoa
- +protists
- +fungi
- +bacteria

If org is not in ensemblgenomes then use:
- +ensembl

This will tell the script so search ftp.ensembl.org not ftp.ensemblgenomes.org

./clean_data.py ftp://ftp.ensembl.org/pub/release-99/
                fasta/mesocricetus_auratus/cdna/
                Mesocricetus_auratus.MesAur1.0.cdna.all.fa.gz
                ./test cdna

or

./clean_data.py mesocricetus_auratus+ensembl ./test cdna

This creates a much cleaner look when calling the script.


-------------------------------------------------------------

Positional arguments:
- FTP                      This argument is to be used when using an ftp address
                           for this script
- SAVE                     Save location for the downloaded files
- TYPE/{cds,cdna,pep}      The type of DATA contained in the file, any number of these can be chosen.

Optional arguments:
- h, --help          show this help message and exit
- v, --version       show program's version number and exit
- c, --clean         Specifying this argument allows the script to clean all
                     un-necessary files after use
