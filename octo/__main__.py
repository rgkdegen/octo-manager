"""Run the desk:  python -m octo --seconds 20"""
from __future__ import annotations

import argparse
import asyncio
import random

from .arms import all_arms
from .core import BOLD, CORAL, RESET, Octopus
from .sim import random_task


async def feed(octo: Octopus, seconds: float, rate: float) -> None:
    loop = asyncio.get_running_loop()
    end = loop.time() + seconds
    while loop.time() < end:
        await octo.submit(random_task())
        await asyncio.sleep(random.expovariate(rate))


async def main(seconds: float, rate: float, seed: int | None) -> None:
    if seed is not None:
        random.seed(seed)
    octo = Octopus(all_arms())
    print(f"{CORAL}{BOLD}OCTO.LOG{RESET}  one octopus · eight arms · sim run, numbers illustrative\n")
    await asyncio.gather(feed(octo, seconds, rate), octo.run(seconds))
    print(octo.summary())


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="RGK Octo Manager demo desk")
    ap.add_argument("--seconds", type=float, default=15)
    ap.add_argument("--rate", type=float, default=3.0, help="tasks per second")
    ap.add_argument("--seed", type=int, default=None)
    a = ap.parse_args()
    asyncio.run(main(a.seconds, a.rate, a.seed))
