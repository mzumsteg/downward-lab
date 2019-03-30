#! /usr/bin/env python

"""Solve some tasks with A* and the CEGAR heuristic."""

import os
import os.path
import platform

from lab.environments import LocalEnvironment, BaselSlurmEnvironment

from downward.experiment import FastDownwardExperiment
from downward.reports.absolute import AbsoluteReport
from downward.reports.scatter import ScatterPlotReport


ATTRIBUTES = ["coverage", "error", "expansions_until_last_jump", "initial_h_value", "search_start_time", "search_start_memory", "split_time"]

NODE = platform.node()
if NODE.endswith(".scicore.unibas.ch") or NODE.endswith(".cluster.bc2.ch"):
	SUITE = ['agricola-opt18-strips', 'airport', 'barman-opt11-strips', 'barman-opt14-strips', 'blocks', 'childsnack-opt14-strips', 'data-network-opt18-strips', 'depot', 'driverlog', 'elevators-opt08-strips', 'elevators-opt11-strips', 'floortile-opt11-strips', 'floortile-opt14-strips', 'freecell', 'ged-opt14-strips', 'grid', 'gripper', 'hiking-opt14-strips', 'logistics00', 'logistics98', 'miconic', 'movie', 'mprime', 'mystery', 'nomystery-opt11-strips', 'openstacks-opt08-strips', 'openstacks-opt11-strips', 'openstacks-opt14-strips', 'openstacks-strips', 'organic-synthesis-opt18-strips', 'organic-synthesis-split-opt18-strips', 'parcprinter-08-strips', 'parcprinter-opt11-strips', 'parking-opt11-strips', 'parking-opt14-strips', 'pathways-noneg', 'pegsol-08-strips', 'pegsol-opt11-strips', 'petri-net-alignment-opt18-strips', 'pipesworld-notankage', 'pipesworld-tankage', 'psr-small', 'rovers', 'satellite', 'scanalyzer-08-strips', 'scanalyzer-opt11-strips', 'snake-opt18-strips', 'sokoban-opt08-strips', 'sokoban-opt11-strips', 'spider-opt18-strips', 'storage', 'termes-opt18-strips', 'tetris-opt14-strips', 'tidybot-opt11-strips', 'tidybot-opt14-strips', 'tpp', 'transport-opt08-strips', 'transport-opt11-strips', 'transport-opt14-strips', 'trucks-strips', 'visitall-opt11-strips', 'visitall-opt14-strips', 'woodworking-opt08-strips', 'woodworking-opt11-strips', 'zenotravel']
	ENV = BaselSlurmEnvironment(email="mar.zumsteg@stud.unibas.ch")
else:
	SUITE = ['depot:p01.pddl', 'gripper:prob01.pddl', 'mystery:prob07.pddl']
	ENV = LocalEnvironment(processes=2)
# Use path to your Fast Downward repository.
REPO = os.environ["DOWNWARD_REPO"]
BENCHMARKS_DIR = os.environ["DOWNWARD_BENCHMARKS"]
REVISION_CACHE = os.path.expanduser('~/lab/revision-cache')

exp = FastDownwardExperiment(environment=ENV, revision_cache=REVISION_CACHE)

# Add built-in parsers to the experiment.
exp.add_parser(exp.EXITCODE_PARSER)
exp.add_parser(exp.TRANSLATOR_PARSER)
exp.add_parser(exp.SINGLE_SEARCH_PARSER)
exp.add_parser(exp.PLANNER_PARSER)
# Add custom parsers to the experiment.
DIR = os.path.dirname(os.path.abspath(__file__))
exp.add_parser(os.path.join(DIR, "start-parser.py"))
exp.add_parser(os.path.join(DIR, "split-time-parser.py"))

exp.add_suite(BENCHMARKS_DIR, SUITE)
exp.add_algorithm('random', REPO, 'refinement-strategies',
	['--search', 'astar(cegar(subtasks=[original()], max_states=10K, max_transitions=infinity, max_time=infinity, pick=RANDOM))'])
exp.add_algorithm('min_cg', REPO, 'refinement-strategies',
	['--search', 'astar(cegar(subtasks=[original()], max_states=10K, max_transitions=infinity, max_time=infinity, pick=MIN_CG))'])
exp.add_algorithm('max_cg', REPO, 'refinement-strategies',
	['--search', 'astar(cegar(subtasks=[original()], max_states=10K, max_transitions=infinity, max_time=infinity, pick=MAX_CG))'])

# Add step that writes experiment files to disk.
exp.add_step('build', exp.build)

# Add step that executes all runs.
exp.add_step('start', exp.start_runs)

# Add step that collects properties from run directories and
# writes them to *-eval/properties.
exp.add_fetcher(name='fetch')

# Add report step (AbsoluteReport is the standard report).
exp.add_report(
	AbsoluteReport(attributes=ATTRIBUTES), outfile='report.html')

# Add scatter plot report step.
def addScatterPlot(attrib, algorithm, compare="random"):
	filename = 'scatter-' + attrib + '-' + algorithm
	if compare != "random":
		filename = filename + '-' + compare
	exp.add_report(
		ScatterPlotReport(attributes=[attrib], filter_algorithm=[compare, algorithm]),
	outfile=filename + '.png')
addScatterPlot("expansions_until_last_jump", "min_cg")
addScatterPlot("expansions_until_last_jump", "max_cg")
addScatterPlot("search_start_time", "min_cg")
addScatterPlot("search_start_time", "max_cg")

# Parse the commandline and show or run experiment steps.
exp.run_steps()
