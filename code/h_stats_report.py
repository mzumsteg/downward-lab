# -*- coding: utf-8 -*-

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
        self.eval_attrib = eval_attrib
        self.min_wins = getattr(eval_attrib, "min_wins", True)
        if n_best <= 0 and n_worst <= 0:
            raise ValueError("Report must select at least one run")
        self.n_best = n_best
        self.n_worst = n_worst
    
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
        header = ["N"]
        if len(candidates) > self.n_best + self.n_worst:
            picks = []
            if self.n_best > 0:
                header += ["best_" + str(x + 1) for x in range(self.n_best)]
                picks += candidates[:self.n_best]
            if self.n_worst > 0:
                header += ["worst_" + str(x + 1) for x in range(self.n_worst)]
                picks += candidates[-self.n_worst:]
        else:
            header += ["best_" + str(x + 1) for x in range(len(candidates))]
            picks = list(candidates)
        for i, pick in enumerate(picks):
            print(pick[1]["id"])
            picks[i] = {s[0]: s[1] for s in pick[1]["h_split_statistics"]}
        lines = [",".join(header)]
        for mark in sorted(set(sum((pick.keys() for pick in picks), []))):
            lines.append(",".join([str(mark)] + [(str(pick[mark]) if mark in pick else "") for pick in picks]))
        return "\n".join(lines)
