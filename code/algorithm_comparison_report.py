# -*- coding: utf-8 -*-

from collections import defaultdict
from os import linesep

from downward.reports import PlanningReport

"""
Comparison map format:
    left_alg and right_alg: algorithms to compare
    min_improvement, quantile: replace parameter if present
"""
def _make_comparison_map(comp):
    if isinstance(comp, dict):
        if not "left_alg" in comp:
            raise ValueError("Comparison has no first algorithm")
        if not "right_alg" in comp:
            raise ValueError("Comparison has no second algorithm")
        if comp["left_alg"] == comp["right_alg"]:
            raise ValueError("Cannot compare algorithm to itself")
        return comp
    else:
        # accept a tuple of algorithm names
        if comp[0] == comp[1]:
            raise ValueError("Cannot compare algorithm to itself")
        result = {"left_alg": comp[0], "right_alg": comp[1]}
        return result

class AlgorithmComparisonReport(PlanningReport):
    """
    Creates a TeX file comparing a number of algorithm pairs.
    """
    def __init__(self, comparison, min_improvement=0, quantile=0.5, **kwargs):
        kwargs["format"] = "tex"
        PlanningReport.__init__(self, **kwargs)
        if len(self.attributes) != 1:
            raise ValueError("Report needs exactly one attribute")
        if len(comparison) == 0:
            raise ValueError("Report needs at least one comparison")
        self.comparison = {id(comp): comp for comp in map(_make_comparison_map, comparison)}
        self.attribute = self.attributes[0]
        self.min_improvement = min_improvement
        self.quantile = quantile
    
    def _format_row(self, name, row):
        line = [r"\textbf{%s}" % name.replace("_", r"{\_}")]
        for (iComp, curr) in row.items():
            if curr[2] > 0:
                comp = self.comparison[iComp]
                line.append(r"\textbf{0}" if curr[0] == 0 else str(curr[0]))
                line.append(r"\textbf{0}" if curr[1] == 0 else str(curr[1]))
                quantile = comp.get("quantile", self.quantile)
                left_win = curr[0] / curr[2]
                right_win = curr[1] / curr[2]
                if quantile < 0.5:
                    left = "{0:.2f}".format(left_win)
                    right = "{0:.2f}".format(right_win)
                    if left_win > 1 - quantile:
                        left = r"\textcolor{{green!{1}!blue}}{{{0}}}".format(left, int(100 * left_win))
                    if right_win > 1 - quantile:
                        right = r"\textcolor{{green!{1}!blue}}{{{0}}}".format(right, int(100 * right_win))
                    line.append("%s %s" % (left, right))
                else:
                    line.append("{0:.2f} {0:.2f}".format(left_win, right_win))
            else:
                # no data => no output
                line.append("")
                line.append("")
                line.append("")
        return " & ".join(line)
    
    def get_text(self):
        return self.get_markup()
    
    def get_markup(self):
        # cannot use Table() because we have duplicate columns (by name, not their contents)
        results = defaultdict(dict)
        for domain in self.domains:
            for comp in self.comparison.values():
                curr = [0, 0, 0]
                min_improvement = comp.get("min_improvement", self.min_improvement)
                other_runs = self.domain_algorithm_runs[(domain, comp["right_alg"])]
                other_runs = {run["problem"]: run for run in other_runs if self.attribute in run}
                for run in self.domain_algorithm_runs[(domain, comp["left_alg"])]:
                    if self.attribute in run and run["problem"] in other_runs:
                        left_val, right_val = run[self.attribute], other_runs[run["problem"]][self.attribute]
                        curr[2] += 1
                        if left_val != right_val:
                            improvement = (left_val - right_val) / max(left_val, right_val)
                            if improvement > min_improvement:
                                curr[0] += 1
                            if -improvement > min_improvement:
                                curr[1] += 1
                results[domain][id(comp)] = curr
        # aggregate over all domains
        total = {id(comp): tuple(sum(x) for x in zip(*(row[id(comp)] for row in results.values())))
            for comp in self.comparison.values()}
        
        # generate output
        lines = []
        lines.append(r"\begin{center}\begin{tabular}{@{}l" + "ccc" * len(self.comparison) + "@{}}")
        # emit header
        line = [""]
        for comp in self.comparison.values():
            line.append(r"\textbf{%s}" % comp["left_alg"].replace("_", r"{\_}"))
            line.append(r"\textbf{%s}" % comp["right_alg"].replace("_", r"{\_}"))
            line.append(r"\textbf{win balance}")
        lines.append(" & ".join(line) + r"\\")
        # emit by-domain info
        lines.append(r"\midrule")
        for (domain, row) in results.items():
            if any(map(lambda curr: curr[2] > 0, row.values())):
                lines.append(self._format_row(domain, row) + r"\\")
        # emit totals
        lines.append(r"\midrule")
        lines.append(self._format_row("Total", total))
        lines.append(r"\end{tabular}\end{center}")
        return linesep.join(lines)
