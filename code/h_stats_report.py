# -*- coding: utf-8 -*-
from __future__ import division

from collections import defaultdict

from downward.reports import PlanningReport

class HeuristicStatisticsReport(PlanningReport):
    """
    Creates a CSV with the best/worst (according to eval_attrib) h_split_statistics values.
    """
    def __init__(self, algorithm, n_best=1, n_worst=0, eval_attrib="expansions_until_last_jump", **kwargs):
        if "format" not in kwargs:
            kwargs["format"] = "txt"
        elif kwargs["format"] != "txt":
            raise ValueError("unsupported format: {}".format(kwargs["format"]))
        kwargs["attributes"] = ["h_split_statistics"]
        PlanningReport.__init__(self, **kwargs)
        self.attribute = self.attributes[0]
        self.algorithm = algorithm
        if n_best <= 0 and n_worst <= 0:
            raise ValueError("Report must select at least one run")
        self.n_best = n_best
        self.n_worst = n_worst
        self.eval_attrib = eval_attrib
        self.min_wins = getattr(eval_attrib, "min_wins", True)
    
    def get_text(self):
        return self.get_markup()
    
    def get_markup(self):
        candidates = []
        for runs in self.problem_runs.values():
            target = next((r for r in runs if r["algorithm"] == self.algorithm), None)
            if target is not None and self.eval_attrib in target and bool(target[self.attribute]):
                min_val = min(r[self.eval_attrib] for r in runs if self.eval_attrib in r)
                max_val = max(r[self.eval_attrib] for r in runs if self.eval_attrib in r)
                value = target[self.eval_attrib]
                if min_val < max_val:
                    value = (value - min_val if self.min_wins else max_val - value) / (max_val - min_val)
                else:
                    value = 0.5 # prefer samples where the selection matters
                candidates.append((value, target))
        if not candidates:
            return "No suitable candidates"
        candidates.sort()
        header, picks = ["N"], []
        used_domains = set()
        
        header += ["best_" + str(x + 1) for x in range(self.n_best)]
        for i in range(self.n_best):
            values = filter(lambda v: v[1]["domain"] not in used_domains, candidates)
            if not values:
                return "Not enough candidates"
            pick = values[0][1]
            used_domains.add(pick["domain"])
            picks.append(pick)
        
        header += ["worst_" + str(x + 1) for x in range(self.n_worst)]
        for i in range(self.n_worst):
            values = filter(lambda v: v[1]["domain"] not in used_domains, candidates)
            if not values:
                return "Not enough candidates"
            pick = values[-1][1]
            used_domains.add(pick["domain"])
            picks.append(pick)
        
        for i, pick in enumerate(picks):
            print(pick["id"])
            picks[i] = {s[0]: s[1] for s in pick["h_split_statistics"]}
        lines = [",".join(header)]
        for mark in sorted(set(sum((pick.keys() for pick in picks), []))):
            lines.append(",".join([str(mark)] + [(str(abs(pick[mark])) if mark in pick else "") for pick in picks]))
        return "\n".join(lines)
