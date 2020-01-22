#!/usr/bin/env python3
"""Please use ./cleandata.py -h for the full __doc__"""

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

try:
    import logging

    print('logging imported')
except ImportError:
    print(f'logging not imported \n {PRINT_ERROR}')
    sys.exit(0)


DOCSTRING = """
-------------------------------------------------------------
                        cleandata.py
-------------------------------------------------------------
                Cleaning gEVAL supporting DATA
                          By dp24
        Updated from wc2's clean_gEVALsupport_data.sh
-------------------------------------------------------------
            IMPORTANT NOTES BEOFRE CARRYING ON
        This script is written in for python3.7

                    IMPORT MODULES

            argparse - for command interface
            os       - for os interface
            sys      - for system interfacing
                       mainly just sys.exit(0) 
            re       - for regex usage
            __________________________________
            logging
-------------------------------------------------------------
USE CASE FOR THE SCRIPT
1, The aim of this script is to take an input FASTA file
(whether cdna/cds/pep or rna) from ensembl or refseq.

2, Next the headers will be massaged into a standardised
format.

3, The sequence (dependant on type) will then be cleaned by
 the use of the seqclean script.

4, Sequences are then trimmed.

5, Finally the sequences are split into user defined entries
per file.
-------------------------------------------------------------
USAGE INSTRUCTIONS

./cleandata.py -TYPE cdna -ORG mesocricetus_auratus -SAVE ./test

or

./cleandata.py -TYPE cdna -ORG ftp://ftp.ensembl.org/pub/
release-98/fasta/mesocricetus_auratus/cdna/Mesocricetus_auratus.
MesAur1.0.cdna.all.fa.gz -SAVE ./test

Optionals include --clean and/or --debug
-------------------------------------------------------------
ARGUMENTS
 - SAVE - ./test

 - ORG - Organism Name - the name of the organism as it looks
  in the respective database.

 - TYPE - will be a choice between cdna/cds/pep/rna

 - PRE - Prefix - will be the user defined naming scheme
  - NOT IN USE

 --clean - and optional argument to remove parent files

 --debug - Used to diagnose issues with the running of the
  script
-------------------------------------------------------------

FUTURE CHANGES
    - More sanity checking
-------------------------------------------------------------
CONTACT
    - dp24@sanger.ac.uk
-------------------------------------------------------------
FILE STRUCTURE
                SAVE location
                -------------
                      |
                      |
                Cleaning_Data
                      |
                      |
    ----------------------------------
    |           |           |       |
    |           |           |       |
Downloaded   Enteries     Logs    cleaned
--------------------------------------------------------------
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

    parser.add_argument('--debug',
                        action='store_true',
                        help='''Specifying this argument allows debug
                         prints to work and show everything the script is
                         doing''',
                        dest='d')

    option = parser.parse_args(args)
    return option


def main():
    """
    A function containing the controlling logic of the script
    """
    option = parse_command_args()

    directlist = ['/cleaning_data', '/cleaning_data/entries', '/cleaning_data/downloaded', '/cleaning_data/logs',
                  '/cleaning_data/cleaned']
    accessrights = 0o755

    downloadloc = f'{option.s}/cleaning_data/downloaded/'

    if option.d:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s',
                            filename='gEVAL_clean.log')

    if option.o:
        for direct in directlist:
            path = option.s + direct
            if os.path.exists(path):
                logging.info(f'Path: {path} :already exists')
            else:
                try:
                    os.makedirs(path, accessrights)
                except OSError:
                    logging.critical(f'Creation of directory has failed at: {path}')
                else:
                    logging.info(f'''Successfully created the directory path at:
                     {path}''')

        if option.o and option.t:
            logging.info('Args accepted - Lets do stuff')
            org = downandsave(option.o, option.t)

            try:
                move_gz_to_direct = os.popen(f'mv *.fa.gz {downloadloc}')
            except:
                logging.info('No zipped file found, in current directory')

            try:
                move_fa_to_direct = os.popen(f'mv *.fa.gz {downloadloc}')
            except:
                logging.info('No unzipped file found, in current directory')

            try:
                rm_excess_gza = os.popen(f'rm *.fa.gz*')
            except:
                logging.info('Removing excess fa.gz.* files')

            decompress(option.s)

            if option.t == 'cdna':
                logging.info('First run of entry funtion will clean headers and produce a singular file for seqclean')
                entryfunction(org, option.s, option.t, 10000000000)

                # seqclean for what should be the only file in the entries
                # folder with the ending all.mod.fa
                # Need to make it so that the finished file form the
                # seqclean is the one that is the input for the second round
                # of entry.

                logging.info('DNA will now be split into 5000 seqs per file')
                entryfunction(org, option.s, option.t, 5000)

            elif option.t == 'pep':
                logging.info('Pep splits at 2000 per file')
                entryfunction(org, option.s, option.t, 2000)

            else:
                logging.info('CDs and ncRNA split at 3000 entries per file')
                entryfunction(org, option.s, option.t, 3000)

        if option.c:
            rm_redundants(option.s)


def downandsave(org, data_type):
    """
    A function to dowload a user defined file and mv it into the
    downloaded folder.
    """
    logging.debug('Downandsave called')

    if data_type == 'ncrna':
        file_end = '.fa.gz'
    else:
        file_end = '.all.fa.gz'

    if org.startswith('ftp://'):
        try:
            logging.info(f'Starting Download of {org}')
            download = os.popen(f'wget -q -o /dev/null {org}')
            logging.info('Download finished')

        except:
            logging.critical('File NOT Downloaded')
            sys.exit(0)

        org_from_name = re.search(r'fasta\/(\w+)', org)
        org = org_from_name.group(1)
        logging.info('Name pulled from FTP address')

    else:
        logging.info('FTP address not giving, creating one from args')
        ftp_address = f'''ftp://ftp.ensembl.org/pub/release-98/fasta/
                          {org}/{data_type}/*{data_type}{file_end}'''
        try:
            logging.info('Attempting to download the created FTP address')
            download = os.popen(f'''wget -q -o /dev/null
             ftp://ftp.ensembl.org/pub/release-98/fasta/
             {org}/{data_type}/*{data_type}{file_end}''')
            logging.info('Download complete')
        except:
            logging.critical('Download NOT performed, error in org name is most likely.')
            sys.exit(0)

    logging.debug('Downandsave finished')
    return org


def decompress(save):
    """
    A function to decompress the downloaded file from downandsave().
    """
    logging.debug('Decompress called')
    file_end = '.fa.gz'

    directory = f'{save}/cleaning_data/downloaded/'
    filefinder = os.listdir(directory)

    for file in filefinder:

        if file.endswith(file_end):
            logging.debug('File to unzip Found')
            try:
                logging.info(f'Starting Decompression of {file}')
                os.popen(f'gunzip {directory}{file}*')
                logging.info('Decompression Complete')
            except:
                logging.critical('Decompression cannot be completed, check the file?')

        else:
            logging.critical('File to decompress not found')
            sys.exit(0)

    logging.debug('Decompression finished')


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
    logging.info('Entery produced')


def entryfunction(org, save, data_type, entryper=1):
    """
    The entryfunction function splits a FASTA file into a defined
    number of entries per file, pep == 2000 enteries and everything
    else is split into 5000 enteries.
    """
    logging.debug('Entryfunction called')

    count = 0
    filecounter = 0
    entry = []

    filesavedto = f'{save}/cleaning_data/entries/'
    directory = f'{save}/cleaning_data/downloaded/'

    if data_type == 'ncrna':
        logging.info('ncrna data type used')
        file_uncomp = '.fa'
        file_ex = '.fna'
        if org.startswith('ftp://'):

            if 'GCF' in org:
                logging.info('FTP address being split to find the organism name (GCF name)')
                org = re.search(r'GC\w+...(\w+\S\d.\d.\d\S){3}', org)
                org = org.group(1)
            elif 'GCA' in org:
                logging.info('FTP address being split to find the organism name (GCA name)')
                org = re.search(r'GC\w+...(\w+){3}', org)
                org = org.group(1)
            else:
                if org == None:
                    logging.info('Regex cannot find org name in FTP address, using simpler method.')
                    org_split = org.split('/')
                    org = org_split[10]
                    org_split2 = org.split('_')
                    org = org_split2[1:].join('')
    else:
        logging.info('Standard latin name provided')
        file_uncomp = '.all.fa'
        file_ex = '.fa'

    if entryper >= 10000000000:
        logging.info('cDNA file supplied - First run to return a complete multi-fasta')
        allmod = '.all.MOD'
    else:
        if data_type == 'ncrna':
            logging.info('ncRNA supplied')
            allmod = ''
        else:
            logging.info(f'Supplied data is not ncRNA - it is {data_type}')
            allmod = '.MOD'

    for file in os.listdir(directory):
        # This is for the DNA post seqclean file
        if file.endswith('.all.MOD.fa.clean'):
            unzipped = f'{directory}{file}'
            logging.debug(f'File to be used: {unzipped}')
        # All other files
        elif file.endswith('.fa'):
            unzipped = f'{directory}{file}'
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

                        elif data_type == 'cds' or 'ncrna' or 'pep':
                            logging.debug(f'{data_type} being used')
                            new_name = massage(name, data_type)
                            if data_type == 'ncra':
                                data_type = ''
                                allmod = ''

                        else:
                            logging.critical(f'Data type of {data_type} not recognised.')
                            sys.exit(0)

                        nameseq = new_name, seq
                        entry.append(nameseq)
                        count += 1

                        if count == entryper:
                            filecounter += 1
                            with open(f'''{filesavedto}{org}{filecounter}{data_type}{allmod}.fa''', 'w') as done:
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
                logging.debug('Cannot find unzipped file')
                sys.exit(0)

        else:
            logging.debug('File extension is not .all.MOD.fa or .fa, still zipped maybe?')
            sys.exit(0)

    logging.debug('Entry Function finished')


def massage(name, data_type):
    """
    A function to 'massage' the sequence headers into a more human readable
     style
    """
    logging.debug('Massage started')
    if data_type == 'pep' or 'cds' or 'dna':
        logging.info(f'This sequence is {data_type} from ensembl.')

        if name.startswith('>'):
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

            name = f'>{gene_symbol}({ens_code})'

    elif data_type == 'ncrna':
        logging.info('This is a RefSeq ncRNA sequecne, not coded for that yet.')

    else:
        logging.debug('Some how you\'ve got to this point with an incorrect data type')
        sys.exit(0)

    logging.debug('Massage finished')
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

    logging.debug('Seqclean called')

    seqclean_v_check = '/nfs/users/nfs_w/wc2/tools/seqclean -v'
    run_seqclean = os.popen('bsub -o cleanplease.out -K seqlean')
    else_run = os.popen('''bsub -o cleanplease.out -K /nfs/users/nfs_w/
                            wc2/tools/seqclean''')
    option = parse_command_args()
    path = f'{option.s}/cleaning_data/enteries'

    if data_type == 'cdna':
        if os.path.exists(path):
            logging.info('Path to files found')
            for file in os.listdir(path):
                if file.endswith(f'{data_type}.all.MOD.fa'):
                    try:
                        set_script = os.popen(f'''bsub -o cleanplease.out
                         -M500 -R\'select[mem>500] rusage[mem=500]
                         \' \\ ~wc2/tools/seqclean/seqclean {file}''')
                    except IOError:
                        logging.debug('Command or files are incorrect')

                result = set_script.read()
                result.close()
                logging.debug(f'Finished: {result}')
            # The above should start the perl script and then check to
            # see if the script runs and finishes for each of the fiules
            # passed onto it and then print the file it has finihsed
            # working on
        else:
            logging.critical('File paths not found')
            sys.exit(0)

    else:
        logging.debug('Seq clean skipped, only for DNA')
        sys.exit(0)

    logging.debug('seqclean finished')
    return seq


def rm_redundants(save):
    """
    A function to remove all redunant files, an optional.
    """
    logging.debug('rm_redundants called')
    directlist = ['/cleaning_data/downloaded', '/cleaning_data/logs']

    extensions = ['.log', '.cidx', '.cln', 'outparts']

    # Add segment about moving the weant to keep files to another folder.

    for direct in directlist:
        path = f'{save}{direct}'
        for file in os.listdir(path):
            for extension in extensions:
                if file.endswith('.clean'):
                    mv_clean = os.popen(f'''mv {save}{direct}{file}
                                        {save}/cleaning_data/cleaned/''')
                    logging.debug(f'File:\n{file}\nBeing moved to:\n{save}/cleaning_data/cleaned/')
                else:
                    clean_out = os.popen(f'rm -rf {path}')
                    logging.debug(f'Up for deletion is:\n{path}')

    rm_original_dl = os.popen(f'rm ./*.gz')
    logging.debug('rm_redundants removed')

if __name__ == '__main__':
    main()
