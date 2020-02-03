#!/usr/bin/env python3

"""
A script to calculate the atomic count of a given amino acid/peptide sequence
"""
import sys
import argparse
import logging

THREE_LETTER = {'A': 'Ala', 'R': 'Arg', 'N': 'Asn', 'D': 'Asp', 'C': 'Cys',
                'E': 'Asn', 'Q': 'Gln', 'G': 'Gly', 'H': 'His', 'I': 'Ile',
                'L': 'Leu', 'K': 'Lys', 'M': 'Met', 'F': 'Phe', 'P': 'Pro',
                'S': 'Ser', 'T': 'Thr', 'W': 'Trp', 'Y': 'Tyr', 'V': 'Val',
                '*': '--'}


def parse_command_args(args=None):
    """
    A function to verify the command line arguments to be passed
    to the rest of the script.
    """
    descformat = argparse.RawDescriptionHelpFormatter

    parser = argparse.ArgumentParser(prog='Clean the gEVAL Supporting DATA',
                                     formatter_class=descformat,
                                     description=DOCSTRING)

    parser.add_argument('seq', '--sequence',
                        action='store',
                        help='The input flag for sequence information')

    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='A flag to collect debug information')

    option = parser.parse_args(args)
    return option


def main():
    """
    A function to control the logic of the script
    """
    option = parse_command_args()

    if option.d:
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s :: %(levelname)s :: %(message)s',
                            filename='peptide_composition.log')


def