#!/usr/bin/env python3
# Test organism link at
# ftp://ftp.ensembl.org/pub/release-98/fasta/mesocricetus_auratus/

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
    print(f'sys not imported \n {PRINT_ERROR}')
    sys.exit(0)

try:
    import argparse
    print('argparse imported')
except ImportError:
    print(f'argparse not imported \n {PRINT_ERROR}')
    sys.exit(0)

try:
    import os
    print('os imported')
except ImportError:
    print(f'os not imported \n {PRINT_ERROR}')
    sys.exit(0)

try:
    import re
    print('regex imported')
except ImportError:
    print(f're not imported \n {PRINT_ERROR}')
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

./cleandata.py -TYPE cdna -ORG mesocricetus_auratus -SAVE ./test

or

./cleandata.py -TYPE cdna -ORG ftp://ftp.ensembl.org/pub/release-98/fasta/mesocricetus_auratus/cdna/Mesocricetus_auratus.MesAur1.0.cdna.all.fa.gz

 - SAVE ./test

 - ORG - Organism Name - the name of the orgnaism as it looks in
 the respective database.

 - TYPE - will be a choice between cdna/cds/pep/rna

 - PRE - Prefix - will be the user defined naming scheme

 - CLEAN - and optional argument to remove parent files



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
                        action='version',
                        version='%(prog)s Alpha 1.0')

    parser.add_argument('-TYPE',
                        type=str,
                        choices=['cds', 'cdna', 'pep', 'ncrna'],
                        help='The type of DATA contained in the file',
                        required=True,
                        dest='t')

    parser.add_argument('--prefix',
                        type=str,
                        action='store',
                        help='User-defined naming scheme',
                        dest='p')

    parser.add_argument('-ORGNAME',
                        type=str,
                        action='store',
                        help='''The Organism under scrutiny
                                  (use how the name would appear in ensembl
                                  to make life easier, long name)''',
                        required=True,
                        dest='o')

    parser.add_argument('-SAVE',
                        type=str,
                        action='store',
                        help='Save location for the downloaded files',
                        required=True,
                        dest='s')

    parser.add_argument('--clean',
                        action='store_true',
                        help='''Specifying this argument allows the
                         script to clean all un-nessasery files after
                         use''',
                        dest='c')

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
                    print(f'''Successfully created the directory path at:
                     {path}''')

        if option.o and option.t:
            print('Lets do stuff')

            org = downandsave(option.o, option.s, option.t)

            decompress(option.s, option.t)

            entryfunction(org, option.s, option.t, option.p)

            # seqclean(seq, data_type)

        if option.c:
            rm_redundants(option.s)
        # Then for the files saved from entryfunction
        # send each one to Seqclean


def downandsave(org, save, data_type):
    """
    A function to dowload a user defined file and mv it into the
    downloaded folder.
    """
    downloadloc = f'{save}/cleaning_data/downloaded/'

    if data_type == 'ncrna':
        file_end = '.fa.gz'
    else:
        file_end = '.all.fa.gz'

    if org.startswith('ftp://'):
        download = os.popen(f'''wget -q -o /dev/null {org}''')
        org_from_name = re.search(r'fasta\/(\w+)', org)
        org = org_from_name.group(1)

    else:
        FTP_ADDRESS = f'''ftp://ftp.ensembl.org/pub/release-98/fasta/
                          {org}/{data_type}/*{data_type}{file_end}'''
        download = os.popen(f'''wget -q -o /dev/null ftp://ftp.ensembl.org/pub/release-98/fasta/{org}/{data_type}/*{data_type}{file_end}''')

    # else:
    # print('Input format not recognised!\nIs it exactly how the species name appears in the relevant database?\nOr the full link from the database?')
    movetodirect = os.popen(f'''mv *{file_end} {downloadloc}''')
    rm_originaldl = os.popen(f'''rm *{file_end}*''')
    return org


def decompress(save, data_type):
    """
    A function to decompress the downloaded file from downandsave().
    """
    file_end = '.fa.gz'

    directory = f'{save}/cleaning_data/downloaded/'
    filefinder = os.listdir(directory)

    for file in filefinder:
        if file.endswith(f'{file_end}'):
            unzipper = os.popen(f'gunzip {directory}*{file_end}')

        else:
            print('No gunzip file found')


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


def entryfunction(org, save, data_type, pre='OrgOfInt'):
    """
    The entryfunction function splits a FASTA file into a defined
    number of entries per file, pep == 2000 enteries and everything
    else is split into 5000 enteries.
    """
    print('CDs, cDNA and ncRNA all split at 5000 entries per file')
    entryper = 5000

    typelist = ['pep', 'ncrna', 'cdna', 'cds']
    for data in typelist:
        if data == data_type:
            if data_type == 'pep':
                entryper = 2000
                print('Pep splits at 2000 per file')
            if data_type == 'ncrna':
                file_uncomp = '.fa'
            else:
                file_uncomp = '.all.fa'

    print(org)
    count = 0
    filecounter = 0
    entry = []

    filesavedto = f'{save}/cleaning_data/entries/'
    directory = f'{save}/cleaning_data/downloaded/'

    for file in os.listdir(directory):

        if file.endswith('.fa'):
            unzipped = f'{directory}{file}'

            if os.path.exists(unzipped):
                print('CAN find the unzipped fasta')
            else:
                print('CANNOT find the unzipped fasta')

            with open(unzipped, 'r') as filetoparse:
                for name, seq in read_fasta(filetoparse):
                    new_name = massage(name, data_type)
                    if data_type == 'dna':
                        seq = seqclean(seq)
                        print('Cleaning the dna sequences')

                    nameseq = new_name, seq
                    entry.append(nameseq)
                    count += 1

                    if count == entryper:
                        filecounter += 1

                        with open(f'{filesavedto}{org}-{data_type}{filecounter}MOD.fa', 'w') as done:
                            for new_name, seq in entry:
                                done.write(f'{new_name}\n{seq} \n\n')

                            count = 0
                            entry = []

                    filecounter += 1
                with open(f'{filesavedto}{org}-{data_type}{filecounter}MOD.fa', 'w') as done:
                    for new_name, seq in entry:
                        done.write(f'{new_name}\n{seq} \n\n')

                    entry = []


def massage(name, data_type):
    """
    A function to 'massage' the sequence headers into a more human readable style
    """

    if data_type == 'pep' or 'cds' or 'dna':
        print(f'This sequence is {data_type} from ensembl.')

        if name.startswith('>'):
            gene_symbol = re.search(r'gene_symbol:(\w+)', name)
            ens_code = re.search(r'ENSMAUT(\w+.\d+)', name)

            if gene_symbol:
                gene_symbol = gene_symbol.group(1)
                print(gene_symbol)
            else:
                gene_symbol = re.search(r'ENSMAUG(\w+)', name)
                gene_symbol = gene_symbol.group(0)

            if ens_code:
                ens_code = ens_code.group(0)
                print(ens_code)
            else:
                ens_code = 'NoEnsCode'

            name = f'>{gene_symbol}({ens_code})'
    elif data_type == 'ncrna':
        print('This is a RefSeq ncRNA sequecne, not coded for that yet.')

    else:
        print('''Some how you\'ve got to this point with an
                 incorrect data type''')
        sys.exit(0)

    print(name)

    return name


"""
BEYOND THIS POINT IS NOT COMPLETED AND MAY NOT RUN AT ALL
"""


def seqclean(seq, data_type):
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

    if data_type == 'cdna':
        if os.path.exists(path):
            print('Path to files found')
            for file in os.listdir(path):
                try:
                    set_script = os.popen(f'''bsub -o cleanplease.out
                     -M500 -R\'select[mem>500] rusage[mem=500]
                     \' \\ ~wc2/tools/seqclean/seqclean {file}''')
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


def rm_redundants(save):
    """
    A function to remove all redunant files, an optional
    """
    print('remover')

    directlist = ['/cleaning_data', '/cleaning_data/entries', '/cleaning_data/downloaded', '/cleaning_data/logs', '/cleaning_data/cleaned']

    exten_dels = ['.log', '.cidx', '.cln', 'outparts']

    for direct in directlist:
        path = f'{save}{direct}'
        for file in os.listdir(path):
            for extension in exten_dels:
                if file.endswith(extension):
                    del_extem_del = os.popen(f'rm {file}')
                else:
                    print('This file type isn\'t accounted for {file}?')
# Needs rewriting
        if file.endswith('.clean'):
            mv_clean = os.popen('mv {save}{directlist}{file} {save}/cleaning_data/cleaned/')


if __name__ == '__main__':
    main()
