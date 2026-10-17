"""Mock task feed for the demo. Every number here is illustrative."""
from __future__ import annotations

import random

from .core import Task

TICKERS = ["INKY", "REEF", "TIDE", "BLOOP", "KRILL", "SQUID", "GLONK", "BLORP", "FROGGO", "KRAKEN"]
TAGS = ["octo summer", "AI agents x memes", "desk bots", "sea season", "zero click"]
ACCOUNTS = ["whale", "degen_daily", "solana_sam", "ct_alpha"]


def _price_path(entry: float) -> list[float]:
    p, path = entry, []
    for _ in range(60):
        p *= random.uniform(0.86, 1.22)
        path.append(p)
    return path


def random_task() -> Task:
    kind = random.choice(["trend", "launch", "launch", "dev_watch", "exits", "clip", "draft", "reply", "report"])
    t = random.choice(TICKERS)
    if kind == "trend":
        return Task(kind, {"tag": random.choice(TAGS), "growth": random.randint(80, 420)})
    if kind == "launch":
        return Task(kind, {"ticker": t, "bundle_pct": random.uniform(0.02, 0.45),
                           "dev_hold": random.uniform(0.0, 0.12), "win_rate": random.uniform(0.3, 0.55),
                           "payoff": random.uniform(3, 9)})
    if kind == "dev_watch":
        return Task(kind, {"ticker": t, "dev_sold": random.choice([0, 0, 0, random.uniform(0.01, 0.05)])})
    if kind == "exits":
        return Task(kind, {"ticker": t, "entry": 7.0, "prices": _price_path(7.0)})
    if kind == "clip":
        return Task(kind, {"minutes": random.randint(40, 180), "clips": random.randint(3, 8)})
    if kind == "draft":
        return Task(kind, {"what": random.choice(["hook", "thread 7/7", "launch post", "3 hook variants"])})
    if kind == "reply":
        return Task(kind, {"account": random.choice(ACCOUNTS), "secs": random.randint(30, 90)})
    return Task(kind, {"pnl": f"+${random.randint(2, 15)},{random.randint(100, 999)} today"})
