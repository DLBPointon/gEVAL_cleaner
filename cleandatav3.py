#!/usr/bin/env python3

"""
cleaningdatav3.py
"""

DOCSTRING = """
-------------------------------------------------------------
                        cleandatav3.py
-------------------------------------------------------------
                Cleaning gEVAL supporting DATA
                          By dp24
        Updated from wc2's clean_gEVALsupport_data.sh
-------------------------------------------------------------
            IMPORTANT NOTES BEFORE CARRYING ON
        This script is written in for python3.6

                    IMPORT MODULES

            argparse - for command interface
            os       - for os interface
            sys      - for system interfacing
            re       - for regex usage
            logging  - for debug logging
            time     - for waiting for file creation
-------------------------------------------------------------
USE CASE FOR THE SCRIPT
1, The aim of this script is to take an input FASTA file
(whether cdna, cds or pep) from ensembl.

2, Next the headers will be massaged into a standardised
format.

3, Sequence will be split into entries and data_type defined
number of entries per file.
For DNA an '.all.MOD.fa' will also be produced for later
seqclean usage.

4, Sequences are then trimmed and modified by Seqclean
(not finished).

5, Finally folders can be cleaned and debug can be read if
needed.
-------------------------------------------------------------
USAGE INSTRUCTIONS

[-arg] = positional args

./cleandatav3.py [-FTP] ftp://ftp.ensembl.org/pub/
release-98/fasta/mesocricetus_auratus/cdna/Mesocricetus_auratus.
MesAur1.0.cdna.all.fa.gz [-SAVE] ./test [-TYPE] cdna

Optionals include --clean and/or --debug
-------------------------------------------------------------
FUTURE CHANGES
    - MissingGene Counter
        - General counters and Stats
    - Add option for parent directory as FTP and script
    searches for file to use.
    - Add README.txt to show stats on data
-------------------------------------------------------------
CONTACT
    - dp24@sanger.ac.uk
            or
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
                    ---------------------
                    |         |         |
                    cDNA   Peptide     CDS
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
    import shutil

    print('Shutil imported')
except ImportError:
    print(f'Shutil not imported \n {PRINT_ERROR}')
    sys.exit(0)

try:
    import time

    print('Time imported')
except ImportError:
    print(f'Time not imported \n {PRINT_ERROR}')
    sys.exit(0)


none_es_gene = 0
none_ens_s = 0
numb_headers = 0
missing_ens = 0
missing_gene = 0
gene_name = 0
gene_ens = 0
ens_style_ens = 0


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
                        version='%(prog)s  3.0')

    parser.add_argument('TYPE',
                        type=str,
                        choices=['cds', 'cdna', 'pep'],
                        help='The type of DATA contained in the file',
                        dest='t')

    parser.add_argument('SAVE',
                        type=str,
                        action='store',
                        help='Save location for the downloaded files',
                        dest='s')

    parser.add_argument('--clean',
                        action='store_true',
                        help='''Specifying this argument allows the
                            script to clean all un-necessary files after
                            use''',
                        dest='c')

    parser.add_argument('--debug',
                        action='store_true',
                        help='''Specifying this argument allows debug
                            prints to work and show everything the script is
                            doing''',
                        dest='d')

    parser.add_argument('FTP',
                        action='store',
                        help='''This argument is to be used when using an 
                            ftp address for this script''',
                        type=str,
                        dest='f')

    option = parser.parse_args(args)
    return option


def main():
    """
    The Main function which controls the logic for the script
    """
    option = parse_command_args()
    if option.f and option.s and option.t:
        if option.d:
            logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s',
                                filename='gEVAL_clean.log')

        logging.debug('Main function has been called')
        cwd = os.getcwd()

        org, directory = file_jenny(option.f, option.s)

        downandsave(option.f)

        # Command block to control usage of seqclean
        for file in os.listdir('./'):
            if file.endswith('.fa'):
                if option.t == 'cdna':
                    seqclean(file)
                else:
                    unzippedfile = f'./{file}'
                    if os.path.exists(unzippedfile):
                        unzippedfile = file
                        logging.debug(f'{unzippedfile} EXISTS')
                        if option.t == 'pep':
                            entryfunction(org, directory, option.t, unzippedfile, entryper=2000)
                        else:
                            entryfunction(org, directory, option.t, unzippedfile, entryper=3000)
                        readme_jenny(none_es_gene, none_ens_s, numb_headers, missing_ens, missing_gene,
                                     gene_name, gene_ens, ens_style_ens, directory, option.t)

        # Command block to control seqclean and the following entryfunction
        if option.t == 'cdna':
            time_counter = 0
            while not file.endswith('.clean'):
                for file in os.listdir(cwd):
                    if file.endswith('.clean'):
                        unzippedfile = f'./{file}'
                        if os.path.exists(unzippedfile):
                            logging.debug(f'{unzippedfile} EXISTS')
                            entryfunction(org, directory, option.t, unzippedfile, entryper=5000)
                            readme_jenny(none_es_gene, none_ens_s, numb_headers, missing_ens, missing_gene,
                                         gene_name, gene_ens, ens_style_ens, directory, option.t)
                            break

                    else:
                        time.sleep(0.25)
                        time_counter += 1
                        logging.debug(f'File not found {time_counter} {file}')
                        print(f'File not found {time_counter} {file}')

    if option.c:
        print('Cleaning')
        logging.debug('Cleaning Called')
        clean_file_system()

    print("Script is Done!")
    logging.debug('Main function finished')


def file_jenny(ftp, save):
    """
    A function to generate the folders to be used through out the script.
    Will use the FTP to generate a naming scheme.
    """
    logging.debug('Folder generator called')
    access_rights = 0o755

    # These are not redundant escapes, they are there due to the structure
    # of the string they are regexing.
    org_from_name = re.search(r'fasta\/\w+\/\w+\/(\w+)\S(\w+)', ftp)
    org = org_from_name.group(1)
    accession = org_from_name.group(2)

    org_ass = f'{org}.{accession}'

    directory_naming = [f'/{org}', f'/{org}/{org_ass}', f'/{org}/{org_ass}/cdna', f'/{org}/{org_ass}/pep',
                        f'/{org}/{org_ass}/cds']

    for direct in directory_naming:
        path = save + direct
        if os.path.exists(path):
            logging.info(f'Path: {path} :already exists')
        else:
            try:
                os.makedirs(path, access_rights)
            except OSError:
                logging.critical(f'Creation of directory has failed at: {path}')
            else:
                logging.info(f'''Successfully created the directory path at:
                                     {path}''')

    logging.debug('Folder generator finished')
    return org, directory_naming


def readme_jenny(a, b, c, d, e, f, g, h, directory, data_type):
    """
    A function to generate a README.txt with relevant stats and information.
    """
    # All stats are post cleaning for cdna
    save_to = directory[1]

    logging.info('README function stated')
    with open(f'.{save_to}/README.txt', 'a') as readme:
        readme.write(f"""|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*||*|*|*|*|*|
    Stats and numbers for the output of the
    cleandatav3.py script
    -----------------------------------------------
    {save_to}
    {data_type.upper()}
    -----------------------------------------------
    The number of entries:
    {c}
    -----------------------------------------------
    Number of named genes:
    {h}
     
    Number of gene symbols
       (ENS style):
    {f}

    Number of missing genes:
    {e}

    Number of None ENS style genecode
       (e.g. barcode style):
    {a}
    -----------------------------------------------
    Number of ENS codes:
    {g}

    Number of missing ENS:
    {d}

    Number of missing ENS 
       (Barcode style):
    {b}
    |*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*||*|*|*|*|*|

    """)

    logging.info('README function finished')


def downandsave(ftp):
    """
    A function to download, save and unzip a file
    """
    logging.debug('Down and save function called')
    if ftp:
        logging.debug('FTP address given as argument')
        try:
            logging.info(f'Starting Download of {ftp}')
            os.popen(f'wget -q -o /dev/null {ftp}')
            time.sleep(2)
            logging.debug('Giving time to download')

        except:
            logging.critical('File NOT Downloaded')
            sys.exit(0)
    else:
        logging.debug('FTP address not given (using just the org name will be coded soon)')

    cwd = os.getcwd()
    for file in os.listdir(f'{cwd}/'):
        if file.endswith('.fa.gz'):
            logging.info('Download finished')
            try:
                os.popen(f'gunzip -fd {file}')
                time.sleep(2)
                logging.debug('Giving time up unpack .gz')
            except:
                logging.critical('Gunzip failed to unzip file')
        elif file.endswith('.fa.gz.1'):
            try:
                os.popen(f'gunzip -fd {file}')
            except:
                logging.critical('Gunzip failed to unzip file')


def read_fasta(filetoparse):
    """
    A function which opens and splits a fasta into name and seq.
    """
    logging.debug('Read_fasta called')
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
    logging.info('Entry produced')


def entryfunction(org, directory, data_type, unzippedfile, entryper):
    """
    The entryfunction function splits a FASTA file into a defined
    number of entries per file, pep == 2000 enteries and everything
    else is split into 5000 enteries.
    """
    logging.debug('Entryfunction called')
    option = parse_command_args()
    count = 0
    filecounter = 0
    entry = []
    filesavedto = f'{directory[1]}/{data_type}/'
    logging.info(f'Supplied data is {data_type}')

    if os.path.exists(unzippedfile):
        logging.info(f'File found at {unzippedfile}')
        print(unzippedfile)
        with open(unzippedfile, 'r') as filetoparse:
            for name, seq in read_fasta(filetoparse):

                # This block controls cDNA files, the first run
                # through this would allow massage to modify the
                # headers, the second run through (to split the
                # file), massage would be excluded to stop any
                # possible errors.
                if data_type == 'cdna':
                    logging.debug('cDNA Massaging')
                    new_name, a, b, c, d, e, f, g, h = massage(name, data_type)
                    print(new_name)
                elif data_type != 'cdna':
                    logging.debug(f'{data_type} being used')
                    new_name, a, b, c, d, e, f, g, h = massage(name, data_type)
                    print(new_name)

                else:
                    logging.critical(f'Data type of {data_type} not recognised.')
                    sys.exit(0)

                nameseq = new_name, seq

                entry.append(nameseq)
                count += 1

                if count == entryper:
                    filecounter += 1
                    with open(f'''{option.s}{filesavedto}{org}{filecounter}{data_type}.MOD.fa''', 'w') as done:
                        for head, body in entry:
                            done.write(f'{head}\n{body}\n')

                        count = 0
                        entry = []

                    logging.debug(f'File saved:\n{option.s}{filesavedto}{org}{filecounter}{data_type}.MOD.fa')

                filecounter += 1
            with open(f'''{option.s}{filesavedto}{org}{filecounter}{data_type}.MOD.fa''', 'w') as done:
                for head, body in entry:
                    done.write(f'{head}\n{body}\n')

                entry = []

            logging.debug(f'File saved:\n{option.s}{filesavedto}{org}{filecounter}{data_type}.MOD.fa')
    else:
        print('Not found')
        logging.debug('Cannot find unzipped file')
        sys.exit(0)

    logging.debug('Entry Function finished')

    return a, b, c, d, e, f, g, h


def massage(name, data_type):
    """
    A function to 'massage' the sequence headers into a more human readable
     style
    """
    global none_es_gene
    global none_ens_s
    global numb_headers
    global missing_ens
    global missing_gene
    global gene_name
    global gene_ens
    global ens_style_ens
    logging.debug('Massage started')
    if data_type == 'pep' or 'cds' or 'cdna':

        if name.startswith('>'):
            numb_headers += 1
            logging.info('Renaming headers')
            gene_symbol = re.search(r'symbol:(\w+\S+)', name)
            ens_code = re.search(r'ENS(\w+)T(\w+.\d+)', name)

            if gene_symbol:
                gene_name += 1
                gene_symbol = gene_symbol.group(1)

            elif gene_symbol is None:
                try:
                    gene_ens += 1
                    gene_symbol = re.search(r'ENS(\w+)G(\w+.\d+)', name)
                    gene_symbol = gene_symbol.group(0)
                except:
                    if gene_symbol is None:
                        none_es_gene += 1
                        gene_symbol = re.search(r'gene:(\w+)', name)
                        gene_symbol = gene_symbol.group(1)
                else:
                    missing_gene += 1
                    gene_symbol = 'MissingInfo'

            if ens_code:
                ens_style_ens += 1
                ens_code = ens_code.group(0)

            elif ens_code is None:
                none_ens_s += 1
                ens_code = re.search(r'>(\S+)', name)
                ens_code = ens_code.group(1)

            else:
                missing_ens += 1
                ens_code = 'NoEnsCode'

            logging.info(f'Gene Symbol found as: {gene_symbol}')
            logging.info(f'Ens Code found as: {ens_code}')
            name = f'>{gene_symbol}({ens_code})'

        else:
            logging.debug('Somethings gone wrongs, headers are corrupt')
            sys.exit(0)

    else:
        logging.debug('Some how you\'ve got to this point with an incorrect data type')
        sys.exit(0)

    logging.debug('Massage finished')
    return name, none_es_gene, none_ens_s, numb_headers, missing_ens, missing_gene, gene_ens, ens_style_ens, gene_name


def seqclean(path):
    """
    A function to sent entry split files to the seqclean perl script,
    this script will clean the sequence to ensure there is nothing that
    requires correcting.
    """
    logging.debug('Seqclean called')

    try:
        logging.info('Running Seq_clean script')
        os.popen(f'./seqclean/seqclean {path}')
        logging.debug(f'Finished, Your file is here: {path}.clean')
        print('dp24 seqclean site')

    except:
        logging.info('Running alt Seq_clean at wc2/tools/')
        os.popen(f'./nfs/users/nfs_w/wc2/tools/seqclean/seqclean {path}')
        logging.debug(f'Finished, Your file is here: {path}.clean')
        print('wc2 seqclean site')

    else:
        logging.debug('Seqclean locations are wrong')

    logging.debug('seqclean finished')


def clean_file_system():
    """
    A function to clean the stray files that appear in the process of this script
    """
    logging.debug('Cleaning File System')

    file_type_del = ['*.log', '*.cidx', '*.sort', '*.cln', '*.fa',
                     '*.fa.gz', '*.fa.gz.*', '*.clean', '*sx_file*', '*_tmp']

    for extension in file_type_del:
        os.popen(f'rm {extension}')

    logging.debug('Cleaning File System finished')


if __name__ == '__main__':
    main()
