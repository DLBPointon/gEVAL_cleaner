# cleandata.py by dp24

## Development Diary

### Usage instructions
./cleandata.py -TYPE cdna -ORG  mesocricetus_auratus -SAVE ./test

--------------

### 10/01/2020
- Changed README so that the newest change is at the top.
- seqclean - rewritten thanks to a better unstanding of the original seqclean script - not finished.
- decompress has stopped working - in process of rewritting.
- Considering rewritting downandsave to accept ftp address.
- Enteries needs a rewrite so that the file outputs are saved in a 'type'.all.fa
- possibly change save file generation to reduce the number of nested folders.

### 20/12/19
- Fixed the entry functions issue with numbers of entries per file - indentation error.
- Completed massage() but there is an error where it will break a dozen files in.
- rm_redundants() has been added to.
- seqclean() will take some time to understand as well as understand the resulting files.
- Added to command structure.

### 19/12/19
- decompress() fixed, used the simpler gunzip method rather than importing modules specifically for the task.
#### Update 2
- Expanded the folder directory creater so that it doesn't throw a false error if the folder already exists.
- Changed argument layouts for consistancy.
- Changed entryfunction to use option.prefix as an optional argument to specify the name of the produced entry files.
#### Update 3
- entryfunction() now working propperly.
	- Indentation Errors.
	- Expanded to include massage function.
		- Currently not working.
	- File locating Error.
- Addition of function __docs__.
- Made a start on massage().
- Made a start on rm_redundants().
- Made changes to account for the fact that ncrna files do not contain .all.fa.gz and instead are .ncrna.fa.gz.
- NCRNA Will need reworking as data comes from RefSeq not ensembl.
- fleshed out more plans for the script.
- Attempting regex.

### 18/12/19
- Used the entry splitted from previous project (fastaparsing).
- Fleshed out most of the functions with a general pseudo-code.
- Added the addition of a directory structure to make downstream sorting easier, e.g. logs go to a log folder and .clean files to another etc.
- Removed some modules for compataility with farm5.
- Simplified with use of os module.
- downandsave() works - downloads all.fa.gz and mv's to a downloaded folder (/gEVAL_cleaner/cleaning_data/downloaded/).
- decompress() semi-functional - a file is decompressed but unfortunately the output is corrupted.

### 12/12/19
- Added basic argparse command structure.
- Added functions:
	- main()
	- downandsave()
	- decompress()
	- read_fasta()
	- entryfunction()
	- seqclean()
	- massage()
	- rm_redundants()
- Each function has basic outline of duties.

### 10/12/19
- Started basic outline of script and master __doc__.

### 11/12/19
- Added Sanity checking and python version checks.