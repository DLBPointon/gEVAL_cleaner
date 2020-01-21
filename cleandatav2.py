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

 - ORG - Organism Name - the name of the orgnaism as it looks
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


    directlist = ['/cleaning_data', '/cleaning_data/entries', '/cleaning_data/downloaded', '/cleaning_data/logs', '/cleaning_data/cleaned']
    accessrights = 0o755

    option = parse_command_args()

    downloadloc = f'{option.s}/cleaning_data/downloaded/'

    if option.o:
        for direct in directlist:
            path = option.s + direct
            if os.path.exists(path):
                print(f'Path: {path} :already exists')
            else:
                try:
                    os.makedirs(path, accessrights)
                except OSError:
                    if option.d:
                        print(f'Creation of directory has failed at: {path}')
                else:
                    if option.d:
                        print(f'''Successfully created the directory path at:
                     {path}''')

        if option.o and option.t:
            if option.d:
                print('Lets do stuff')

            org = downandsave(option.o, option.s, option.t, option.d)

            move_gz_to_direct = os.popen(f'mv *.fa.gz {downloadloc}')
            move_fa_to_direct = os.popen(f'mv *.fa. {downloadloc}')

            decompress(option.s, option.d)

            if option.t == 'cdna':
                # To produce a single file for seqclean
                if option.d:
                    print('First run of entry funtion will clean headers')

                entryfunction(org, option.s, option.t, option.d, 10000000000)

                # seqclean for what should be the only file in the entries
                # folder with the ending all.mod.fa
                # Need to make it so that the finished file form the
                # seqclean is the one that is the input for the second round
                # of entry.
                if option.d:
                    print('DNA will now be split into 5000 seqs per file')

                entryfunction(org, option.s, option.t, option.d, 5000)

            elif option.t == 'pep':
                if option.d:
                    print('Pep splits at 2000 per file')

                entryfunction(org, option.s, option.t, option.d, 2000)

            else:
                if option.d:
                    print('CDs and ncRNA split at 3000 entries per file')

                entryfunction(org, option.s, option.t, option.d, 3000)

        if option.c:
            if option.d:
                print('Cleaning up the files and folders produced my this script')
            rm_redundants(option.s, option.d)

            if option.d:
                print('Cleaning finished')


def downandsave(org, save, data_type, debug=False):
    """
    A function to dowload a user defined file and mv it into the
    downloaded folder.
    """

    if data_type == 'ncrna':
        file_end = '.fa.gz'
    else:
        file_end = '.all.fa.gz'

    if org.startswith('ftp://'):
        try:
            if debug:
                print(f'Downloading: {org}')
            download = os.popen(f'wget -q -o /dev/null {org}')

        except:
            if debug:
                print('''File not downloading: check
                 spelling and whether it exists''')
                sys.exit(0)

        org_from_name = re.search(r'fasta\/(\w+)', org)
        org = org_from_name.group(1)

    else:
        ftp_address = f'''ftp://ftp.ensembl.org/pub/release-98/fasta/
                          {org}/{data_type}/*{data_type}{file_end}'''
        try:
            if debug:
                print(f'Downloading: {ftp_address}')
            download = os.popen(f'''wget -q -o /dev/null
             ftp://ftp.ensembl.org/pub/release-98/fasta/
             {org}/{data_type}/*{data_type}{file_end}''')
        except:
            if debug:
                print('''File not downloading: check spelling and
                 whether it exists''')
            sys.exit(0)

    # else:
    # print('Input format not recognised!\nIs it exactly how the species
    # name appears in the relevant database?\nOr the full link from the
    # database?'

    if org.startswith('ftp://'):
        ftp_name = org.split('/')
        file_name = ftp_name[8]
        print(file_name)

    return org


def decompress(save, debug=False):
    """
    A function to decompress the downloaded file from downandsave().
    """
    file_end = '.fa.gz'

    directory = f'{save}/cleaning_data/downloaded/'
    filefinder = os.listdir(directory)

    for file in filefinder:
        if file.endswith(f'{file_end}'):
            if debug:
                print('Unzipping downloaded file with gunzip')
                try:
                    unzipper = os.popen(f'gunzip {directory}*{file_end}')
                except:
                    if debug:
                        print('No gunzip file found or already unzipped')
                    pass

        else:
            if debug:
                print('No gunzip file found')
            # Nees a sys.exit(0) but will break script


def read_fasta(filetoparse, debug=False):
    """
    A function which opens and splits a fasta into name and seq.
    """
    if debug:
        print('Splitting headers from sequences')
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


def entryfunction(org, save, data_type, debug=False, entryper=1):
    """
    The entryfunction function splits a FASTA file into a defined
    number of entries per file, pep == 2000 enteries and everything
    else is split into 5000 enteries.
    """
    if debug:
        print('Entry Function starting')

    count = 0
    filecounter = 0
    entry = []

    filesavedto = f'{save}/cleaning_data/entries/'
    directory = f'{save}/cleaning_data/downloaded/'

    if data_type == 'ncrna':
        file_uncomp = '.fa'
    else:
        file_uncomp = '.all.fa'

    if entryper >= 10000000000:
        allmod = '.all.MOD'
    else:
        allmod = '.MOD'

    for file in os.listdir(directory):

        # This is for the DNA post seqclean file
        if file.endswith('.all.MOD.fa.clean'):
            unzipped = f'{directory}{file}'
            if debug:
                print(f'File in use:\n{unzipped}')
        # All other files
        if file.endswith('.fa'):
            unzipped = f'{directory}{file}'
            if debug:
                print(f'File in use:\n{unzipped}')

            if os.path.exists(unzipped):
                if debug:
                    print('CAN find the unzipped fasta')

                with open(unzipped, 'r') as filetoparse:
                    for name, seq in read_fasta(filetoparse):

                        # This block controlls cDNA files, the first run
                        # through this would allow massage to modify the
                        # headers, the second run through (to split the
                        # file), massage would be excluded to stop any
                        # possible errors.
                        if data_type == 'cdna':
                            if entryper >= 10000000000:
                                if debug:
                                    print('First round of cleaning for cdna file')
                                new_name = massage(name, data_type)

                            else:
                                if debug:
                                    print('File should should have already been run through massage so it doesn\'t need to again')
                                new_name = massage(name, data_type)

                        elif data_type == 'cds' or 'ncrna':
                            new_name = massage(name, data_type)

                        else:
                            if debug:
                                print('Data type not recognised')
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

                            if debug:
                                print(f'''File saved to:\n{filesavedto}{org}{filecounter}{data_type}{allmod}.fa''')

                        filecounter += 1
                    with open(f'''{filesavedto}{org}{filecounter}{data_type}{allmod}.fa''', 'w') as done:
                        for new_name, seq in entry:
                            done.write(f'{name}\n{seq} \n')

                        entry = []

                    if debug:
                        print(f'''File saved to:\n{filesavedto}{org}{filecounter}{data_type}{allmod}.fa''')
            else:
                if debug:
                    print('CANNOT find the unzipped fasta')
    if debug:
        print('Entry Function Finished')


def massage(name, data_type, debug=False):
    """
    A function to 'massage' the sequence headers into a more human readable
     style
    """

    if data_type == 'pep' or 'cds' or 'dna':
        if debug:
            print(f'This sequence is {data_type} from ensembl.')

        if name.startswith('>'):
            gene_symbol = re.search(r'gene_symbol:(\w+)', name)
            ens_code = re.search(r'ENS(\w+)T(\w+.\d+)', name)

            if gene_symbol:
                gene_symbol = gene_symbol.group(1)
                if debug:
                    print(gene_symbol)
            if gene_symbol == None:
                gene_symbol = re.search(r'EN(\w+)G(\w+)', name)
                gene_symbol = gene_symbol.group(0)

            else: 
                gene_symbol = 'MissingInfo'

            if ens_code:
                ens_code = ens_code.group(0)
                if debug:
                    print(ens_code)
            else:
                ens_code = 'NoEnsCode'

            name = f'>{gene_symbol}({ens_code})'

    elif data_type == 'ncrna':
        if debug:
            print('This is a RefSeq ncRNA sequecne, not coded for that yet.')

    else:
        if debug:
            print('Some how you\'ve got to this point with an incorrect data type')
        sys.exit(0)

    if debug:
        print(name)

    return name


"""
BEYOND THIS POINT IS NOT COMPLETED AND MAY NOT RUN AT ALL
"""


def seqclean(seq, data_type, debug=False):
    """
    A function to sent entry split files to the seqclean perl script,
    this script will clean the sequence to ensure there is nothing that
    requires correcting.
    """

    seqclean_v_check = '/nfs/users/nfs_w/wc2/tools/seqclean -v'
    run_seqclean = os.popen('bsub -o cleanplease.out -K seqlean')
    else_run = os.popen('''bsub -o cleanplease.out -K /nfs/users/nfs_w/
                            wc2/tools/seqclean''')
    option = parse_command_args()
    path = f'{option.s}/cleaning_data/enteries'

    if data_type == 'cdna':
        if os.path.exists(path):
            if debug:
                print('Path to files found')
            for file in os.listdir(path):
                try:
                    set_script = os.popen(f'''bsub -o cleanplease.out
                     -M500 -R\'select[mem>500] rusage[mem=500]
                     \' \\ ~wc2/tools/seqclean/seqclean {file}''')
                except IOError:
                    if debug:
                        print('Command or files are incorrect')

                result = set_script.read()
                result.close()
                if debug:
                    print(f'Finished: {result}')
                # The above should start the perl script and then check to
                # see if the script runs and finishes for each of the fiules
                # passed onto it and then print the file it has finihsed
                # working on
        else:
            if debug:
                print('File paths not found')
            sys.exit(0)

    else:
        if debug:
            print('Seq clean skipped, only for DNA')

    return seq


def rm_redundants(save, debug=False):
    """
    A function to remove all redunant files, an optional.
    """
    directlist = ['/cleaning_data/downloaded', '/cleaning_data/logs']

    extensions = ['.log', '.cidx', '.cln', 'outparts']

    # Add segment about moving the weant to keep files to another folder.

    for direct in directlist:
        path = f'{save}{direct}'
        for file in os.listdir(path):
            for extension in extensions:
                if file.endswith('.clean'):
                    mv_clean = os.popen(f'''mv {save}{directlist}{file}
                                         {save}/cleaning_data/cleaned/''')
                    if debug:
                        print(f'File:\n{file}\nBeing moved to:\n{save}/cleaning_data/cleaned/')
                else:
                    clean_out = os.popen(f'rm -rf {path}')
                    if debug:
                        print(f'Up for deletion is:\n{path}')

    rm_original_dl = os.popen(f'rm ./*.gz')


if __name__ == '__main__':
    main()
