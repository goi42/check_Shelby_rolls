import argparse
import logging
import math

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import mplhep as hep
import pandas as pd
from uncertainties import ufloat
import uproot


def _adjust_stats(df):
    """Add 2 ability score improvements to one human.

    Assigns the asi to the lowest stats in turn.
    Does not divide the ability score improvements between stats.
    """

    def _adjust(row, asi=(2, 2)):
        col_vals = row.values.tolist()
        # human
        for i in range(len(col_vals)):
            col_vals[i] += 1
        # asi
        for a in asi:
            lowest_index = col_vals.index(min(col_vals))
            col_vals[lowest_index] += a
        return col_vals

    out = pd.DataFrame(columns=df.columns)
    out[out.columns] = df.apply(_adjust, axis=1, result_type="expand")
    out["lowest"] = out.apply(_lowest, axis=1, result_type="expand")
    return out


def _lowest(row):
    assert all(x == int(x) for x in row.values), row.values
    return int(min(row))


def _efficiency(r: "int", N: "int"):
    variance = N / (N - 1) * N * r / N * (1 - r / N)
    return ufloat(r / N, math.sqrt(variance) / N)


def calculate_probabilities(out, df):
    style = hep.style.LHCb2
    hep.style.use(style)

    # adjust df
    df = _adjust_stats(df)
    # calculate probabilities
    N = len(df)
    at_least = {}
    for lowest_value in range(1, 20):
        n = len(df[df["lowest"] >= lowest_value])
        prob = _efficiency(n, N)
        at_least[lowest_value] = prob
    # draw
    with PdfPages(out) as pdf:
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
        # vertical line at 18
        ax.axvline(18, color="red", linestyle="--")
        ax.set_xlabel("Stat value")
        ax.set_ylabel("Probability")
        ax.set_title(
            f"Probability of all stats being at least ({N:,} sets of stats rolled)"
        )
        pdf.savefig(fig)
        plt.close(fig)
    # print
    print("Probability of all stats being at least:")
    for lowest_value, prob in at_least.items():
        print(f"{lowest_value}: {prob:%}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="stats file")
    parser.add_argument("out", help="output file")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    # df = uproot.open("stats.root")["stats"].pandas.df()
    with uproot.open(f"{args.file}:stats") as tree:
        df = tree.arrays(library="pd")
    calculate_probabilities(args.out, df)
