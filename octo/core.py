"""Core of Octo Manager: one octopus, eight arms, one task queue.

The octopus owns a queue of tasks. Each arm handles one kind of task and
works on at most one task at a time, so the desk never runs more than eight
jobs in parallel. Every finished job is written to the OCTO.LOG.
"""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Callable

RESET, DIM, BOLD = "\033[0m", "\033[2m", "\033[1m"
CORAL, LIME, GREY = "\033[38;5;209m", "\033[38;5;149m", "\033[38;5;245m"


@dataclass
class Task:
    kind: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class Result:
    ok: bool
    message: str


class Arm:
    """One of the eight arms. Subclasses set `number`, `name`, `kind` and implement `work`."""

    number = "00"
    name = "Arm"
    kind = "noop"

    def __init__(self) -> None:
        self.busy = asyncio.Lock()
        self.done = 0

    async def work(self, task: Task) -> Result:  # pragma: no cover - overridden
        raise NotImplementedError

    async def run(self, task: Task) -> Result:
        async with self.busy:
            result = await self.work(task)
            self.done += 1
            return result


class Octopus:
    """Hands tasks to the right arm, tracks what is on duty, keeps the log."""

    def __init__(self, arms: list[Arm], log: Callable[[str], None] = print) -> None:
        if len(arms) > 8:
            raise ValueError("an octopus has eight arms")
        self.arms = {arm.kind: arm for arm in arms}
        self.queue: asyncio.Queue[Task] = asyncio.Queue()
        self.log = log
        self.closed = 0
        self.manual_clicks = 0  # stays at zero, that is the point
        self.started = time.monotonic()

    def on_duty(self) -> int:
        return sum(arm.busy.locked() for arm in self.arms.values())

    async def submit(self, task: Task) -> None:
        await self.queue.put(task)

    async def _handle(self, task: Task) -> None:
        arm = self.arms.get(task.kind)
        if arm is None:
            self.log(f"{GREY}no arm for task kind '{task.kind}', dropped{RESET}")
            return
        result = await arm.run(task)
        self.closed += 1
        stamp = time.strftime("%H:%M:%S")
        mark = f"{LIME}✓{RESET}" if result.ok else f"{CORAL}✗{RESET}"
        self.log(
            f"{DIM}{stamp}{RESET}  {CORAL}arm.{arm.number}{RESET}  "
            f"{BOLD}{arm.name.upper():<12}{RESET} {result.message:<46} {mark}"
        )

    async def run(self, seconds: float) -> None:
        """Dispatch tasks until `seconds` have passed, then wait for running jobs."""
        running: set[asyncio.Task] = set()
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            try:
                task = await asyncio.wait_for(self.queue.get(), timeout=0.2)
            except asyncio.TimeoutError:
                continue
            job = asyncio.create_task(self._handle(task))
            running.add(job)
            job.add_done_callback(running.discard)
        if running:
            await asyncio.gather(*running)

    def summary(self) -> str:
        hours = self.closed * 0.6  # rough manual time saved per closed task
        return (
            f"\n{BOLD}TASKS CLOSED{RESET} {self.closed}   "
            f"{BOLD}HOURS SAVED{RESET} {hours:.1f}h   "
            f"{BOLD}MANUAL CLICKS{RESET} {LIME}{self.manual_clicks}{RESET}"
        )
