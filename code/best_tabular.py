# -*- coding: utf-8 -*-

from collections import defaultdict

from downward.reports import PlanningReport

class BestTabularReport(PlanningReport):
    """
    Creates a CSV containing a histogram of a specific attribute.
    This file can then be used via PGFPlots to create an image.
    """
    def __init__(self, nbest=5, total=False, **kwargs):
        if "format" not in kwargs:
            kwargs["format"] = "tex"
        elif kwargs["format"] != "tex":
            raise ValueError("unsupported format: {}".format(kwargs["format"]))
        PlanningReport.__init__(self, **kwargs)
        if len(self.attributes) != 1:
            raise ValueError("Report needs exactly one attribute")
        self.attribute = self.attributes[0]
        self.nbest = nbest
        self.total = total
    
    def get_text(self):
        return self.get_markup()
    
    def get_markup(self):
        lines = []
        algorithms = list(self.algorithms)
        # generate header
        lines.append(r"\begin{tabular}{@{}l|" + 'c' * len(algorithms) + "@{}}")
        line = ["Domain"] + algorithms
        lines.append(" & ".join(line) + r"\\")
        lines.append(r"\midrule")
        # generate content
        domains = {}
        for domain in self.domains:
            getattr = lambda algo: sum(item[self.attribute] for item in self.domain_algorithm_runs[domain, algo])
            domains[domain] = [getattr(algo) for algo in algorithms]
        sortfunc = lambda x: -sum(x[1]) / float(len(self.domains[x[0]]))
        domains = sorted(domains.items(), key=sortfunc)
        for i in range(min(self.nbest, len(domains))):
            domain, values = domains[i]
            line = [r"\textbf{{{}}} ({})".format(domain, len(self.domains[domain]))] + [str(val) for val in values]
            lines.append(" & ".join(line) + r"\\")
        # generate total (if enabled)
        if self.total:
            totals = [sum(values[i] for domain, values in domains) for i in range(len(self.algorithms))]
            line = [r"\textbf{Total}"] + [str(val) for val in totals]
            lines.append(" & ".join(line) + r"\\")
        if lines[-1].endswith(r"\\"):
            lines[-1] = lines[-1][:-2]
        lines.append(r"\end{tabular}")
        return "\n".join(lines)
