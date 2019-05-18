# -*- coding: utf-8 -*-

from collections import defaultdict

from downward.reports import PlanningReport

class HistogramReport(PlanningReport):
    """
    Creates a CSV containing a histogram of a specific attribute.
    This file can then be used via PGFPlots to create an image.
    """
    def __init__(self, count=100, min=None, max=None, **kwargs):
        if "format" not in kwargs:
            kwargs["format"] = "txt"
        elif kwargs["format"] != "txt":
            raise ValueError("unsupported format: {}".format(kwargs["format"]))
        if min is not None and max is not None and min >= max:
            raise ValueError("min must be below max: {} >= {}".format(min, max))
        PlanningReport.__init__(self, **kwargs)
        self.attributes = kwargs["attributes"]
        if len(self.attributes) != 1:
            raise ValueError("Report needs exactly one attribute")
        self.attribute = self.attributes[0]
        self.count = int(count)
        self.min = min
        self.max = max
    
    def get_text(self):
        return self.get_markup()
    
    def get_markup(self):
        if self.min is None or self.max is None:
            any = False
            dmin, dmax = float("inf"), float("-inf")
            for run in self.props.values():
                val = run.get(self.attribute)
                if val is not None:
                    any = True
                    dmin, dmax = min(dmin, val), max(dmax, val)
            if not any: raise Error("no data")
            if self.min is not None: dmin = self.min
            if self.max is not None: dmax = self.max
        else:
            dmin, dmax = self.min, self.max
        delta = dmax - dmin
        bins = [0] * self.count
        domains, domainMap = [], {}
        domainBins = []
        for run in self.props.values():
            val = run.get(self.attribute)
            # ensure every domain exists, even if it provides no data
            domain = run["domain"]
            if domain not in domainMap:
                domainMap[domain] = len(domains)
                domains.append(domain)
                domainBins.append([0] * self.count)
            if val is not None and val >= dmin and val <= dmax:
                # secure against FP-issues near dmax
                binIdx = min(int(self.count * (val - dmin) / delta), self.count - 1)
                bins[binIdx] += 1
                domainBins[domainMap[domain]][binIdx] += 1
        bars = ["value,count," + ",".join(domains)]
        binDomains = list(zip(*domainBins)) # index by bin
        for i, cnt in enumerate(bins):
            bars.append("{},{},".format(dmin + delta * i / self.count, cnt) + ",".join(map(str, binDomains[i])))
        bars.append("{},{}".format(dmax, 0) + ",0" * len(domains))
        return "\n".join(bars)
