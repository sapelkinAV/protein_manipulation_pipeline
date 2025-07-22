from abc import ABC, abstractmethod
from typing import Dict, Any
from pathlib import Path

from ..core.models import AnalysisStep


class BaseStep(ABC):
    """Base class for analysis steps."""

    def __init__(self, step: AnalysisStep, working_dir: Path):
        self.step = step
        self.working_dir = working_dir
        self.data_dir = working_dir / "data"
        self.results_dir = working_dir / "results"

        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    async def execute(self) -> Dict[str, Any]:
        """Execute the step and return output data."""
        pass

    @property
    def name(self) -> str:
        return self.step.name