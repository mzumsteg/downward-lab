#! /usr/bin/env python

import re
import logging

from lab.parser import Parser

class MultiPattern:
    def __init__(self, attribute, regex, mapper, required=False, flags=''):
        self.attribute = attribute
        self.mapper = mapper
        self.required = required

        flag = 0
        for char in flags:
            try:
                flag |= getattr(re, char)
            except AttributeError:
                logging.critical('Unknown pattern flag: {}'.format(char))

        self.regex = re.compile(regex, flag)

    def search(self, content, filename):
        found_items = []
        for match in self.regex.finditer(content):
            value = self.mapper(match)
            found_items.append(value)
        if self.required and not found_items:
            logging.error('Pattern "%s" not found in %s' % (self, filename))
        return {self.attribute: found_items}

    def __str__(self):
        return self.regex.pattern

class HParser(Parser):
    def add_special_pattern(self, pattern, file='run.log'):
        self.file_parsers[file].add_pattern(pattern)

print("Running heuristic information parser")
parser = HParser()
parser.add_special_pattern(MultiPattern("h_split_statistics",
        r"Best heuristic value \(N = (\d+)\): (.+) \((\d+) distinct\)",
        lambda m: [int(m.group(1)), float(m.group(2)), int(m.group(3))]))
parser.parse()
