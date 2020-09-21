#!/usr/bin/env python3
"""
cleaning_geval_data.py
- This is an update on the previously used clean_data.py
Due to some errors and a incompatibility to work with a second
needed FTP server.
This script should be able to work with both ensembl and NCBI
"""

DOCSTRING = """
-------------------------------------------------------------
                   cleaning_gEVAL_data.py
-------------------------------------------------------------
                Cleaning gEVAL supporting DATA
                          By dp24
          Update from wc2's clean_gEVALsupport_data.sh
-------------------------------------------------------------
            IMPORTANT NOTES BEFORE CARRYING ON
        This script is written in and for python3.6

                    IMPORT MODULES

            argparse - for command interface
            os       - for os interface
            sys      - for system interfacing
            re       - for regex usage
            logging  - for debug logging
            subprocess - for better os interfacing
            SHOULD eventually replace os module
-------------------------------------------------------------
USAGE INSTRUCTIONS

./clean_data.py {FTP} {SAVE} {ens | ncbi}
                {pep, cds, cdna, rna}
                [-NAME] [-c, --clean] [-d, --debug]
NOTE:- -NAME is required if using ncbi address due to their
    naming scheme


EXAMPLES
Found on the GitHub Page:


-------------------------------------------------------------


USE CASE FOR THE SCRIPT
1, The aim of this script is to take an input FASTA file
(whether cdna, cds, pep or rna) from ensembl or ncbi.

2, This is downloaded and Unzipped.

2, If Data type is cdna, seqclean is called (may have to
be modified for data sets with high N count).

3, File is read and Headers are split away from the
sequence and massaged into an easy read format.

3, New headers and sequence are merged and counted.
Once the count reaches a set number (for each data type)
a file is produced.

5, Finally folders can be cleaned and debug logs can be read
if needed.
-------------------------------------------------------------
CONTACT
    - dp24@sanger.ac.uk
          and/or
    - grit@sanger.ac.uk
-------------------------------------------------------------
FILE STRUCTURE - if save == './'
                        ./Organism Name
                        -------------
                              |
                              |
                Organism Name + Accession No.
                              |
                              |
            ------------------------------------
            |         |         |      |       |
            cDNA   Peptide     CDS    RNA   README.txt
--------------------------------------------------------------
"""

PRINT_ERROR = '''Does not exist\n
                 Get module installed before import attempt\n
                 If running server side then contact your admin'''

try:
    import sys

    if sys.version_info[0] < 3 and sys.version_info[1] < 6:
        raise Exception("""Must be using Python 3.6 for the full
                        functionality of this script""")
    if sys.version_info[0] >= 3 and sys.version_info[1] >= 6:
        print('Your using at least Version 3.6, You are good to go...')
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

try:
    import logging

    print('logging imported')
except ImportError:
    print(f'logging not imported \n {PRINT_ERROR}')
    sys.exit(0)

try:
    import subprocess as sub

    print('subprocess imported')
except ImportError:
    print(f'subprocess not imported \n {PRINT_ERROR}')
    sys.exit(0)

# ----- NAMING CONSTANTS -----
# COULD BE SIMPLIFIED BY USING A DICT
NONE_ENS_GENE = 0
NONE_ENS_S = 0
NUMB_HEADERS = 0
MISSING_ENS = 0
MISSING_GENE = 0
GENE_NAME = 0
GENE_ENS = 0
ENS_STYLE_ENS = 0
# ----- NAMING CONSTANTS -----


def parse_command_args(args=None):
    """
    A function to verify the command line arguments to be passed
    to the rest of the script.
    :param args:
    :return option:
    """
    # Although This Chunk is Highlighted as an Error,
    # it is correct and does function as intended.
    parser = argparse.ArgumentParser(prog='Clean the gEVAL Supporting DATA',
                                     description=DOCSTRING,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('FTP',
                        action='store',
                        help='''This argument is to be used when using an
                            ftp address for this script''',
                        type=str)

    parser.add_argument('SAVE',
                        type=str,
                        action='store',
                        help='Save location for the downloaded files')

    parser.add_argument('FTP_TYPE',
                        type=str,
                        choices=['ens', 'ncbi'],
                        help='Specify the FTP')

    parser.add_argument('TYPE',
                        type=str,
                        choices=['cds', 'cdna', 'pep'],
                        help='The type of DATA contained in the file',
                        nargs='*')

    parser.add_argument('-NAME', '--organism_ncbi',
                        type=str,
                        action='store',
                        help='''If using ncbi FTP, then the organisms
                            name must be provided due to how they name
                            their files''',
                        dest='name')

    parser.add_argument('-v', '--version',
                        action='version',
                        version='%(prog)s  4.0.0')

    parser.add_argument('-c', '--clean',
                        action='store_true',
                        help='''Specifying this argument allows the
                            script to clean all un-necessary files after
                            use''',
                        dest='c')

    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='''Specifying this argument allows debug
                            prints to work and show everything the script is
                            doing''',
                        dest='d')

    option = parser.parse_args(args)
    return option


def main():
    """
    A function to control the overall
    controlling logic of the script
    """
    option = parse_command_args()

    if option.d:
        logging.basicConfig(filename="cleaning.log",
                            level=logging.DEBUG,
                            format="%(asctime)s:%(levelname)s:%(message)s")
        logging.info('Welcome to cleaning_geval_data.py version 4 \n'
                     'Options passed to script: \n'
                     '%s', option)

    # Check for -NAME and -FTP_TYPE, if one and not the other then exit
    if option.FTP_TYPE and not option.name:
        logging.critical('Argument -NAME is required when ncbi is used')
        sys.exit()

    org_name, file = ftp_check(option)
    directory = directory_jenny(option, org_name)

    # Set the file name we want to use
    seq_file = re.search(r'\/(\w+.\w+.\w+.all.fa)', option.FTP)
    if seq_file:
        # For Ens
        seq_file = seq_file.group(1)
    else:
        # For NCBI
        seq_file = re.search(r'(\w+.\w+.\w+).gz', file)
        seq_file = seq_file.group(1)
        if not seq_file.startswith('GC'):
            file = re.search(r'(\w+.\w+.\w+.\w+).gz', file)
            seq_file = file.group(1)
        else:
            logging.critical('Regex Couldn\'t find the right file name.'
                             'Found: %s', seq_file)
            sys.exit()

    logging.info('File to use: %s', seq_file)
    print(seq_file)

    # CURRENTLY A LIST TO FACILITATE MULTI-FETCHING
    for dtype in option.TYPE:
        if dtype == 'cdna':
            # Re-Sets file name we want to play with
            seq_file = seqclean(option)
            seq_file = f'{seq_file}.clean'
            entryper = 5000

        elif dtype == 'pep':
            entryper = 2000
        else:
            # cds and rna
            entryper = 3000

        logging.info('Type of data: %s \n So entry per file is: %i',
                     dtype, entryper)
        entryfunction(option, seq_file, org_name, directory, entryper)
        readme_jenny(directory, dtype)

    if option.c:
        clean_file_system()


def ftp_check(option):
    """
    A function to check the FTP address and download the needed file.
    :param option:
    :return org_name:
    :return file:
    """
    ftp = option.FTP
    if option.FTP_TYPE == 'ens':
        logging.info('Ensembl')
        file = re.search(r'\/(\w+.\w+.\w+.\w+.\w+.gz)', ftp)
        file = file.group(1)
    elif option.FTP_TYPE == 'ncbi':
        logging.info('NCBI')
        file = re.search(r'(\w+.\w+.\w+.gz)', ftp)
        file = file.group(1)
        if not file.startswith('GC'):
            file = re.search(r'(\w+.\w+.\w+.\w+.gz)', ftp)
            file = file.group(1)
        else:
            pass

    else:
        logging.critical('Proper file name can\'t be derived')
        sys.exit()

    curling = sub.Popen(['curl', f'-o{file}', f'{ftp}'],
                        stdout=sub.PIPE,
                        stderr=sub.PIPE)
    logging.info('curl -o %s %s', file, ftp)
    curling.wait()

    if option.FTP_TYPE == 'ens':
        org_name = re.search(r'(\w+.\w+.\w+.\w+.\w+)', file)
        org_name = org_name.group(1)
    else:
        org_name = option.name

    os.popen('gunzip -f *.gz')
    logging.info('Unzipping Zipped files')

    return org_name, file


def directory_jenny(option, org_name):
    """
    A function to generate a directory structure
    :param option:
    :param org_name:
    :return directory_naming:
    """
    logging.info('Directory Generator Called')
    access_rights = 0o755

    if option.FTP_TYPE == 'ens':
        org_from_name = re.search(r'\w+\/([A-Z]\w*).([\S]\w*)',
                                  option.FTP)
        org_name = org_from_name.group(1)
        accession = org_from_name.group(2)
    else:
        acc = re.search(r'\/GC._\w+.(\w+)',
                        option.FTP)
        accession_re = acc.group(1).split('_')
        accession = accession_re[1]

    org_ass = f'{org_name}.{accession}'

    directory_naming = [f'{option.SAVE}{org_name}',
                        f'{option.SAVE}{org_name}/{org_ass}',
                        f'{option.SAVE}{org_name}/{org_ass}/cdna',
                        f'{option.SAVE}{org_name}/{org_ass}/pep',
                        f'{option.SAVE}{org_name}/{org_ass}/cds',
                        f'{option.SAVE}{org_name}/{org_ass}/rna']

    for direct in directory_naming:
        if os.path.exists(direct):
            logging.info('Path: %s :already exists', direct)
        else:
            try:
                os.makedirs(direct, access_rights)
            except OSError:
                logging.warning('Creation of directory'
                                ' has failed at: %s', direct)
            else:
                logging.info('Successfully created the directory '
                             'path at: %s', direct)

    logging.debug('Folder generator finished')

    return directory_naming


def seqclean(option):
    """
    A function to control the use of SeqClean,
    the file passed into it and which SeqClean
    Location to use.
    :param option:
    :return file_to_seq:
    """
    if option.FTP_TYPE == 'ens':
        file_to_seq = re.search(r'\/fasta\/\w+\/\w+\/(\w*.+).gz', option.FTP)
        file_to_seq = file_to_seq.group(1)
    else:
        file_to_seq = re.search(r'\/(GC\w*.\w*.\w+).gz', option.FTP)
        file_to_seq = file_to_seq.group(1)

    cwd = os.getcwd()

    try:
        seq_file = sub.Popen(['./seqclean/seqclean',
                              f'{cwd}/{file_to_seq}'])
        loc = 'Primary location: ./seqclean/seqclean'
        seq_file.wait()
    except OSError:
        seq_file = sub.Popen(['./nfs/users/nfs_w/wc2/tools/seqclean/seqclean',
                              f'{cwd}/{file_to_seq}'])
        loc = 'Secondary location: ./nfs/users/nfs_w/wc2/tools/seqclean/seqclean'
        seq_file.wait()

    logging.info('File to use in seqclean: %s \n'
                 'Using Seqclean found at: %s',
                 file_to_seq, loc)

    return file_to_seq


def entryfunction(option, seq_file, org, directory, entryper):
    """
    The entryfunction function splits a FASTA file into a defined
    number of entries per file, pep == 2000 enteries and everything
    else is split into 5000 enteries.
    :param seq_file:
    :param org:
    :param directory:
    :param entryper:
    :param option:
    """
    logging.debug('Entryfunction called')
    count = 0
    filecounter = 0
    entry = []

    org = re.search(r'(\w+)', org)
    org = org.group(1)

    for data_type in option.TYPE:

        filesavedto = f'{directory[1]}/{data_type}/'
        short_save_dir = f'{option.SAVE}{filesavedto}{org}'

        if data_type == 'cdna':
            file_path = f'{seq_file}.clean'
        else:
            file_path = seq_file

        if os.path.exists(file_path):
            logging.info('File found at %s', file_path)
            with open(file_path, 'r') as filetoparse:
                logging.info('Renaming headers')
                for name, seq in read_fasta(filetoparse):
                    # Logging is here inorder to stop un-needed repetition in log
                    new_name = massage(option, name)
                    print(new_name)  # Here as a manual check of headers
                    nameseq = new_name, seq
                    entry.append(nameseq)
                    count += 1

                    if count == entryper:
                        filecounter += 1
                        with open(f'{short_save_dir}{filecounter}'
                                  f'{data_type}.MOD.fa', 'w') as done:
                            for head, body in entry:
                                done.write(f'{head}\n{body}\n')
                            count = 0
                            entry = []
                        logging.info('File saved:\n '
                                     '%s %i %s .MOD.fa', short_save_dir, filecounter, data_type)

                    filecounter += 1

                with open(f'{short_save_dir}{filecounter}'
                          f'{data_type}.MOD.fa', 'w') as done:
                    for head, body in entry:
                        done.write(f'{head}\n{body}\n')

                    entry = []

                    logging.info('File saved:\n '
                                 '%s %i %s .MOD.fa', short_save_dir, filecounter, data_type)


# Should be changed as if, elif statements in this way are
# rather crude. Needs to be simplified as well as make more
# expansive to catch the best data possible.
def massage(option, name):
    """
    A function to 'massage' the sequence headers into a more human readable
    style
    :param option:
    :param name:
    :return name:
    """
    global NONE_ENS_GENE
    global NONE_ENS_S
    global NUMB_HEADERS
    global MISSING_ENS
    global MISSING_GENE
    global GENE_NAME
    global GENE_ENS
    global ENS_STYLE_ENS

    if name.startswith('>'):
        NUMB_HEADERS += 1
        if option.FTP_TYPE == 'ncbi':
            gene_symbol = re.search(r'gene=([A-Z]\w+)', name)
            ens_code = re.search(r'GeneID:([1-9])\w+', name)
        else:
            gene_symbol = re.search(r'symbol:(\S+)', name)
            ens_code = re.search(r'ENS(\w+)T(\w+.\d+)', name)

        if gene_symbol:
            GENE_NAME += 1
            gene_symbol = gene_symbol.group(1)
        elif gene_symbol is None:
            gene_symbol = re.search(r'gene:(\S+)', name)

            if gene_symbol:
                gene_symbol = gene_symbol.group(1)
                if gene_symbol.startswith('ENS'):
                    GENE_ENS += 1
                else:
                    GENE_NAME += 1
            elif gene_symbol is None:
                gene_symbol = re.search(r'PREDICTED: (.+) \[', name)
                if gene_symbol:
                    gene_symbol = gene_symbol.group(1)
                    gene_symbol = gene_symbol.split()
                    gene_symbol = '_'.join(gene_symbol)
                else:
                    gene_symbol = 'MissingInfo'
                    NONE_ENS_GENE += 1

        if ens_code:
            ENS_STYLE_ENS += 1
            ens_code = ens_code.group(0)

        elif ens_code is None:
            NONE_ENS_S += 1
            ens_code = re.search(r'>(\S+)', name)
            if ens_code:
                ens_code = ens_code.group(1)
            elif ens_code is None:
                MISSING_ENS += 1
                ens_code = 'NoEnsCode'

        logging.info('Gene Symbol found as: %s', gene_symbol)
        logging.info('Ens Code found as: %s', ens_code)
        if gene_symbol == 'MissingInfo':
            logging.info('MissingInfo replaced with %s', ens_code)
            gene_symbol = ens_code
        name = f'>{gene_symbol}({ens_code})'

    else:
        logging.debug('Somethings gone wrongs, headers are wrong')
        sys.exit(0)

    return name


def read_fasta(filetoparse):
    """
    A function which opens and splits a fasta into name and seq.
    :param filetoparse:
    """
    logging.info('Read_fasta called')
    counter = 0
    name, seq = None, []

    for line in filetoparse:
        line = line.rstrip()

        if line.startswith(">"):
            if name:
                yield name, ''.join(seq)
            name, seq = line, []
        else:
            seq.append(line)

    if name:
        yield name, ''.join(seq)
        counter += 1

    logging.info('Entry %i produced', counter)


# Not Working correctly, needs alot of work
# Alot more stats that could be added, but is it worth it?
def readme_jenny(directory, data_type):
    """
    A function to generate a README.txt with relevant stats and information.
    :param directory:
    :param data_type:
    """
    global NONE_ENS_GENE
    global NONE_ENS_S
    global NUMB_HEADERS
    global MISSING_ENS
    global MISSING_GENE
    global GENE_NAME
    global GENE_ENS
    global ENS_STYLE_ENS

    # All stats are post cleaning for cdna
    option = parse_command_args()
    save_to = directory[1]
    breaker = '|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*||*|*|*|*|*|'
    divider = '-----------------------------------------------'

    logging.info('README function stated')
    with open(f'{save_to}/README.txt', 'w') as readme:
        readme.write(f"""
    {breaker}\n
    Stats and numbers for the output of the
    cleaning_gEVAL_data.py script
    {divider}
    {save_to}
    {data_type.upper()}
    {divider}
    Direct link to data used to produce the nested
    information
    {option.FTP}
    {option.FTP_TYPE}
    {divider}
    The number of entries:
    {NUMB_HEADERS}
    {divider}
    Number of named genes:
    {ENS_STYLE_ENS}

    Number of gene symbols (ENS style):
    {GENE_NAME}

    Number of missing genes:
    {MISSING_GENE}

    Number of None-ENS style genecode (e.g. barcode style):
    {NONE_ENS_GENE}
    {divider}
    Number of ENS codes:
    {GENE_ENS}

    Number of missing ENS:
    {MISSING_ENS}

    Number of missing ENS (Barcode style):
    {NONE_ENS_S}
    {breaker} \n\n
    """)

    logging.info('README function finished')


def clean_file_system():
    """
    A function to clean the stray files that appear in the process
    of this script
    """
    logging.info('Cleaning File System')
    file_type_del = ['*.fa', '*.fa.gz', '*.fa.gz.*',
                     '*.clean', '*.cidx', '*.sort', '*.cln',
                     '*sx_file*', '*_tmp', '*.log',
                     '*.fna', '*.fna.gz', '*.faa', '*.faa.gz']

    for extension in file_type_del:
        os.popen(f'rm {extension}')

    logging.debug('Cleaning File System finished')


if __name__ == "__main__":
    main()
