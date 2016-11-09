"""Copyright (c) 2016 Civic Knowledge

This file is licensed under the terms of the MIT License,
included in this distribution as LICENSE

"""

import sys

def main(argsv):
    from cli import make_parser

    parser = make_parser(argsv[0])

    args = parser.parse_args(argsv[1:])

    args.command(args)


main(sys.argv)
