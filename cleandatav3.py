"""
Version 3 of cleaningdata.py
"""

DOCSTRING = """Bollocks"""
#!/usr/bin/env python3

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
    directory = file_jenny(option.FTP, option.s)

    downandsave(option.FTP, directory)





def file_jenny(ftp, save):
    option = parse_command_args()
    accessrights = 0o755

    org_from_name = re.search(r'fasta\/\w+\/\w+\/(\w+)\S(\w+)', ftp)
    org = org_from_name.group(1)
    accession = org_from_name.group(2)

    org_ass = f'{org}.{accession}'

    directory_naming = [f'/{org}', f'/{org}/{org_ass}', f'/{org}/{org_ass}/cdna', f'/{org}/{org_ass}/pep', f'/{org}/{org_ass}/cds']

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

    return directory_naming


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

            if file.endswith('fa'):
                os.popen(f'mv -d {file} {directory[1]}')
            else:
                logging.critical('Bollocks-2')


if __name__ == '__main__':
    main()
