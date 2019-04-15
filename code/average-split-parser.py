#! /usr/bin/env python

from lab.parser import Parser

print("Running average split parser")
parser = Parser()
parser.add_pattern("average_split_options", r"Average number of possible splits: (.+)", type=float)
parser.add_pattern("average_distinct_rated", r"Average number of distinct ratings: (.+)", type=float)
parser.parse()
