# -*- coding: utf-8 -*-
from __future__ import division

from collections import defaultdict
from math import sqrt

from downward.reports import PlanningReport

class OptimalStrategyEvaluator:
    OUTPUT_FORMATS = "tex txt".split()
    """
    Creates a table listing how often a strategy is optimal for each group.
    """
    def __init__(self, optimum_bound=0, quantile=0.1):
        self.optimum_bound = optimum_bound
        self.quantile = quantile
    
    def setReport(self, report):
        self.report = report
        if report.output_format not in self.OUTPUT_FORMATS:
            raise ValueError('invalid format: {}'.format(report.output_format))
        if len(report.attributes) != 1:
            raise ValueError("Evaluator needs exactly one attribute")
        self.attribute = report.attributes[0]
    
    def _get_optimal(self, values):
        # want (val - min(*values)) / max(*values) <= self.optimum_bound
        required = min(*values) + self.optimum_bound * max(*values)
        return tuple((1 if v <= required else 0) for v in values)
    
    def _format_cell(self, cell):
        if cell != 0:
            if cell > 1 - self.quantile or cell < self.quantile:
                return r"\textcolor{{green!{1}!blue}}{{{0:.4f}}}".format(cell, int(100 * cell))
            else:
                return "{:.4f}".format(cell)
        else:
            return r"\textbf{0}"
    
    def _format_tex(self, groups):
        if len(groups) > 0:
            lines = []
            lines.append(r"\begin{center}\begin{tabular}{@{}l" + "|c" * len(self.report.algorithm_names) + "@{}}")
            # emit header
            line = [""]
            for alg in self.report.algorithm_names:
                line.append(r"\textbf{%s}" % alg.replace("_", r"{\_}"))
            lines.append(" & ".join(line) + r"\\")
            # emit domain info
            lines.append(r"\midrule")
            for group, problems in groups.items():
                optimals = []
                for problem, algorithms in problems.items():
                    optimals.append(self._get_optimal(list(map(lambda run: run[self.attribute], algorithms))))
                optimals = [sum(x) / len(x) for x in zip(*optimals)]
                line = [self._format_cell(x) for x in optimals]
                lines.append(" & ".join(["{} ({})".format(group, len(problems))] + line) + r"\\")
            # emit totals
            lines.append(r"\midrule")
            optimals = []
            for group, problems in groups.items():
                for problem, algorithms in problems.items():
                    optimals.append(self._get_optimal(list(map(lambda run: run[self.attribute], algorithms))))
            optimals = [sum(x) / len(x) for x in zip(*optimals)]
            line = [self._format_cell(x) for x in optimals]
            lines.append(" & ".join(["Total ({})".format(sum(map(len, groups.values())))] + line))
            lines.append(r"\end{tabular}\end{center}")
            return "\n".join(lines)
        else:
            return r"\textbf{NO DATA}"
    
    def _format_txt(self, groups):
        lines = [",".join(["domain", "count"] + self.report.algorithm_names)]
        if len(groups) > 0:
            for group, problems in groups.items():
                optimals = []
                for problem, algorithms in problems.items():
                    optimals.append(self._get_optimal(list(map(lambda run: run[self.attribute], algorithms))))
                line = ["{:.7f}".format(sum(x) / len(x)) for x in zip(*optimals)]
                lines.append(",".join([group, str(len(problems))] + line))
            optimals = []
            for group, problems in groups.items():
                for problem, algorithms in problems.items():
                    optimals.append(self._get_optimal(list(map(lambda run: run[self.attribute], algorithms))))
            line = ["{:.7f}".format(sum(x) / len(x)) for x in zip(*optimals)]
            lines.append(",".join(["_total", str(sum(map(len, groups.values())))] + line))
        return "\n".join(lines)
    
    def format(self, groups):
        return getattr(self, "_format_" + self.report.output_format)(groups)

class DomainStatisticsEvaluator:
    TEX_CELL_PATTERN = r"$\mathbb{{V}} = \left[{}, {}\right];\; \mu = {:.1f};\; \sigma = {:.2f}$"
    TXT_CELL_PATTERN = "{},{},{:.3f},{:.5f}"
    OUTPUT_FORMATS = "tex txt".split()
    """
    Creates a table listing statistical attributes of each domain
    (generated over it's problems).
    """
    def __init__(self):
        pass
    
    def setReport(self, report):
        self.report = report
        if report.output_format not in self.OUTPUT_FORMATS:
            raise ValueError('invalid format: {}'.format(report.output_format))
        # the planner is never run without an algorithm,
        # so to avoid duplicate data we have to pick one still
        if len(report.algorithm_names) != 1:
            raise ValueError("Evaluator needs exactly one algorithm")
    
    def _format_tex(self, groups):
        if len(groups) > 0:
            lines = []
            lines.append(r"\begin{center}\begin{tabular}{@{}l" + "|c" * len(self.report.attributes) + "@{}}")
            line = [""]
            for attrib in self.report.attributes:
                line.append(r"\textbf{%s}" % attrib.replace("_", r"{\_}"))
            lines.append(" & ".join(line) + r"\\")
            lines.append(r"\midrule")
            for group, problems in groups.items():
                line = ["{} ({})".format(group, len(problems))]
                for attrib in self.report.attributes:
                    values = list(map(lambda run: run[0][attrib], problems.values()))
                    lower, upper, mean = min(values), max(values), sum(values) / len(values)
                    stddev = sqrt(sum(map(lambda x: (x - mean)**2, values)) / (len(values) - 1))
                    line.append(self.TEX_CELL_PATTERN.format(lower, upper, mean, stddev))
                lines.append(" & ".join(line) + r"\\")
            # emit totals
            lines.append(r"\midrule")
            line = ["Total ({})".format(sum(map(len, groups.values())))]
            for attrib in self.report.attributes:
                values = []
                for group, problems in groups.items():
                    values += list(map(lambda run: run[0][attrib], problems.values()))
                    lower, upper, mean = min(values), max(values), sum(values) / len(values)
                    stddev = sqrt(sum(map(lambda x: (x - mean)**2, values)) / (len(values) - 1))
                line.append(self.TEX_CELL_PATTERN.format(lower, upper, len(values), mean, stddev))
            lines.append(" & ".join(line))
            lines.append(r"\end{tabular}\end{center}")
            return "\n".join(lines)
        else:
            return r"\textbf{NO DATA}"
    
    def _format_txt(self, groups):
        lines = []
        line = ["domain", "count"]
        for attrib in self.report.attributes:
            line.append("min_" + attrib)
            line.append("max_" + attrib)
            line.append("mean_" + attrib)
            line.append("std_" + attrib)
        lines.append(",".join(line))
        if len(groups) > 0:
            for group, problems in groups.items():
                line = [group, str(len(problems))]
                for attrib in self.report.attributes:
                    values = list(map(lambda run: run[0][attrib], problems.values()))
                    lower, upper, mean = min(values), max(values), sum(values) / len(values)
                    stddev = sqrt(sum(map(lambda x: (x - mean)**2, values)) / (len(values) - 1))
                    line.append(self.TXT_CELL_PATTERN.format(lower, upper, mean, stddev))
                lines.append(",".join(line))
            line = ["_total", str(sum(map(len, groups.values())))]
            for attrib in self.report.attributes:
                values = []
                for group, problems in groups.items():
                    values += list(map(lambda run: run[0][attrib], problems.values()))
                    lower, upper, mean = min(values), max(values), sum(values) / len(values)
                    stddev = sqrt(sum(map(lambda x: (x - mean)**2, values)) / (len(values) - 1))
                line.append(self.TXT_CELL_PATTERN.format(lower, upper, len(values), mean, stddev))
            lines.append(",".join(line))
        return "\n".join(lines)
    
    def format(self, groups):
        return getattr(self, "_format_" + self.report.output_format)(groups)

class IdealProblemsEvaluator:
    OUTPUT_FORMATS = "txt".split()
    """
    Creates a table listing statistical attributes of each domain
    (generated over it's problems).
    """
    def __init__(self, eval_attribute):
        self.eval_attribute = eval_attribute
        self.min_wins = getattr(eval_attribute, "min_wins", True)
    
    def setReport(self, report):
        self.report = report
        if report.output_format not in self.OUTPUT_FORMATS:
            raise ValueError('invalid format: {}'.format(report.output_format))
    
    def _format_txt(self, groups):
        lines = []
        lines.append(",".join(["domain", "problem", "ideal"] + self.report.attributes))
        if len(groups) > 0:
            for group, problems in groups.items():
                for problem, algorithms in problems.items():
                    perf = zip(map(lambda run: run[self.eval_attribute], algorithms), self.report.algorithm_names)
                    ideal = min(perf)[1] if self.min_wins else max(perf)[1]
                    attributes = list(map(lambda attrib: str(algorithms[0][attrib]), self.report.attributes))
                    lines.append(",".join([group, problem, ideal] + attributes))
        return "\n".join(lines)
    
    def format(self, groups):
        return getattr(self, "_format_" + self.report.output_format)(groups)

class DomainComparisonReport(PlanningReport):
    """
    Creates a TeX file determining how often an algorithm
    is optimal with respect to a given attribute.
    """
    def __init__(self, algorithms, evaluator, min_group_size=1, **kwargs):
        PlanningReport.__init__(self, **kwargs)
        if len(algorithms) < 1:
            raise ValueError("Report needs at least one algorithm")
        if len(set(algorithms)) != len(algorithms):
            raise ValueError("Algorithms may not appear multiple times")
        self.algorithm_names = algorithms
        self.algorithm_idx = {alg: i for i, alg in enumerate(algorithms)}
        self.evaluator = evaluator
        # values less than one imply no bound
        self.min_group_size = min_group_size
        evaluator.setReport(self)
    
    def _is_run_valid(self, run):
        valid = run["algorithm"] in self.algorithm_idx
        valid = valid and all(map(lambda attrib: attrib in run, self.attributes))
        return valid
    
    def get_text(self):
        return self.get_markup()
    
    def get_markup(self):
        # gather runs indexed by group, problem into a list of algorithms
        groups = defaultdict(lambda: defaultdict(lambda: [None] * len(self.algorithm_names)))
        for run in self.props.values():
            if self._is_run_valid(run):
                groups[run["domain"]][run["problem"]][self.algorithm_idx[run["algorithm"]]] = run
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
