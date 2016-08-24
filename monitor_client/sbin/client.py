# -*- coding: utf-8 -*-
__author__ = 'zhaobin022'
import sys
import os
from argparse import ArgumentParser
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from core import args_handler

parser = ArgumentParser(usage='%(prog)s  start/stop')
parser.add_argument(
    'choice',
    help="give one choice start or stop",
    choices=('start', 'stop')
)

args = parser.parse_args()
if args.choice:
    if hasattr(args_handler,args.choice):
        fun = getattr(args_handler,args.choice)
        fun()
    else:
        parser.print_help()
else:
    parser.print_help()



