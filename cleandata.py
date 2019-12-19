#!/usr/bin/env python3

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


'''Please use ./cleandata.py -h for the full __doc__'''

DOCSTRING = """
-------------------------------------------------------------
        Clean_gEVAL_supporting_DATA
-------------------------------------------------------------
        Also known as cleandata.py
            By dp24
    Updated from wc2's clean_gEVALsupport_data.sh
-------------------------------------------------------------
    IMPORTANT NOTES BEOFRE CARRYING ON
This script is written in for python3.6

          IMPORT MODULES

            arg.parse
            os
            sys
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

 - Organism Name - the name of the orgnaism as it looks in
 the respective database.

 - Save - The directotry to save all files



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

    parser.add_argument('-TYPE',
                        type = str,
                        choices=['cds', 'cdna', 'pep', 'ncrna'],
                        help = 'The type of DATA contained in the file',
                        required = True,
                        dest = 'ty')

    parser.add_argument('--prefix',
                        type = str,
                        action = 'store',
                        help = 'User-defined naming scheme',
                        dest = 'pre')

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
                        required = True,
                        dest = 'sv')

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
            path = option.sv + direct
            if os.path.exists(path):
                print(f'Path: {path} :already exists')
            else:
                try:
                    os.makedirs(path, accessrights)
                except OSError:
                    print(f'Creation of directory has failed at: {path}')
                else:
                    print(f'Successfully created the directory path at: {path}')

    
        if option.org and option.ty:
            print('Lets do stuff')

            downandsave(option.org, option.sv, option.ty)

            entryfunction(option.org, option.sv, option.pre, option.ty)

            seqclean()

            rm_redundants()
        # Then for the files saved from entryfunction
        # send each one to Seqclean


def downandsave(org, sv, ty = 'pep'):
    """
    A function to dowload a user defined file and mv it into the
    downloaded folder.
    """
    if ty == 'ncrna':
        file_end = '.fa.gz'
    else:
        file_end = '.all.fa.gz'
    FTP_ADDRESS = f'''ftp://ftp.ensembl.org/pub/release-98/fasta/
                      {org}/{ty}/*{ty}{file_end}'''
    downloadloc = f'{sv}/cleaning_data/downloaded/'
    
    download = os.popen(f'''wget -q -o /dev/null ftp://ftp.ensembl.org/pub/release-98/fasta/{org}/{ty}/*{ty}{file_end}''')

    movetodirect = os.popen(f'''mv *{file_end} {downloadloc}''')


def decompress(org, sv, ty = 'pep'):
    """
    A function to decompress the downloaded file from downandsave().
    """
    if ty == 'ncrna':
        file_end = '.fa.gz'
        file_uncomp = '.fa'
    else:
        file_end = '.all.fa.gz'
        file_uncomp = '.all.fa'
    newfile = f'{sv}/cleaning_data/downloaded/{org}-{ty}{file_uncomp}'
    directory = f'{sv}/cleaning_data/downloaded/'
    for file in os.listdir(directory):
        if file.endswith(f'.{ty}{file_end}'):
            unzipper = os.popen(f'gunzip {directory}{file_end}')
    return unzipper

def read_fasta(filetoparse):
    """
    A function which opens and splits a fasta into name and seq.
    """
    name, seq = None, []
    for line in filetoparse:
        line = line.rstrip()
        if line.startswith(">"):
            if name:
                yield (name, ''.join(seq))
            name, seq = line, []
        else:
            seq.append(line)
    if name:
        yield (name, ''.join(seq))


def entryfunction(org, sv, pre = 'OrgOfInt', ty = 'pep'):
    """
    The entryfunction function splits a FASTA file into a defined
    number of entries per file, pep == 2000 enteries and everything
    else is split into 5000 enteries.
    """
    if ty == 'pep':
        print('peptide datatypes split at 2000 entries per file')
        entryper = 2000
    else:
        print('CDs, cDNA and RNA all split at 5000 entries per file')
        entryper = 5000

    if ty == 'ncrna':
        file_uncomp = '.fa'
    else:
        file_uncomp = '.all.fa'


    count = 0
    filecounter = 0
    entry = []

    filesavedto = f'{sv}/cleaning_data/entries/'
    directory = f'{sv}/cleaning_data/downloaded/'

    for file in os.listdir(directory):

        if file.endswith(file_uncomp):
            unzipped = f'{directory}{file}'

            if os.path.exists(unzipped):
                print('It\'s a valid address')
            else FileNotFoundError:
                print('Cannot find the file, check the folders')

            with open(unzipped,'r') as filetoparse:
                for name, seq in read_fasta(filetoparse):
                    name = massage(name)
                    print('Cleaning the headers')
                    if ty == 'dna':
                        seq = seqclean(seq)
                        print('Cleaning the dna sequences')

                    nameseq = name, seq
                    entry.append(nameseq)
                    count += 1

                    if count == entryper:
                        filecounter += 1

                        with open(f'{filesavedto}{pre}-{filecounter}.fa', 'w') as done:
                            print(f'Find your file at: \n {filesavedto}{pre}-{filecounter}.fa')
                            for header, sequence in entry:
                                done.write(f'{header} {sequence} \n\n')

                            count = 0
                            entry = []

                    filecounter += 1
                    with open(f'{filesavedto}{pre}-{filecounter}.fa', 'w') as done:
                        print(f'Find your file at: \n {filesavedto}{pre}-{filecounter}.fa')
                        for header, sequence in entry:
                            done.write(f'{header} {sequence} \n\n')

                        entry = []

-----------------------
def seqclean(seq):
    """
    A function to sent entry split files to the seqclean perl script,
    this script will clean the sequence to ensure there is nothing that
    requires correcting.
    """
    # Send to wc2 seqclean perl script
    seqclean_v_check = '/nfs/users/nfs_w/wc2/tools/seqclean -v'
    run_seqclean = os.popen('bsub -o cleanplease.out -K seqlean')
    else_run = os.popen('bsub -o cleanplease.out -K /nfs/users/nfs_w/wc2/tools/seqclean')

    if ty == 'dna':

        for seq:
            if seqclean_v_check:
                run_seqclean + file
            if seqclean_v_check == False:
                else_run + file
            else:
                print('Failed to run')
                sys.exit(0)
    else:
        print('Seq clean skipped, only for DNA')

    return seq

def massage(name, ty):
    """
    A function to 'massage' the sequence headers into a more human readable style
    """
    if ty == 'ncrna'
        print('Damned NCBI RNA')

    else:
        print('Data from Ensembl')

        Need the gene symbol and the ENS code >symbol(ENS code)
        
        #Use regex to get string segment at gene name to label the header 

    return name

def rm_redundants(sv, clean):
    """
    A function to remove all redunant files, an optional 
    """
    dellogs = os.popen('rm ')

    needs to get rid of *log, *.cidx, *.cln, outparts*
    
    .clean files are what we need!!!!

    # rm the now useless files


if __name__ == '__main__':
    main()
