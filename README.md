# cleandata.py by dp24
A python update to a bash script inuse in a GRIT pipeline

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
