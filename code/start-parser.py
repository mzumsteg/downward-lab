#! /usr/bin/env python

from lab.parser import Parser

def no_search(content, props):
	# Patterns for time and memory have the same structure,
	# they match the same locations but extract different data
	if "search_start_time" not in props:
		error = props.get("error")
		if error is not None and error != "incomplete-search-found-no-plan":
			props["error"] = "no-search-due-to-" + error 

print("Running start time/memory parser")
parser = Parser()
parser.add_pattern("search_start_time", r"\[g=0, 1 evaluated, 0 expanded, t=(.+)s, \d+ KB\]", type=float)
parser.add_pattern("search_start_memory", r"\[g=0, 1 evaluated, 0 expanded, t=.+s, (\d+) KB\]", type=int)
parser.add_function(no_search)
parser.parse()
