from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field


class AnalysisStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class AnalysisStep(BaseModel):
    name: str
    description: str
    step_type: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    configuration: Dict[str, Any] = Field(default_factory=dict)
    status: StepStatus = StepStatus.PENDING
    order: int = 0
    depends_on: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    output_data: Dict[str, Any] = Field(default_factory=dict)


class AnalysisPlan(BaseModel):
    id: str
    name: str
    description: str
    pdb_id: Optional[str] = None
    local_pdb_path: Optional[str] = None
    steps: List[AnalysisStep] = Field(default_factory=list)
    status: AnalysisStatus = AnalysisStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExecutionProgress(BaseModel):
    plan_id: str
    current_step: int = 0
    total_steps: int = 0
    step_progress: Dict[str, StepStatus] = Field(default_factory=dict)
    estimated_remaining_time: Optional[float] = None
    last_updated: datetime = Field(default_factory=datetime.now)