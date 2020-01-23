"""
Version 3 of cleaningdata.py
"""

DOCSTRING = """Bollocks"""
# !/usr/bin/env python3

PRINT_ERROR = '''Does not exist\n
                 Get module installed before import attempt\n
                 If running server side then contact your admin'''

try:
    import sys

    if sys.version_info[0] < 3 and sys.version_info[1] < 6:
        raise Exception("""Must be using Python 3.7 for the full
                        functionality of this script""")
    if sys.version_info[0] >= 3 and sys.version_info[1] >= 6:
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

try:
    import logging

    print('logging imported')
except ImportError:
    print(f'logging not imported \n {PRINT_ERROR}')
    sys.exit(0)


# input -ftp of full FTP address
# save remains the same

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

    parser.add_argument('-TYPE',
                        type=str,
                        choices=['cds', 'cdna', 'pep', 'ncrna'],
                        help='The type of DATA contained in the file',
                        dest='t')

    parser.add_argument('--prefix',
                        type=str,
                        action='store',
                        help='User-defined naming scheme',
                        dest='p')

    parser.add_argument('--ORGNAME',
                        type=str,
                        action='store',
                        help='''The Organism under scrutiny
                                   (use how the name would appear in ensembl
                                   to make life easier, long name)''',
                        dest='o')

    parser.add_argument('-SAVE',
                        type=str,
                        action='store',
                        help='Save location for the downloaded files',
                        dest='s')

    parser.add_argument('--clean',
                        action='store_true',
                        help='''Specifying this argument allows the
                         script to clean all un-nessasery files after
                         use''',
                        dest='c')

    parser.add_argument('--debug',
                        action='store_true',
                        help='''Specifying this argument allows debug
                         prints to work and show everything the script is
                         doing''',
                        dest='d')

    parser.add_argument('-FTP',
                        action='store',
                        type=str)

    option = parser.parse_args(args)
    return option


def main():
    option = parse_command_args()

    if option.d:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s',
                            filename='gEVAL_clean.log')

    print(option.FTP)
    org, directory = file_jenny(option.FTP, option.s)

    downandsave(option.FTP, directory)

    if option.t == 'cdna':
        entryfunction(org, directory, option.t, entryper=100000000000)

        entryfunction(org, directory, option.t, entryper=5000)

    elif option.t == 'pep':
        entryfunction(org, directory, option.t, entryper=2000)

    else:
        entryfunction(org, directory, option.t, entryper=3000)


def file_jenny(ftp, save):
    option = parse_command_args()
    accessrights = 0o755

    org_from_name = re.search(r'fasta\/\w+\/\w+\/(\w+)\S(\w+)', ftp)
    org = org_from_name.group(1)
    accession = org_from_name.group(2)

    org_ass = f'{org}.{accession}'

    directory_naming = [f'/{org}', f'/{org}/{org_ass}', f'/{org}/{org_ass}/cdna', f'/{org}/{org_ass}/pep',
                        f'/{org}/{org_ass}/cds']

    for direct in directory_naming:
        path = option.s + direct
        if os.path.exists(path):
            print(f'Path: {path} :already exists')
        else:
            try:
                os.makedirs(path, accessrights)
            except OSError:
                logging.critical(f'Creation of directory has failed at: {path}')
            else:
                logging.info(f'''Successfully created the directory path at:
                                     {path}''')

    return org, directory_naming


def downandsave(ftp, directory):
    option = parse_command_args()

    if option.FTP:
        try:
            logging.info(f'Starting Download of {option.FTP}')
            os.popen(f'wget -q -o /dev/null {option.FTP}')
            logging.info('Download finished')
        except:
            logging.critical('File NOT Downloaded')
            sys.exit(0)

        for file in os.listdir('./'):
            if file.endswith('.fa.gz'):
                os.popen(f'gunzip -fd {file}')
            else:
                logging.critical('Bollocks-1')


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
                yield (name, ''.join(seq))
            name, seq = line, []
        else:
            seq.append(line)

    if name:
        yield (name, ''.join(seq))
    logging.info('Entry produced')


def entryfunction(org, directory, data_type, entryper=1):
    """
    The entryfunction function splits a FASTA file into a defined
    number of entries per file, pep == 2000 enteries and everything
    else is split into 5000 enteries.
    """
    logging.debug('Entryfunction called')

    count = 0
    filecounter = 0
    entry = []

    filesavedto = f'.{directory[1]}/{data_type}/'
    print(filesavedto)

    file_uncomp = '.all.fa'
    file_ex = '.fa'

    if entryper >= 10000000000:
        logging.info('cDNA file supplied - First run to return a complete multi-fasta')
        allmod = '.all.MOD'
    else:
        logging.info(f'Supplied data is {data_type}')
        allmod = '.MOD'

    cwd = os.getcwd()
    for root, dirs, files in os.walk(f'{cwd}/{option.s}/'):
        print(files)
        unzippedfile = f'{option.s}/{files[0]}'
        print(unzippedfile)
        if unzippedfile.endswith('.fa'):
            unzipped = f'{fullpath}'
            print(unzipped)
            logging.debug(f'File to be used: {unzipped}')

            if os.path.exists(unzipped):
                logging.info(f'File found at {unzipped}')

                with open(unzipped, 'r') as filetoparse:
                    for name, seq in read_fasta(filetoparse):

                        # This block controlls cDNA files, the first run
                        # through this would allow massage to modify the
                        # headers, the second run through (to split the
                        # file), massage would be excluded to stop any
                        # possible errors.
                        if data_type == 'cdna':
                            if entryper >= 10000000000:
                                logging.debug('First round of cleaning for cDNA file in Massage')
                                new_name = massage(name, data_type)

                            else:
                                logging.debug('Second round of cDNA through Massage')
                                new_name = massage(name, data_type)

                        elif data_type == 'cds' or 'pep':
                            logging.debug(f'{data_type} being used')
                            new_name = massage(name, data_type)

                        else:
                            logging.critical(f'Data type of {data_type} not recognised.')
                            sys.exit(0)

                        nameseq = new_name, seq
                        entry.append(nameseq)
                        count += 1

                        if count == entryper:
                            filecounter += 1
                            with open(f'''{filesavedto}{org}{filecounter}{data_type}{allmod}{file_ex}''', 'w') as done:
                                for name, seq in entry:
                                    done.write(f'{name}\n{seq} \n')

                                count = 0
                                entry = []

                            logging.debug(f'File saved:\n{filesavedto}{org}{filecounter}{data_type}{allmod}{file_ex}')

                        filecounter += 1
                    with open(f'''{filesavedto}{org}{filecounter}{data_type}{allmod}{file_ex}''', 'w') as done:
                        for name, seq in entry:
                            done.write(f'{name}\n{seq} \n')

                        entry = []

                    logging.debug(f'File saved:\n{filesavedto}{org}{filecounter}{data_type}{allmod}{file_ex}')
            else:
                print('Nope not found')
                logging.debug('Cannot find unzipped file')
                sys.exit(0)

        else:
            logging.debug('File extension is not .fa, still zipped maybe?')
            sys.exit(0)

    logging.debug('Entry Function finished')


def massage(name, data_type):
    """
    A function to 'massage' the sequence headers into a more human readable
     style
    """
    logging.debug('Massage started')
    if data_type == 'pep' or 'cds' or 'dna':

        if name.startswith('>'):
            logging.info('Renaming headers')
            gene_symbol = re.search(r'symbol:(\w+\S+)', name)
            ens_code = re.search(r'ENS(\w+)T(\w+.\d+)', name)

            if gene_symbol:
                gene_symbol = gene_symbol.group(1)

            elif gene_symbol is None:
                gene_symbol = re.search(r'ENS(\w+)G(\w+.\d+)', name)
                gene_symbol = gene_symbol.group(0)

            else:
                gene_symbol = 'MissingInfo'

            if ens_code:
                ens_code = ens_code.group(0)

            else:
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
    return name


if __name__ == '__main__':
    main()
