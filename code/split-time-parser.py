#! /usr/bin/env python

from lab.parser import Parser

print("Running split time parser")
parser = Parser()
parser.add_pattern("split_time", r"Time for picking split: (\d+)s", type=float)
parser.parse()
