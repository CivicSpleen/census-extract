"""Ambry Library User Administration CLI

Copyright (c) 2015 Civic Knowledge. This file is licensed under the terms of
the Revised BSD License, included in this distribution as LICENSE.txt

"""

def make_parser(prog_name, argsv):

    import argparse

    parser = argparse.ArgumentParser(
        prog=prog_name,
        description='')

    sp = parser.add_parser('run', help='Run the web user interface')
    sp.set_defaults(command=run_extract)

def run_extract(args):
    print "here", args
