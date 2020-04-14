#!/usr/bin/env python3

"""
clean_data.py
"""

DOCSTRING = """
-------------------------------------------------------------
                        clean_data.py
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
            ftplib   - for access to and searching through an
                        ftp server
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

5, Finally folders can be cleaned and debug logs can be read
 if needed.
-------------------------------------------------------------
USAGE INSTRUCTIONS

./clean_data.py {FTP} {SAVE} {pep, cds, cdna, all}
                 [--clean] [--debug] [--time]

FTP can be either:
- The full ftp address for example:
        ftp://ftp.ensemblgenomes.org/pub/release-46/
        plants/fasta/arabidopsis_thaliana/cdna/
        Arabidopsis_thaliana.TAIR10.cdna.all.fa.gz

- Or organism name + org type in the style of:
        arabidopsis_thaliana+plants

        This +plants refers to the ensemblgenomes directory
        so this can be:
        +plants
        +metazoa
        +protists
        +fungi
        +bacteria

        If org is not in ensemblgenomes then use:
        +ensembl

        This will tell the script so search ftp.ensembl.org
        not ftp.ensemblgenomes.org

-------------------------------------------------------------
FUTURE CHANGES
    - Add option for parent directory as FTP and script
    searches for file to use.
    - Add more stats to the README.txt
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
                ------------------------------
                |         |         |        |
                cDNA   Peptide     CDS   README.txt
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
    import time

    print('Time imported')
except ImportError:
    print(f'Time not imported \n {PRINT_ERROR}')
    sys.exit(0)

try:
    from ftplib import FTP

    print('FTP module imported')
except ImportError:
    print(f'FTP not imported \n {PRINT_ERROR}')
    sys.exit(0)

try:
    import ftplib

    print('ftplib imported')
except ImportError:
    print(f'ftplib not imported \n {PRINT_ERROR}')
    sys.exit(0)

# ----- NAMING CONSTANTS -----
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
    """
    descformat = argparse.RawDescriptionHelpFormatter

    parser = argparse.ArgumentParser(prog='Clean the gEVAL Supporting DATA',
                                     formatter_class=descformat,
                                     description=DOCSTRING)

    parser.add_argument('FTP',
                        action='store',
                        help='''This argument is to be used when using an
                            ftp address for this script''',
                        type=str)

    parser.add_argument('SAVE',
                        type=str,
                        action='store',
                        help='Save location for the downloaded files')

    parser.add_argument('TYPE',
                        type=str,
                        choices=['cds', 'cdna', 'pep', 'all'],
                        help='The type of DATA contained in the file')

    parser.add_argument('-v', '--version',
                        action='version',
                        version='%(prog)s  3.3.0')

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

    parser.add_argument('-t', '--time',
                        action='store_true',
                        help='A flag to check the run time of the script')

    option = parser.parse_args(args)
    return option


def main():
    """
    The Main function which controls the logic for the script
    """
    logging.debug('Main function has been called')
    option = parse_command_args()

    # --- None ftp link style name handling ---
    if not option.FTP.startswith('ftp://'):
        logging.debug(f'shortened ftp address used: {option.FTP}')
        name_list = option.FTP.split('+')

        if name_list[1] == 'ensembl':
            url_gen = f'/pub/release-99/fasta/{name_list[0]}/{option.TYPE}'
            ftp_loc = 'ftp.ensembl.org'
        else:
            url_gen = f'/pub/release-46/{name_list[1]}/fasta/' \
                      f'{name_list[0]}/{option.TYPE}'
            ftp_loc = 'ftp.ensemblgenomes.org'

        full_ftp = f'{ftp_loc}{url_gen}'
        ftp_url = FTP(ftp_loc)
        ftp_url.login()
        # Insert a return code check, if not 200 sys.exit()
        ftp_url.cwd(f'{url_gen}')
        ftp_dir = ftp_url.nlst()

        for file in ftp_dir:
            if file.endswith(f'{option.TYPE}.all.fa.gz'):
                option.FTP = f'ftp://{full_ftp}/{file}'
                logging.debug(f'shortened ftp address converted to '
                              f'long style used: {option.FTP}')

    # --- None ftp link style name handling ---

    logging.debug(f'long ftp address used: {option.FTP}')
    if option.FTP and option.SAVE and option.TYPE:
        if option.d:
            logging.basicConfig(level=logging.INFO,
                                format='%(asctime)s :: '
                                       '%(levelname)s :: '
                                       '%(message)s',
                                filename='gEVAL_clean.log')

        cwd = os.getcwd()
        logging.debug(' FTP == %s', option.FTP)
        org, directory = file_jenny(option.FTP, option.SAVE)
        downandsave(option.FTP)

        # Command block to control usage of seqclean
        for file in os.listdir(option.SAVE):
            if file.endswith('.all.fa'):
                if option.TYPE == 'cdna' or 'all':
                    if file.endswith('cdna.all.fa'):
                        seqclean(file)
                elif option.TYPE != 'cdna':
                    unzippedfile = f'{option.SAVE}{file}'
                    if os.path.exists(unzippedfile):
                        unzippedfile = file
                        logging.debug('%s EXISTS', unzippedfile)
                        if option.TYPE == 'pep':
                            entryfunction(org, directory, option.TYPE,
                                          unzippedfile, entryper=2000)
                        else:
                            entryfunction(org, directory, option.TYPE,
                                          unzippedfile, entryper=3000)
                        readme_jenny(NONE_ENS_GENE, NONE_ENS_S,
                                     NUMB_HEADERS, MISSING_ENS,
                                     MISSING_GENE, GENE_NAME, GENE_ENS,
                                     ENS_STYLE_ENS, directory, option.TYPE)

        # Command block to control seqclean and the following entryfunction
        if option.TYPE == 'cdna':
            time_counter = 0
            while not file.endswith('.clean'):
                for file in os.listdir(cwd):
                    if file.endswith('.clean'):
                        unzippedfile = f'{option.SAVE}{file}'
                        if os.path.exists(unzippedfile):
                            logging.debug('%s EXISTS', unzippedfile)
                            entryfunction(org, directory, option.TYPE,
                                          unzippedfile, entryper=5000)
                            readme_jenny(NONE_ENS_GENE, NONE_ENS_S,
                                         NUMB_HEADERS, MISSING_ENS,
                                         MISSING_GENE, GENE_NAME,
                                         GENE_ENS, ENS_STYLE_ENS,
                                         directory, option.TYPE)
                            break

                    else:
                        time.sleep(0.05)
                        time_counter += 1
                        logging.debug(f'File not found {0}'
                                      f' {1}'.format(time_counter, file))
                        print(f' File not found {time_counter} {file}')

                    real_count = time_counter / 20
                    logging.info('File found in %s', real_count)
                    print(f'Run Time of {real_count}')

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

    directory_naming = [f'/{org}', f'/{org}/{org_ass}',
                        f'/{org}/{org_ass}/cdna',
                        f'/{org}/{org_ass}/pep',
                        f'/{org}/{org_ass}/cds']

    for direct in directory_naming:
        path = save + direct
        if os.path.exists(path):
            logging.info('Path: %s :already exists', path)
        else:
            try:
                os.makedirs(path, access_rights)
            except OSError:
                logging.critical('Creation of directory'
                                 ' has failed at: %s', path)
            else:
                logging.info('Successfully created the directory '
                             'path at: %s', path)

    logging.debug('Folder generator finished')
    return org, directory_naming


def readme_jenny(none_ens_code, none_ens_s, numb_headers, missing_ens,
                 missing_gene, gene_name, gene_ens, ens_style_ens,
                 directory, data_type):
    """
    A function to generate a README.txt with relevant stats and information.
    """
    # All stats are post cleaning for cdna
    option = parse_command_args()
    save_to = directory[1]

    logging.info('README function stated')
    with open(f'.{save_to}/README.txt', 'a') as readme:
        readme.write(f"""
    |*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*||*|*|*|*|*|
    Stats and numbers for the output of the
    clean_data.py script
    -----------------------------------------------
    {save_to}
    {data_type.upper()}
    -----------------------------------------------
    Direct link to data used to produce the nested
    information
    {option.FTP}
    -----------------------------------------------
    The number of entries:
    {numb_headers}
    -----------------------------------------------
    Number of named genes:
    {ens_style_ens}

    Number of gene symbols
       (ENS style):
    {gene_name}

    Number of missing genes:
    {missing_gene}

    Number of None ENS style genecode
       (e.g. barcode style):
    {none_ens_code}
    -----------------------------------------------
    Number of ENS codes:
    {gene_ens}

    Number of missing ENS:
    {missing_ens}

    Number of missing ENS
       (Barcode style):
    {none_ens_s}
    |*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*||*|*|*|*|*|

    """)

    logging.info('README function finished')


def downandsave(ftp):
    """
    A function to download, save and unzip a file
    """
    logging.debug('Down and save function called')
    print(ftp)
    if ftp:
        logging.debug('FTP address given as argument')
        try:
            logging.info('Starting Download of %s', ftp)
            os.popen(f'wget -q -o /dev/null {ftp}')
            time.sleep(2)
            logging.debug('Giving time to download')

        except NameError:
            logging.critical('File NOT Downloaded')
            sys.exit(0)
    else:
        logging.debug('FTP address not given (using just the org name'
                      ' will be coded soon)')

    cwd = os.getcwd()
    for file in os.listdir(f'{cwd}/'):
        if file.endswith('.fa.gz'):
            logging.info('Download finished')
            try:
                os.popen(f'gunzip -fd {file}')
                time.sleep(2)
                logging.debug('Giving time up unpack .gz')
            except Exception:
                logging.critical('Gunzip failed to unzip file')
        elif file.endswith('.fa.gz.1'):
            try:
                os.popen(f'gunzip -fd {file}')
            except Exception:
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
    short_save_dir = f'{option.SAVE}{filesavedto}{org}{filecounter}' \
                     f'{data_type}'
    logging.info('Supplied data is %s', data_type)

    if os.path.exists(unzippedfile):
        logging.info('File found at %s', unzippedfile)
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
                    new_name, none_ens_code, none_ens_s, numb_headers,\
                        missing_ens, missing_gene, gene_name, gene_ens,\
                        ens_style_ens = massage(name, data_type)
                    print(new_name)
                elif data_type != 'cdna':
                    logging.debug('%s being used', data_type)
                    new_name, none_ens_code, none_ens_s, numb_headers,\
                        missing_ens, missing_gene, gene_name, gene_ens,\
                        ens_style_ens = massage(name, data_type)
                    print(new_name)

                else:
                    logging.critical('Data type of %s'
                                     ' not recognised.', data_type)
                    sys.exit(0)

                nameseq = new_name, seq

                entry.append(nameseq)
                count += 1

                if count == entryper:
                    filecounter += 1
                    with open(f'{short_save_dir}.MOD.fa', 'w') as done:
                        for head, body in entry:
                            done.write(f'{head}\n{body}\n')

                        count = 0
                        entry = []

                    logging.debug('File saved:\n'
                                  '%s.MOD.fa',
                                  short_save_dir)

                filecounter += 1
            with open(f'{short_save_dir}.MOD.fa', 'w') as done:
                for head, body in entry:
                    done.write(f'{head}\n{body}\n')

                entry = []

            logging.debug(f'File saved:\n{0}'
                          f'{1}.MOD.fa'.format(option.SAVE, short_save_dir))
    else:
        print('Not found')
        logging.debug('Cannot find unzipped file')
        sys.exit(0)

    logging.debug('Entry Function finished')

    return none_ens_code, none_ens_s, numb_headers, missing_ens,\
        missing_gene, gene_name, gene_ens, ens_style_ens


def massage(name, data_type):
    """
    A function to 'massage' the sequence headers into a more human readable
     style
    """
    global NONE_ENS_GENE
    global NONE_ENS_S
    global NUMB_HEADERS
    global MISSING_ENS
    global MISSING_GENE
    global GENE_NAME
    global GENE_ENS
    global ENS_STYLE_ENS

    logging.debug('Massage started')
    if data_type == 'pep' or 'cds' or 'cdna':

        if name.startswith('>'):
            NUMB_HEADERS += 1
            logging.info('Renaming headers')
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
            name = f'>{gene_symbol}({ens_code})'

        else:
            logging.debug('Somethings gone wrongs, headers are corrupt')
            sys.exit(0)

    else:
        logging.debug('Some how you\'ve got to this point'
                      ' with an incorrect data type')
        sys.exit(0)

    logging.debug('Massage finished')
    return name, NONE_ENS_GENE, NONE_ENS_S,\
        NUMB_HEADERS, MISSING_ENS, MISSING_GENE,\
        GENE_ENS, ENS_STYLE_ENS, GENE_NAME


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
        logging.debug('Finished, Your file is here: %s.clean', path)
        print('Primary seqclean site')

    except Exception:
        logging.info('Running alt Seq_clean at wc2/tools/')
        os.popen(f'./nfs/users/nfs_w/wc2/tools/seqclean/seqclean {path}')
        logging.debug('Finished, Your file is here: %s.clean', path)
        print('Secondary seqclean site')

    else:
        logging.debug('Seqclean locations are wrong')

    logging.debug('seqclean finished')


def clean_file_system():
    """
    A function to clean the stray files that appear in the process
    of this script
    """
    logging.debug('Cleaning File System')

    file_type_del = ['*.log', '*.cidx', '*.sort', '*.cln', '*.fa',
                     '*.fa.gz', '*.fa.gz.*', '*.clean', '*sx_file*',
                     '*_tmp']

    for extension in file_type_del:
        os.popen(f'rm {extension}')

    logging.debug('Cleaning File System finished')


if __name__ == '__main__':
    main()
