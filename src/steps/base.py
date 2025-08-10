from abc import ABC, abstractmethod
from typing import Dict, Any
from pathlib import Path

from ..core.models import AnalysisStep
from .config import StepConfiguration, StepResult


class BaseStep(ABC):
    """Base class for analysis steps with unified configuration interface."""

    def __init__(self, step: AnalysisStep, working_dir: Path):
        self.step = step
        self.working_dir = working_dir
        self.data_dir = working_dir / "data"
        self.results_dir = working_dir / "results"

        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    async def execute(self) -> StepResult:
        """Execute the step and return structured result."""
        pass

    @property
    def name(self) -> str:
        return self.step.name

    def get_configuration(self) -> StepConfiguration:
        """Get step configuration from step parameters."""
        return StepConfiguration(**self.step.configuration)

    def save_result(self, result: StepResult) -> None:
        """Save step result to results directory."""
        result_file = self.results_dir / f"{self.name}_result.json"
        with open(result_file, 'w') as f:
            f.write(result.json(indent=2))