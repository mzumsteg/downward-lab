# -*- coding: utf-8 -*-

from __future__ import division

from collections import defaultdict

from downward.reports import PlanningReport

class OptimalStrategyEvaluator:
    """
    Creates a table listing how often a strategy is optimal for each group.
    """
    def __init__(self, optimum_bound=0, quantile=0.1):
        self.optimum_bound = optimum_bound
        self.quantile = quantile
    
    def setReport(self, report):
        self.report = report
        if len(report.attributes) != 1:
            raise ValueError("Evaluator needs exactly one attribute")
        self.attribute = report.attributes[0]
    
    def _get_optimal(self, values):
        # want (val - min(*values)) / max(*values) <= self.optimum_bound
        required = min(*values) + self.optimum_bound * max(*values)
        return tuple((1 if v <= required else 0) for v in values)
    
    def format(self, groups):
        if len(groups) > 0:
            lines = []
            lines.append(r"\begin{center}\begin{tabular}{@{}l" + "|c" * len(self.report.algorithms) + "@{}}")
            # emit header
            line = [""]
            for alg in self.report.algorithms:
                line.append(r"\textbf{%s}" % alg.replace("_", r"{\_}"))
            lines.append(" & ".join(line) + r"\\")
            # emit domain info
            lines.append(r"\midrule")
            for group, problems in groups.items():
                optimals = []
                for problem, algorithms in problems.items():
                    optimals.append(self._get_optimal(list(map(lambda run: run[self.attribute], algorithms))))
                optimals = [sum(x) / len(x) for x in zip(*optimals)]
                line = [("{:.4f}".format(x) if x != 0 else r"\textbf{0}") for x in optimals]
                lines.append(" & ".join([group] + line) + r"\\")
            # emit totals
            lines.append(r"\midrule")
            optimals = []
            for group, problems in groups.items():
                for problem, algorithms in problems.items():
                    optimals.append(self._get_optimal(list(map(lambda run: run[self.attribute], algorithms))))
            optimals = [sum(x) / len(x) for x in zip(*optimals)]
            line = [("{:.4f}".format(x) if x != 0 else r"\textbf{0}") for x in optimals]
            lines.append(" & ".join(["Total"] + line))
            lines.append(r"\end{tabular}\end{center}")
            return "\n".join(lines)
        else:
            return "\\textbf{NO DATA}"

class DomainComparisonReport(PlanningReport):
    """
    Creates a TeX file determining how often an algorithm
    is optimal with respect to a given attribute.
    """
    def __init__(self, algorithms, evaluator, min_group_size=10, **kwargs):
        PlanningReport.__init__(self, **kwargs)
        if len(algorithms) < 1:
            raise ValueError("Report needs at least one algorithm")
        if len(set(algorithms)) != len(algorithms):
            raise ValueError("'algorithms' may not contain duplicates")
        self.algorithms = algorithms
        self.algorithm_idx = {alg: i for i, alg in enumerate(algorithms)}
        self.evaluator = evaluator
        # values less than two imply no bound
        self.min_group_size = min_group_size
        evaluator.setReport(self)
    
    def get_text(self):
        return self.get_markup()
    
    def get_markup(self):
        # gather runs indexed by group, problem into a list of algorithms
        groups = defaultdict(lambda: defaultdict(lambda: [None] * len(self.algorithms)))
        for run in self.props.values():
            if run["algorithm"] in self.algorithm_idx:
                groups[run["domain"]][run["problem"]][algorithm_idx[run["algorithm"]]] = run
        # remove problems which aren't solved by all algorithms
        for group, problems in groups.items():
            for problem, algorithms in list(problems.items()):
                if not all(algorithms):
                    del problems[problem]
        # remove domains which don't meet the min_group_size
        for group, problems in list(groups.items()):
            if len(problems) < self.min_group_size:
                del groups[group]
        # call evaluator to sample data of interest
        return self.evaluator.format(groups)
