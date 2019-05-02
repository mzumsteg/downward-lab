# -*- coding: utf-8 -*-

from collections import defaultdict

from matplotlib import ticker

from downward.reports.scatter import ScatterPlotReport
from downward.reports.plot import PlotReport, Matplotlib, MatplotlibPlot, PgfPlots


# TODO: handle outliers

# TODO: this is mostly copied from ScatterMatplotlib (scatter.py)
class RelativeScatterMatplotlib(Matplotlib):
    @classmethod
    def _plot(cls, report, axes, categories, styles):
        # Display grid
        axes.grid(b=True, linestyle='-', color='0.75')

        has_points = False
        # Generate the scatter plots
        for category, coords in sorted(categories.items()):
            X, Y = zip(*coords)
            axes.scatter(X, Y, s=42, label=category, **styles[category])
            if X and Y:
                has_points = True

        if report.xscale == 'linear' or report.yscale == 'linear':
            plot_size = report.missing_val * 1.01
        else:
            plot_size = report.missing_val * 1.25

        """
        # make 5 ticks above and below 1
        yticks = []
        tick_step = report.ylim_top**(1/5.0)
        for i in xrange(-5, 6):
            yticks.append(tick_step**i)
        axes.set_yticks(yticks)
        axes.get_yaxis().set_major_formatter(ticker.ScalarFormatter())
        """
        # use built-in log scale so all ticks are readable
        axes.set_yscale("log")

        axes.set_xlim(report.xlim_left or -1, report.xlim_right or plot_size)
        axes.set_ylim(report.ylim_bottom or -1, report.ylim_top or plot_size)

        for axis in [axes.xaxis, axes.yaxis]:
            MatplotlibPlot.change_axis_formatter(
                axis,
                report.missing_val if report.show_missing else None)
        return has_points


class RelativeScatterPgfPlots(PgfPlots):
    @classmethod
    def _format_coord(cls, coord):
        def format_value(v):
            return str(v) if isinstance(v, int) else '%f' % v
        return '(%s, %s)' % (format_value(coord[0]), format_value(coord[1]))

    @classmethod
    def _get_plot(cls, report):
        lines = []
        options = cls._get_axis_options(report)
        lines.append('\\begin{axis}[%s]' % cls._format_options(options))
        for category, coords in sorted(report.categories.items()):
            plot = {'only marks': True}
            lines.append(
                '\\addplot+[%s] coordinates {\n%s\n};' % (
                    cls._format_options(plot),
                    ' '.join(cls._format_coord(c) for c in coords)))
            if category:
                lines.append('\\addlegendentry{%s}' % category)
        # Add black line.
        start = min(report.min_x, report.min_y)
        if report.xlim_left is not None:
            start = min(start, report.xlim_left)
        if report.ylim_bottom is not None:
            start = min(start, report.ylim_bottom)
        end = max(report.max_x, report.max_y)
        if report.xlim_right:
            end = max(end, report.xlim_right)
        if report.ylim_top:
            end = max(end, report.ylim_top)
        if report.show_missing:
            end = max(end, report.missing_val)
        lines.append(
            '\\addplot[color=black] coordinates'
            ' {{({start}, 1) ({end}, 1)}};'.format(**locals()))
        lines.append('\\end{axis}')
        return lines

    @classmethod
    def _get_axis_options(cls, report):
        opts = PgfPlots._get_axis_options(report)
        # Add line for missing values.
        for axis in ['x', 'y']:
            opts['extra %s ticks' % axis] = report.missing_val
            opts['extra %s tick style' % axis] = 'grid=major'
        return opts


class RelativeScatterPlotReport(ScatterPlotReport):
    """
    Generate a scatter plot that shows a relative comparison of two
    algorithms with regard to the given attribute. The attribute value
    of algorithm 1 is shown on the x-axis and the relation to the value
    of algorithm 2 on the y-axis.
    """

    def __init__(self, show_missing=True, get_category=None, xlim_left = None, xlim_right = None,
            ylim_bottom = None, ylim_top = None, **kwargs):
        ScatterPlotReport.__init__(self, show_missing, get_category, **kwargs)
        self.xlim_left = xlim_left
        self.xlim_right = xlim_right
        self.ylim_bottom = ylim_bottom
        self.ylim_top = ylim_top
        if self.output_format == 'tex':
            self.writer = RelativeScatterPgfPlots
        else:
            self.writer = RelativeScatterMatplotlib

    def _fill_categories(self, runs):
        # We discard the *runs* parameter.
        # Map category names to value tuples
        categories = defaultdict(list)
        ylim_bottom = 2
        ylim_top = 0.5
        xlim_left = float("inf")
        xbetter = 0
        ybetter = 0
        for (domain, problem), runs in self.problem_runs.items():
            if len(runs) != 2:
                continue
            run1, run2 = runs
            assert (run1['algorithm'] == self.algorithms[0] and
                    run2['algorithm'] == self.algorithms[1])
            val1 = run1.get(self.attribute)
            val2 = run2.get(self.attribute)
            if val1 is None or val2 is None:
                continue
            val1 = max(val1, 0.1)
            val2 = max(val2, 0.1)
            category = self.get_category(run1, run2)
            x = val1
            y = val2 / float(val1)

            categories[category].append((x, y))

            ylim_top = max(ylim_top, y)
            ylim_bottom = min(ylim_bottom, y)
            xlim_left = min(xlim_left, x)

            if val1 > val2:
                xbetter += 1
            elif val1 < val2:
                ybetter += 1
        if not categories:
            ylim_bottom = 0.5
            ylim_top = 2
            xlim_left = 0.5

        # use guessed limits only if not fixed
        self.xlim_left = self.xlim_left or xlim_left
        self.ylim_bottom = self.ylim_bottom or ylim_bottom
        self.ylim_top = self.ylim_top or ylim_top
        # center around 1
        if self.ylim_bottom < 1:
            self.ylim_top = max(self.ylim_top, 1 / float(self.ylim_bottom))
        if self.ylim_top > 1:
            self.ylim_bottom = min(self.ylim_bottom, 1 / float(self.ylim_top))

        self.xlabel += " ({})".format(xbetter)
        self.ylabel += " ({})".format(ybetter)
        return categories

    def _set_scales(self, xscale, yscale):
        # ScatterPlot uses log-scaling on the x-axis by default.
        PlotReport._set_scales(
            self, xscale or self.attribute.scale or 'log', 'log')
