"""RGK Octo Manager — one octopus, eight arms, zero manual clicks."""
from .core import Arm, Octopus, Result, Task
from .arms import all_arms, passes_filter, kelly_units, exit_plan

__all__ = ["Arm", "Octopus", "Result", "Task", "all_arms", "passes_filter", "kelly_units", "exit_plan"]
__version__ = "0.1.0"
