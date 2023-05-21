"""Roll up some D&D stats."""
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
    rolls = roll_dice(4)
    rolls.sort()
    return rolls[1:]


def _stats():
    stats = []
    for i in range(6):
        stats.append(sum(_4d6kh3()))
    return stats


def main(N):
    """Generate N sets of stats."""
    logging.info(f"Generating {N} sets of stats")
    df = pd.DataFrame(columns=["STR", "DEX", "CON", "INT", "WIS", "CHA"])
    for i in range(N):
        if i % 1000 == 0:
            logging.info(f"Generating set {i}")
        df.loc[i] = _stats()

    logging.info("Writing stats to stats.root")
    with uproot.recreate("stats_new.root") as f:
        f["stats"] = df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main(100_000)
