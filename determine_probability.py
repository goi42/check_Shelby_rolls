import logging
import math

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import mplhep as hep
import pandas as pd
from uncertainties import ufloat
import uproot


def _adjust_stats(df):
    def _adjust(row, additions=(2, 2, 2, 1)):
        col_vals = row.values.tolist()
        for a in sorted(additions, reverse=True):
            lowest_index = col_vals.index(min(col_vals))
            col_vals[lowest_index] += a
        return col_vals

    out = pd.DataFrame(columns=df.columns)
    out[out.columns] = df.apply(_adjust, axis=1, result_type="expand")
    return out


def _lowest(row):
    assert all(x == int(x) for x in row.values), row.values
    return int(min(row))


def _efficiency(r: "int", N: "int"):
    variance = N / (N - 1) * N * r / N * (1 - r / N)
    return ufloat(r / N, math.sqrt(variance) / N)


def calculate_probabilities(df):
    style = hep.style.LHCb2
    hep.style.use(style)

    # adjust df
    df = _adjust_stats(df)
    df["lowest"] = df.apply(_lowest, axis=1, result_type="expand")
    # calculate probabilities
    N = len(df)
    at_least = {}
    for lowest_value in range(1, 20):
        n = len(df[df["lowest"] >= lowest_value])
        prob = _efficiency(n, N)
        at_least[lowest_value] = prob
    # draw
    with PdfPages("probabilities.pdf") as pdf:
        fig, ax = plt.subplots()
        bin_edges = [x - 0.5 for x in at_least.keys()] + [max(at_least.keys()) + 0.5]
        hep.histplot(
            [x.n for x in at_least.values()],
            bin_edges,
            xerr=True,
            yerr=[x.s for x in at_least.values()],
            ax=ax,
            histtype="errorbar",
        )
        ax.set_yscale("log")
        ax.set_xlabel("Lowest value")
        ax.set_ylabel("Probability")
        ax.set_title("Probability of lowest stat being at least X")
        pdf.savefig(fig)
        plt.close(fig)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # df = uproot.open("stats.root")["stats"].pandas.df()
    with uproot.open("stats_new.root:stats") as tree:
        df = tree.arrays(library="pd")
    calculate_probabilities(df)