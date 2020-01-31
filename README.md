# cleandata.py by dp24

## Development Diary

### Usage instructions
./cleandatav3.py -TYPE cdna -FTP ftp://ftp.ensembl.org/pub/release-98/fasta/mesocricetus_auratus/cdna/Mesocricetus_auratus.MesAur1.0.cdna.all.fa.gz -SAVE ./test

-------------
#### Args

- t = -TYPE 	cdna, pep, cds.
- s = -SAVE 	Save location for the file structure.
- f = -FTP 	Full ftp address.
- c = --clean 	Clean all unneeded files.
--------------

### To-Do list
- Fix bugs.
- Add readme for stats.
--------------
### 30/01/2020


### 29/01/2020
- Script working.
    - Scans working directory for .clean file to then run that file through the entryfunction.
- Script now accepts all data types.
- Added the Time module to allow for the directory scanning.
- Confirmed working on all data types and with the file structure.
#### Update 2
- Added regex options for metazoans and insects.
- Corrected rm_redundants - addition of extensions and major simplification thanks to simplifying file structure.

Known Bugs:
- For cdna files the script must be interrupted twice and then allowed to run, the cause is currently unknown.
- Occasionally other data types will fail for no reason and need to be re-run.

### 24/01/2020
- Begin work on implementing the seqclean function.

### 23/01/2020
- Entries now being produced for v3 script.
- Place holder terms for testing have been changed to widely useful terms.
- Added FTP argument for full FTP address input.
- Added function Doc Strings.
- Added globally controlled logging statements to minimise duplicate script.
- Added argument dest.
- Added placeholder for Seqclean.
- Added cleaning function.
- Added comment to explain regex use.
- Addition of Logging statements for debugging rather than innumerable print functions.
- Expanded on os.popen blocks - gunzip - mv and rm.

### 22/01/2020
- Changing save structure to align with house style.
- More use of regex to accomplish individualised file structure for each organism.
- Start on cleandatav3.py - recycling much of v2.
- Implemented the logging module for easier debugging management.

### 21/01/2020
- Removed various errors in structure (too many spaces and gaps.
- Changed Quotes so that doubles are used for doc_strings rather than singles.
- Fixed an error with regex where too many MissingInfo's were being assigned.
- Fixed an error where the final file produced by the entryfunction does not include any massaged headers.
- Fixed an error where regex was assigning None to a new_name where length was 2 characters or less.
- Fixed regex issue where the gene ens_code would be terminated too early in some cases.
- Removal of redundant code.


### 17/01/2020
- Removed excessive use of the "\n" character to match "house style".
	- {header}\n\n{sequence} rather than {header}\n{sequence}.
- File save formatting fixed (too many .).
	- {name}.all.MOD.fa rather than {name}..all.MOD.fa
- File save formatting fixed (too few .).
	- {name}.MOD.fa rather than {name}MOD.fa
- Entryper fix )to stop multi all files.
- cdna has been changed to an entryper of 5000.
- Changed executable settings for cleandatav2.py.

#### Update 2
- Bug where script needs to be run 4 times to complete task.

### 16/01/2020
- Test runs were failing due to a missing function call in a next of if branches.
	- Added the missing new_name = massage(name, data_type).
- Series of Syntax and grammar changes to improve functionality.
- Added a third missing gene symbol catch as a just in case (possiblity was caught in the failing tests).
- 

### 15/01/2020
- Fixed the impropper use of seqclean in entry function.
- Added debug feature.
- Changed up the ./cleandata.py -h.
- Fixed more spelling, grammar and syntax errors.
- Addition of numberous print() functions to aid debugging.
- Added Folder tree showing the produced file structure.
- Changed rm_redundants.
- PyCodeStyle Fixes.
- PyLint score of 8.83.
- DOCS updated.
- Re-ordered entry function.
- Changed position of rm_redundant function calling.

### 14/01/2020
- Fixed the renaming of enteries as master file is split.
- Script now takes a ftp ensembl link as input as well as the organism name as it would appear on the website
e.g. genus_species.
	- Uses Regex to pull out a organism name.
- Fixed spelling and syntax errors.
- Fixed Regex errors.
- Majority PyCodeStyle compliant.
- PyLint 8.12 - Due to unfinished nature of script.
- Files are now saved in the format orgname-type-genecounterMOD.fa.
- DOCS Updated.
- Reordered script to help it make more sense.
- Updates to README in the form of Usage instructions and to do list.

### 10/01/2020

#### Update 1
- Changed README so that the newest change is at the top.
- seqclean - rewritten thanks to a better unstanding of the original seqclean script - not finished.
- Decompress has stopped working - in process of rewritting.
- Considering rewritting downandsave to accept ftp address.
- Enteries needs a rewrite so that the file outputs are saved in a 'type'.all.fa
- Possibly change save file generation to reduce the number of nested folders.

#### Update 2
- Added decompress to main()
- Changed args for easier use in command
	- t = -TYPE
	- s = -SAVE
	- o = -ORGNAME
	- p = --prefix
	- c = --clean
- Changed the entry function type checking method so it is more comprehensive although more complex.
- Simplified decompress - unnecessary complexity.

#### Update 3
- Fixed decompress issue.
- Massaging step is now finding missing gene_symbols.

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
- downandsave() works - downloads all.fa.gz and mv's to a downloaded folder (/'User-defined'/cleaning_data/downloaded/).
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
