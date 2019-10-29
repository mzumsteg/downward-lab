#! /usr/bin/env python

"""Solve some tasks with A* and the CEGAR heuristic."""

import os
import os.path
import platform

from lab.environments import LocalEnvironment, BaselSlurmEnvironment

from lab.reports import Attribute
from experiment import CEGARExperiment
from downward.reports.absolute import AbsoluteReport
from downward.reports.scatter import ScatterPlotReport

from per_task_comparison import PerTaskComparison
from relativescatter import RelativeScatterPlotReport
from best_tabular import BestTabularReport

def mean(list):
    return sum(list) / len(list)
ATTRIBUTES = ["coverage", "error", "expansions_until_last_jump", "initial_h_value",
    "search_start_time", "search_start_memory"]

NODE = platform.node()
if NODE.endswith(".scicore.unibas.ch") or NODE.endswith(".cluster.bc2.ch"):
	SUITE = ['agricola-opt18-strips', 'airport', 'barman-opt11-strips', 'barman-opt14-strips', 'blocks', 'childsnack-opt14-strips', 'data-network-opt18-strips', 'depot', 'driverlog', 'elevators-opt08-strips', 'elevators-opt11-strips', 'floortile-opt11-strips', 'floortile-opt14-strips', 'freecell', 'ged-opt14-strips', 'grid', 'gripper', 'hiking-opt14-strips', 'logistics00', 'logistics98', 'miconic', 'movie', 'mprime', 'mystery', 'nomystery-opt11-strips', 'openstacks-opt08-strips', 'openstacks-opt11-strips', 'openstacks-opt14-strips', 'openstacks-strips', 'organic-synthesis-opt18-strips', 'organic-synthesis-split-opt18-strips', 'parcprinter-08-strips', 'parcprinter-opt11-strips', 'parking-opt11-strips', 'parking-opt14-strips', 'pathways-noneg', 'pegsol-08-strips', 'pegsol-opt11-strips', 'petri-net-alignment-opt18-strips', 'pipesworld-notankage', 'pipesworld-tankage', 'psr-small', 'rovers', 'satellite', 'scanalyzer-08-strips', 'scanalyzer-opt11-strips', 'snake-opt18-strips', 'sokoban-opt08-strips', 'sokoban-opt11-strips', 'spider-opt18-strips', 'storage', 'termes-opt18-strips', 'tetris-opt14-strips', 'tidybot-opt11-strips', 'tidybot-opt14-strips', 'tpp', 'transport-opt08-strips', 'transport-opt11-strips', 'transport-opt14-strips', 'trucks-strips', 'visitall-opt11-strips', 'visitall-opt14-strips', 'woodworking-opt08-strips', 'woodworking-opt11-strips', 'zenotravel']
	ENV = BaselSlurmEnvironment(email="mar.zumsteg@stud.unibas.ch")
else:
	SUITE = ['depot:p01.pddl', 'depot:p02.pddl',
		'gripper:prob01.pddl', 'gripper:prob02.pddl', 'gripper:prob03.pddl',
		'mystery:prob01.pddl', 'mystery:prob03.pddl']
	ENV = LocalEnvironment(processes=6)
# Use path to your Fast Downward repository.
REPO = os.environ["DOWNWARD_REPO"]
BENCHMARKS_DIR = os.environ["DOWNWARD_BENCHMARKS"]
REVISION_CACHE = os.path.expanduser('~/lab/revision-cache')

exp = CEGARExperiment(soft_limit=20*1024, hard_limit=50*1024, environment=ENV, revision_cache=REVISION_CACHE)
exp.add_suite(BENCHMARKS_DIR, SUITE)

splitters = ["RANDOM", "MAX_REFINED", "MIN_CG", "MAX_CG"]
samplers = ["RANDOM_WALK", "RANDOM_SYN", "RANDOM_VALID"]
algorithms = [(split, smpl) for split in splitters for smpl in samplers]
for split, smpl in algorithms:
	exp.add_algorithm(split.lower() + "-" + smpl.lower(), REPO, 'sampling-strategies',
		['--search', 'astar(saturated_cost_partitioning([cartesian([landmarks(order=random, random_seed=0), goals(order=random, random_seed=0)], pick=' + split + ')], max_time=200, max_orders=infinity, diversify=true, sampler=' + smpl + ', max_optimization_time=0))'])
alg_names = [split.lower() + "-" + smpl.lower() for split, smpl in algorithms]

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
exp.add_report(
	PerTaskComparison(sort=True, attributes=["expansions_until_last_jump"]), outfile='task_comparison.html')

# Add scatter plot report step.
def addScatterPlot(attrib, algorithm, compare=alg_names[0]):
	filename = 'scatter-' + attrib + '-' + algorithm
	if compare != alg_names[0]:
		filename = filename + '-' + compare
	exp.add_report(
		RelativeScatterPlotReport(attributes=[attrib], filter_algorithm=[compare, algorithm],
			xlim_left = 1e-1, ylim_bottom = 1e-4, ylim_top = 1e4, tick_size=14, label_size=20, title_size=24),
		outfile=filename + '.png')

for alg in alg_names[1:]:
	addScatterPlot("expansions_until_last_jump", alg)
for spl in splitters[1:]:
	for smpl in samplers[1:]:
		addScatterPlot("expansions_until_last_jump", spl.lower() + "-" + smpl.lower(),
			spl.lower() + "-" + samplers[0].lower())

exp.add_report(BestTabularReport(10, total=True, attributes=["coverage"]), outfile="best_coverage.tex")

# Parse the commandline and show or run experiment steps.
exp.run_steps()
