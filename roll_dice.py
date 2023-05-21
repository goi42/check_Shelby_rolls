"""Roll up some D&D stats."""
import argparse
import logging
import random

import pandas as pd
import uproot


def roll_die():
    """Roll a 6-sided die."""
    return random.randint(1, 6)


def roll_dice(n):
    """Roll n 6-sided dice."""
    rolls = []
    for i in range(n):
        rolls.append(roll_die())
    return rolls


def _4d6kh3():
    """Drop lowest roll from 4d6."""
    rolls = roll_dice(4)
    rolls.sort()
    return rolls[1:]


def _stats():
    """Roll standard stats (6 4d6, drop lowest)."""
    stats = []
    for _ in range(6):
        stats.append(sum(_4d6kh3()))
    return stats


def main(out, N):
    """Generate N sets of stats."""
    logging.info(f"Generating {N} sets of stats")
    df = pd.DataFrame(columns=["STR", "DEX", "CON", "INT", "WIS", "CHA"])
    for i in range(N):
        if i % 1000 == 0:
            logging.info(f"Generating set {i}")
        df.loc[i] = _stats()

    logging.info(f"Writing stats to {out}")
    with uproot.recreate(out) as f:
        f["stats"] = df


if __name__ == "__main__":
    argparse = argparse.ArgumentParser()
    argparse.add_argument("N", type=int, help="Number of sets of stats to generate")
    argparse.add_argument("out", type=str, help="Output ROOT file")
    args = argparse.parse_args()

    logging.basicConfig(level=logging.INFO)
    main(args.out, args.N)
