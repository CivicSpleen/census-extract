"""Ambry Library User Administration CLI

Copyright (c) 2015 Civic Knowledge. This file is licensed under the terms of
the Revised BSD License, included in this distribution as LICENSE.txt

"""

def make_parser(prog_name):

    import argparse

    parser = argparse.ArgumentParser(
        prog=prog_name,
        description='Extract Census data to CSV files')

    cmd = parser.add_subparsers(title='commands', help='command help')

    sp = cmd.add_parser('run', help='Run the web user interface')
    sp.add_argument('ref', type=str, help='Reference to  bundle to extract')
    sp.add_argument('-r', '--remote', help="Remote name to write files to")
    sp.add_argument('-e', '--exception', default=False, action='store_true',
                    help="Re-raise exceptoins after remorting them")
    sp.set_defaults(command=run_extract)

    return parser

def get_library(args):

    from ambry import get_library

    return get_library()


def run_extract(args):
    from . import write_csv

    library = get_library(args)

    write_csv(library, args.ref, args.remote, args.exception)

