#!/usr/bin/env python3

PRINT_ERROR = '''Does not exist\n
                 Get module installed before import attempt\n
                 If running server side then contact your admin'''

try:
    import sys
    if sys.version_info[0] < 3 and sys.version_info[1] < 7:
        raise Exception("""Must be using Python 3.7 for the full
                        functionality of this script""")
    if sys.version_info[0] >= 3 and sys.version_info[1] >= 7:
        print('Your using at least Version 3.7, You are good to go...')
except ImportError:
    print(f'sys not imported \n {PRINT_ERROR}' )
    sys.exit(0)

try:
    import argparse
    print('argparse imported')
except ImportError:
    print(f'argparse not imported \n {PRINT_ERROR}' )
    sys.exit(0)

try:
    import os
    print('os imported')
except ImportError:
    print(f'os not imported \n {PRINT_ERROR}' )
    sys.exit(0)

try:
    import re
    print('regex imported')
except ImportError:
    print(f're not imported \n {PRINT_ERROR}' )
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

            argparse
            os
            sys
            re

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
                        dest = 't')

    parser.add_argument('--prefix',
                        type = str,
                        action = 'store',
                        help = 'User-defined naming scheme',
                        dest = 'p')

    parser.add_argument('-ORGNAME',
                        type = str,
                        action = 'store',
                        help = '''The Organism under scrutiny 
                                  (use how the name would appear in ensembl
                                  to make life easier, long name)''',
                        required = True,
                        dest = 'o')

    parser.add_argument('-SAVE',
                        type = str,
                        action = 'store',
                        help = 'Save location for the downloaded files',
                        required = True,
                        dest = 's')

    parser.add_argument('--clean',
                        action = 'store_true',
                        help = 'Specifying this argument allows the script to clean all un-nessasery files after use',
                        dest = 'c')

    option = parser.parse_args(args)
    return option


def main():

    directlist = ['/cleaning_data', '/cleaning_data/entries', '/cleaning_data/downloaded', '/cleaning_data/logs', '/cleaning_data/cleaned', '/cleaning_data/dna_seqclean']
    accessrights = 0o755

    option = parse_command_args()



    if option.o:
        for direct in directlist:
            path = option.s + direct
            if os.path.exists(path):
                print(f'Path: {path} :already exists')
            else:
                try:
                    os.makedirs(path, accessrights)
                except OSError:
                    print(f'Creation of directory has failed at: {path}')
                else:
                    print(f'Successfully created the directory path at: {path}')

    
        if option.o and option.t:
            print('Lets do stuff')

            downandsave(option.o, option.s, option.t)

            decompress(option.s, option.t)

            entryfunction(option.o, option.s, option.p, option.t)

            # seqclean(seq, ty)
            
        if option.c:
            rm_redundants(option.s)
        # Then for the files saved from entryfunction
        # send each one to Seqclean


def downandsave(org, sv, ty):
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


def decompress(sv, ty):
    """
    A function to decompress the downloaded file from downandsave().
    """
    file_end = '.fa.gz'

    directory = f'{sv}/cleaning_data/downloaded/'
    filefinder = os.listdir(directory)
    for file in filefinder:
        if file.endswith(f'{file_end}'):
            unzipper = os.popen(f'gunzip {directory}*{file_end}')
            if file in filefinder.endswith('.fa'):
                print(file)


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


def entryfunction(org, sv, ty, pre = 'OrgOfInt'):
    """
    The entryfunction function splits a FASTA file into a defined
    number of entries per file, pep == 2000 enteries and everything
    else is split into 5000 enteries.
    """
    print('CDs, cDNA and ncRNA all split at 5000 entries per file')
    entryper = 5000

    typelist = ['pep', 'ncrna', 'cdna', 'cds']
    for type in typelist:
        if type == ty:
            if ty == 'pep':
                entryper = 2000
                print('Pep splits at 2000 per file')
            if ty == 'ncrna':
                file_uncomp = '.fa'
            else:
                file_uncomp = '.all.fa' 
        else:
            print(f'Is the file still compressed or is there an odd extention. \nLooking for \'.fa\' or \'.all.fa\'\nCheck your parent file in: {sv}/cleaning_data/downloads')

    count = 0
    filecounter = 0
    entry = []

    filesavedto = f'{sv}/cleaning_data/entries/'
    directory = f'{sv}/cleaning_data/downloaded/'

    for file in os.listdir(directory):

        if file.endswith('.fa'):
            unzipped = f'{directory}{file}'

            if os.path.exists(unzipped):
                print('CAN find the unzipped fasta')
            else:
                print('CANNOT find the unzipped fasta')

            with open(unzipped,'r') as filetoparse:
                for name, seq in read_fasta(filetoparse):
                    name = massage(name, ty)
                    print('Cleaning the headers')
                    if ty == 'dna':
                        seq = seqclean(seq)
                        print('Cleaning the dna sequences')

                    nameseq = name, seq
                    entry.append(nameseq)
                    count += 1

                    if count == entryper:
                        filecounter += 1

                        with open(f'{filesavedto}{org}-{filecounter}.fa', 'w') as done:
                            print(f'Find your file at: \n {filesavedto}-{org}-{filecounter}.fa')
                            for header, sequence in entry:
                                done.write(f'{header} {sequence} \n\n')

                            count = 0
                            entry = []

                    filecounter += 1
                with open(f'{filesavedto}{org}-{filecounter}.fa', 'w') as done:
                    print(f'Find your file at: \n {filesavedto}-{org}-{filecounter}.fa')
                    for header, sequence in entry:
                        done.write(f'{header} {sequence} \n\n')

                    entry = []


def seqclean(seq, ty):
    """
    A function to sent entry split files to the seqclean perl script,
    this script will clean the sequence to ensure there is nothing that
    requires correcting.
    """

    seqclean_v_check = '/nfs/users/nfs_w/wc2/tools/seqclean -v'
    run_seqclean = os.popen('bsub -o cleanplease.out -K seqlean')
    else_run = os.popen('bsub -o cleanplease.out -K /nfs/users/nfs_w/wc2/tools/seqclean')
    option = parse_command_args()
    path = f'{option.s}/cleaning_data/enteries'

    if ty == 'dna':
        if os.path.exists(path):
            print('Path to files found')
            for file in os.listdir(path):
                try:
                    set_script = os.popen(f'bsub -o cleanplease.out -M500 -R\'select[mem>500] rusage[mem=500]\' \\ ~wc2/tools/seqclean/seqclean {file}')
                except IOError:
                    print('Command or files are incorrect')

                result = set_script.read()
                res.close()
                print(f'Finished: {result}')
                # The above should start the perl script and then check to see if the script runs and finishes for each of the fiules passed onto it and then print the file it has finihsed working on
        else:
            print('File paths not found')
            sys.exit(0)


    else:
        print('Seq clean skipped, only for DNA')

    return seq


def massage(name, ty):
    """
    A function to 'massage' the sequence headers into a more human readable style
    """
    if ty == 'pep' or 'cds' or 'dna':
        print(f'This sequence is {ty} from ensembl.')

        if name.startswith('>'):
            gene_symbol = re.search(r'gene_symbol:(\w+)', name).group(0)
            ens_code = re.search(r'ENS(\w+.\d+)', name).group(1)
            name = f'> {gene_symbol} ({ens_code})'

    elif ty == 'ncrna':
        print('This is a RefSeq ncRNA sequecne, not coded for that yet.')

    else:
        print('Some how you\'ve got to this point with an incorrect data type')
        sys.exit(0)
    
    return name


def rm_redundants(sv):
    """
    A function to remove all redunant files, an optional 
    """
    print('remover')
    
    directlist = ['/cleaning_data', '/cleaning_data/entries', '/cleaning_data/downloaded', '/cleaning_data/logs', '/cleaning_data/cleaned']

    exten_dels = ['.log', '.cidx', '.cln', 'outparts']

    for direct in directlist:
        path = f'{sv}{direct}'
        for file in os.listdir(path):
            for extension in exten_dels:
                if file.endswith(extension):
                    if extension == '.clean':
                        mv_clean = os.popen('mv {sv}{directlist}{file} {sv}/cleaning_data/cleaned/')
                        del_redun = os.popen(f'rm {sv}{directlist}*{exten_dels}')
                
                else:
                    print('What is this {file}?')


if __name__ == '__main__':
    main()
