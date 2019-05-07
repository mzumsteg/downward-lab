# -*- coding: utf-8 -*-

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
        for run in self.props.values():
            val = run.get(self.attribute)
            if val is not None and val >= dmin and val <= dmax:
                # secure against FP-issues near dmax
                bins[min(int(self.count * (val - dmin) / delta), self.count - 1)] += 1
        bars = ["value,count"]
        for i, cnt in enumerate(bins):
            bars.append("{},{}".format(dmin + delta * i / self.count, cnt))
        bars.append("{},{}".format(dmax, 0))
        return "\n".join(bars)
