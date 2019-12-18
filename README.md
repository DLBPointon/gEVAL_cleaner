# cleandata.py by dp24

## Development Diary

### 11/12/19
- Added Sanity checking and python version checks.

### 10/12/19
- Started basic outline of script and master __doc__.

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

### 18/12/19
- Used the entry splitted from previous project (fastaparsing).
- Fleshed out most of the functions with a general pseudo-code.
- Added the addition of a directory structure to make downstream sorting easier, e.g. logs go to a log folder and .clean files to another etc.
- Removed some modules for compataility with farm5.
- Simplified with use of os module.
- downandsave() works - downloads all.fa.gz and mv's to a downloaded folder (/gEVAL_cleaner/cleaning_data/downloaded/).
- decompress() semi-functional - a file is decompressed but unfortunately the output is corrupted.
