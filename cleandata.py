#!/usr/bin/env python

import sys
if sys.version_info[0] < 3 and sys.version_info[1] < 7:
    raise Exception("""Must be using Python 3.7 for the full
                    functionality of this script""")
if sys.version_info[0] >= 3 and sys.version_info[1] >= 7:
    print('Your using at least Version 3.7, You are good to go...')

PRINT_ERROR = '''Does not exist\n
                 Get module installed before import attempt\n
                 If running server side then contact your admin'''
try:
    import argparse
    print('argparse imported')
except ImportError:
    print('argparse not imported')
    print(PRINT_ERROR)
    sys.exit(0)

try:
    import os
    print('os imported')
except ImportError:
    print('os not imported')
    print(PRINT_ERROR)
    sys.exit(0)

try:
    import glob2
    print('glob2 imported')
except ImportError:
    print('glob2 not imported')
    print(PRINT_ERROR)
    sys.exit(0)

try:
    import wget
    print('wget imported')
except ImportError:
    print('wget not imported')
    print(PRINT_ERROR)
    sys.exit(0)

import gzip
import shutil
import delegator

'''Please use ./cleandata.py -h for the full __doc__'''

DOCSTRING ="""
-------------------------------------------------------------
        Clean_gEVAL_supporting_DATA
-------------------------------------------------------------
        Also known as cleandata.py
            By dp24
    Updated from wc2's clean_gEVALsupport_data.sh
-------------------------------------------------------------
    IMPORTANT NOTES BEOFRE CARRYING ON
This script is written in python 3.7 although it should be 
        possible to run on 3.6.

          IMPORT MODULES

            arg.parse
            os
            sys
            glob2
            shutil
            contextlib
            urllib2
-------------------------------------------------------------

USE CASE FOR THE SCRIPT
1, The aim of this script is to take an input FASTA file
(whether cdna/cds/pep or rna) from ensembl or refseq.

2, Next the headers will be massaged into a standardised
format.

3, The sequence will then be cleaned by the use of the
seqclean script.

4, Sequences are then trimmed.

5, Finally the sequences are split into user defined entries
per file.

-------------------------------------------------------------

USAGE INSTRUCTIONS
 ./cleandata.py [-FASTA input], [-type], [-prefix], [--clean]

 - FASTA - will be the input FASTA File

 - Type - will be a choice between cdna/cds/pep/rna

 - Prefix - will be the user defined naming scheme
 
 - Clean - and optional argument to remove parent files

-------------------------------------------------------------

FUTURE CHANGES
    - Change input file to top level directory where -type 
    then specifies the file to be scrapped.

-------------------------------------------------------------
CONTACT
    - dp24@sanger.ac.uk

-------------------------------------------------------------

"""


def parse_command_args(args=None):
    """
    A function to verify the command line arguments to be passed
    to the rest of the script.
    """
    descformat = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(prog='Clean the gEVAL Supporting DATA',
                                     formatter_class=descformat,
                                     description=DOCSTRING)

    parser.add_argument('-v', '--version',
                        action = 'version',
                        version = '%(prog)s Alpha 1.0')

    parser.add_argument('-FASTA',
                        type = str,
                        action = 'store',
                        help = 'The path for the FASTA input')

    parser.add_argument('-TYPE',
                        type = str,
                        choices=['cds', 'cdna', 'pep', 'ncrna'],
                        help = 'The type of DATA contained in the file',
                        required = True)

    parser.add_argument('-PREFIX',
                        type = str,
                        action = 'store',
                        help = 'User-defined naming scheme',)

    parser.add_argument('-ENTRIES',
                        type = int,
                        action = 'store',
                        help = 'User-defined number of entries per file')

    parser.add_argument('-ORGNAME',
                        type = str,
                        action = 'store',
                        help = '''The Organism under scrutiny 
                                  (use how the name would appear in ensembl
                                  to make life easier, long name)''',
                        required = True,
                        dest = 'org')

    parser.add_argument('-SAVE',
                        type = str,
                        action = 'store',
                        help = 'Save location for the downloaded files',
                        required = True)

    parser.add_argument('--clean',
                        action = 'store_true',
                        help = 'Specifying this argument, ')

    option = parser.parse_args(args)
    return option



def main():

    directlist = ['/cleaning_data', '/cleaning_data/entries', '/cleaning_data/downloaded',
                  '/cleaning_data/logs', '/cleaning_data/cleaned']
    accessrights = 0o755

    option = parse_command_args()

    if option.org:
        for direct in directlist:
            path = option.SAVE + direct
            try:
                os.makedirs(path, accessrights)
            except OSError:
                print(f'Creation of directory has failed at: {path}')
            else:
                print(f'Successfully created the directory path at: {path}')

    
        if option.org and option.TYPE:
            print('Lets do stuff')

            full_address = downandsave(option.org, option.TYPE, option.SAVE)

            # fileout = decompress(full_address, option.SAVE, option.org, option.TYPE)

            # entryfunction(fileout, naming, op.TYPE)

        # Then for the files saved from entryfunction
        # send each one to Seqclean


def downandsave(orgname, datatype, save):
    FTP_ADDRESS = 'ftp://ftp.ensembl.org/pub/release-98/fasta/'
    file_end = '.all.fa.gz'
    full_address = f'{FTP_ADDRESS}{orgname}*{datatype}{file_end}'
    print(full_address)

    filetodecomp = delegator.run(f'wget -P {save}/cleaning_data/downloaded/ {full_address}')

    return filetodecomp


def decompress(full_address, save, orgname, datatype):
    newfile = f'{save}/cleaning_data/downloads/{orgname}-{datatype}.fa'
    with open(newfile, 'w') as filein:
        with gzip.open(full_address, 'r') as fileout:
            shutil.copyfileobj(filein, fileout)

    return fileout


def read_fasta(fileout):
    """A function which opens and splits a fasta into name and seq"""
    name, seq = None, []
    for line in fileout:
        line = line.rstrip()
        if line.startswith(">"):
            if name:
                yield (name, ''.join(seq))
            name, seq = line, []
        else:
            seq.append(line)
    if name:
        yield (name, ''.join(seq))


def entryfunction(filein, naming, datatype='pep'):
    """The entryfunction function splits a FASTA file into a user defined
    number of entries per file"""
    if datatype == 'pep':
        print('peptide datatypes split at 2000 entries per file')
        entryper = 2000
    else:
        print('CDs, cDNA and RNA all split at 5000 entries per file')
        entryper = 5000

    count = 0
    filecounter = 0
    entry = []

    FO += '/fastaparsed/entries/'

    with open(FI) as filetoparse:
        for name, seq in read_fasta(filetoparse):
            nameseq = name, seq
            entry.append(nameseq)
            count += 1

            if count == entryper:
                filecounter += 1

                with open(f'{FO}{naming}{filecounter}.fa', 'w') as done:
                    print(f'Find your file at: \n {FO}entry{filecounter}.fa')
                    for idss, sequence in entry:
                        done.write(f'{idss} {sequence} \n\n')

                    count = 0
                    entry = []

        filecounter += 1
        with open(f'{FO}{naming}{filecounter}.fa', 'w') as done:
            print(f'Find your file at: \n {FO}entry{filecounter}.fa')
            for idss, sequence in entry:
                done.write(f'{idss} {sequence} \n\n')

            entry = []


def seqclean():
    # Send to wc2 seqclean perl script
    # Can use envoy or sys
    seqclean_v_check = '/nfs/users/nfs_w/wc2/tools/seqclean -v'
    entr_file_loc = [] # for all files in the location for the entry folder
    run_seqclean = delegator.run('bsub -o cleanplease.out -K seqlean')
    else_run = delegator.run('bsub -o cleanplease.out -K /nfs/users/nfs_w/wc2/tools/seqclean')

    for file in entr_file_loc:
        if seqclean_v_check:
            run_seqclean + file
        if seqclean_v_check == False:
            else_run + file
        else:
            print('Failed to run')
            sys.exit(0)


def massage():
    for header, seq in entry:
        print(header)
        #Use regex to get string segment at gene name to label the header 


def rm_redundants():
    print('x')
    # rm the now useless files


if __name__ == '__main__':
    main()
