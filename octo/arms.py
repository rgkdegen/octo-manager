"""The eight arms. Trading arms carry the real rules; content arms are simulated work."""
from __future__ import annotations

import asyncio
import random

from .core import Arm, Result, Task

# ---- rules worth stealing --------------------------------------------------

BUNDLE_MAX = 0.20     # skip if bundled wallets hold more than 20% of supply
DEV_MAX = 0.05        # skip if the dev wallet holds more than 5%
KELLY_CAP = 16        # position size is Kelly, capped at 16 units
MAX_BAG = 12          # never more than 12 of 16 units in one token
EXIT_LADDER = (3, 8, 20, 50, 100)  # sell 20% of the bag at each multiple
SELL_SLICE = 0.20
TRAIL_STOP = -0.35    # trailing stop, 35% under the running high


def passes_filter(bundle_pct: float, dev_hold: float) -> tuple[bool, str]:
    """The two-line filter. Returns (ok, reason)."""
    if bundle_pct > BUNDLE_MAX:
        return False, f"bundle {bundle_pct:.0%}"
    if dev_hold > DEV_MAX:
        return False, f"dev holding {dev_hold:.1%}"
    return True, "passed all reads"


def kelly_units(win_rate: float, payoff: float) -> int:
    """Kelly fraction mapped to 0..16 units and capped by MAX_BAG."""
    edge = win_rate - (1 - win_rate) / payoff
    units = max(0, round(edge * KELLY_CAP))
    return min(units, KELLY_CAP, MAX_BAG)


def exit_plan(prices: list[float], entry: float) -> list[tuple[str, float]]:
    """Walk a price path and return the sells: ('ladder' | 'stop', multiple)."""
    sells: list[tuple[str, float]] = []
    left, high, rung = 1.0, entry, 0
    for p in prices:
        high = max(high, p)
        mult = p / entry
        while rung < len(EXIT_LADDER) and mult >= EXIT_LADDER[rung] and left > 0:
            left -= SELL_SLICE
            sells.append(("ladder", EXIT_LADDER[rung]))
            rung += 1
        if left > 0 and p <= high * (1 + TRAIL_STOP):
            sells.append(("stop", round(mult, 2)))
            break
    return sells


# ---- arms ------------------------------------------------------------------

async def _busy(lo: float = 0.3, hi: float = 1.2) -> None:
    await asyncio.sleep(random.uniform(lo, hi))


class Scout(Arm):
    number, name, kind = "01", "Scout", "trend"

    async def work(self, task: Task) -> Result:
        await _busy()
        tag, growth = task.payload["tag"], task.payload["growth"]
        return Result(True, f'narrative "{tag}" +{growth}% mentions')


class Sniper(Arm):
    number, name, kind = "02", "Sniper", "launch"

    async def work(self, task: Task) -> Result:
        await _busy(0.2, 0.6)
        p = task.payload
        ok, why = passes_filter(p["bundle_pct"], p["dev_hold"])
        if not ok:
            return Result(True, f"${p['ticker']} skipped · {why}")
        units = kelly_units(p["win_rate"], p["payoff"])
        return Result(True, f"${p['ticker']} sized {units}/{KELLY_CAP} · entry")


class RugGuard(Arm):
    number, name, kind = "03", "Rug Guard", "dev_watch"

    async def work(self, task: Task) -> Result:
        await _busy(0.2, 0.5)
        p = task.payload
        if p["dev_sold"] > 0:
            return Result(True, f"${p['ticker']} dev moved {p['dev_sold']:.1%} → exit all")
        return Result(True, f"${p['ticker']} dev wallet quiet")


class Treasurer(Arm):
    number, name, kind = "04", "Treasurer", "exits"

    async def work(self, task: Task) -> Result:
        await _busy()
        p = task.payload
        sells = exit_plan(p["prices"], p["entry"])
        ladder = [m for k, m in sells if k == "ladder"]
        stop = next((m for k, m in sells if k == "stop"), None)
        msg = f"${p['ticker']} sold 20% at " + ", ".join(f"{m}x" for m in ladder) if ladder else f"${p['ticker']} no rung hit"
        if stop is not None:
            msg += f" · trail out {stop}x"
        return Result(True, msg)


class Clipper(Arm):
    number, name, kind = "05", "Clipper", "clip"

    async def work(self, task: Task) -> Result:
        await _busy(0.8, 1.6)
        return Result(True, f"stream {task.payload['minutes']}m → {task.payload['clips']} clips · captioned")


class Ghostwriter(Arm):
    number, name, kind = "06", "Ghostwriter", "draft"

    async def work(self, task: Task) -> Result:
        await _busy(0.6, 1.4)
        return Result(True, f"{task.payload['what']} drafted · waiting for approval")


class ReplyGuy(Arm):
    number, name, kind = "07", "Reply Guy", "reply"

    async def work(self, task: Task) -> Result:
        await _busy(0.2, 0.6)
        return Result(True, f"replied under @{task.payload['account']} · {task.payload['secs']}s")


class Accountant(Arm):
    number, name, kind = "08", "Accountant", "report"

    async def work(self, task: Task) -> Result:
        await _busy(0.5, 1.0)
        return Result(True, f"PnL report built · {task.payload['pnl']}")


def all_arms() -> list[Arm]:
    return [Scout(), Sniper(), RugGuard(), Treasurer(), Clipper(), Ghostwriter(), ReplyGuy(), Accountant()]
