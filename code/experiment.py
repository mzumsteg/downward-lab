#! /usr/bin/env python

import os.path

from downward.experiment import FastDownwardExperiment

class CEGARExperiment(FastDownwardExperiment):
	def __init__(self, soft_limit=1024, hard_limit=10240, *args, **kwargs):
		FastDownwardExperiment.__init__(self, *args, **kwargs)
		self.soft_limit = soft_limit
		self.hard_limit = hard_limit
		# Add built-in parsers to the experiment.
		self.add_parser(self.EXITCODE_PARSER)
		self.add_parser(self.TRANSLATOR_PARSER)
		self.add_parser(self.SINGLE_SEARCH_PARSER)
		self.add_parser(self.PLANNER_PARSER)
		# Add custom parsers to the experiment.
		DIR = os.path.dirname(os.path.abspath(__file__))
		self.add_parser(os.path.join(DIR, "start-parser.py"))
		self.add_parser(os.path.join(DIR, "split-time-parser.py"))
	
	def _add_runs(self):
		FastDownwardExperiment._add_runs(self)
		for run in self.runs:
			command = run.commands["planner"]
			command[1]['soft_stdout_limit'] = self.soft_limit
			command[1]['hard_stdout_limit'] = self.hard_limit
