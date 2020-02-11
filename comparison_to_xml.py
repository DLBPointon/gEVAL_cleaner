#!/usr/bin/env python3

"""
comparison_to_TSV.py
"""

DOCSTRING = """
-------------------------------------------------------------
                    comparison_to_TSV.py
A script to take the TSV from the downloaded results from
ensembl (relavent database [metazoa, genomes, bacteria, 
                            protists, fungi, plants, 
                            vertebrates])
and compare the pulled down games IDs and names to what is
contained in the multifasta files produced by the main
cleandatav3.py script.

This will will also aim to replace all unnecessary naming
with proper stable naming.

-------------------------------------------------------------
CONTACT
    - dp24@sanger.ac.uk
            or
    - grit@sanger.ac.uk
-------------------------------------------------------------
FILE STRUCTURE TO USE - if save of previous script == './'
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

try:
    import sys

    if sys.version_info[0] < 3 and sys.version_info[1] < 6:
        raise Exception("""Must be using Python 3.6 for the full
                        functionality of this script""")
    if sys.version_info[0] >= 3 and sys.version_info[1] >= 6:
        print('Your using at least Version 3.6, You are good to go...')
except ImportError:
    print(f'sys not imported')
    sys.exit(0)

try:
    import pandas as pd

    print('pandas imported')
except ImportError:
    print(f'pandas not imported')
    sys.exit(0)

try:
    import argparse

    print('argparse imported')
except ImportError:
    print(f'argparse not imported')
    sys.exit(0)

try:
    import os

    print('os imported')
except ImportError:
    print(f'os not imported')
    sys.exit(0)

try:
    import re

    print('regex imported')
except ImportError:
    print(f're not imported')
    sys.exit(0)

try:
    import logging

    print('logging imported')
except ImportError:
    print(f'logging not imported')
    sys.exit(0)


def parse_command_args(args=None):
    """
    A function to verify the command line arguments to be passed
    to the rest of the script.
    """
    descformat = argparse.RawDescriptionHelpFormatter

    parser = argparse.ArgumentParser(prog='compare ensembl data to that contained in the multifastas',
                                     formatter_class=descformat,
                                     description=DOCSTRING)

    parser.add_argument('-TSV',
                        action='store',
                        help='''This flag is the address of the TSV downloaded from biomart''',
                        type=str,
                        dest='f')

    parser.add_argument('--MFL',
                        help='A flag for the location of the FOLDER holding the files produced by cleandatav3.py',
                        type=str,
                        dest='m')

    option = parser.parse_args(args)
    return option


def main():
    """
    The Main function which controls the logic for the script
    """
    option = parse_command_args()
    rowsandstuff = {}
    counter_already = 0
    no_gene_name = 0
    new_gene_name = 0
    not_present_in_homo_comp = 0

    with open(f'{option.f}', 'r') as martfile:
        for line in martfile:
            row = line.strip().split('\t')
            rowsandstuff[row[0]] = row

    for file in os.listdir(f'{option.m}'):
        with open(f'{option.m}{file}') as reading:
            for line in reading:
                if line.startswith('>'):
                    line = re.search(r'>(\w+)', line)
                    line = line.group(1)
                    if line.startswith('AGAP'):
                        try:
                            if rowsandstuff[line]:
                                try:
                                    if rowsandstuff[line][3] != '':
                                        print(rowsandstuff[line][3])
                                        new_gene_name += 1
                                except:
                                    # print('No Gene Name')
                                    no_gene_name += 1
                            else:
                                no_gene_name += 1
                        except:
                            # Gets rid of those not in the homologue comparison dict
                            not_present_in_homo_comp += 1
                    else:
                        # print('Gene Name already there')
                        counter_already += 1

            print(f' new genes = {new_gene_name}'
                  f'\n no gene name = {no_gene_name}'
                  f'\n gene already there = {counter_already}'
                  f'\n homologue comp = {not_present_in_homo_comp}')


if __name__ == '__main__':
    main()
