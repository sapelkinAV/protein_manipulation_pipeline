import yaml
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import uuid

from .models import AnalysisPlan, AnalysisStep, AnalysisStatus, StepStatus


class PlanManager:
    """Manages analysis plans and their execution state."""
    
    def __init__(self, plans_dir: Path = None):
        self.plans_dir = plans_dir or Path("plans")
        self.plans_dir.mkdir(exist_ok=True)
        self._plans_cache: Dict[str, AnalysisPlan] = {}
    
    def create_plan(self, name: str, description: str, 
                   pdb_id: Optional[str] = None, 
                   local_pdb_path: Optional[str] = None,
                   configuration: Optional[Dict] = None) -> AnalysisPlan:
        """Create a new analysis plan."""
        plan_id = str(uuid.uuid4())[:8]
        
        plan = AnalysisPlan(
            id=plan_id,
            name=name,
            description=description,
            pdb_id=pdb_id,
            local_pdb_path=local_pdb_path,
            configuration=configuration or {}
        )
        
        self._save_plan(plan)
        return plan
    
    def add_step(self, plan_id: str, step: AnalysisStep) -> bool:
        """Add a step to an existing plan."""
        plan = self.get_plan(plan_id)
        if not plan:
            return False
        
        step.order = len(plan.steps)
        plan.steps.append(step)
        self._save_plan(plan)
        return True
    
    def get_plan(self, plan_id: str) -> Optional[AnalysisPlan]:
        """Get a plan by ID."""
        if plan_id in self._plans_cache:
            return self._plans_cache[plan_id]
        
        plan_file = self.plans_dir / f"{plan_id}.yaml"
        if not plan_file.exists():
            return None
        
        try:
            with open(plan_file, 'r') as f:
                data = yaml.safe_load(f)
            
            plan = AnalysisPlan(**data)
            self._plans_cache[plan_id] = plan
            return plan
        except Exception:
            return None
    
    def list_plans(self) -> List[AnalysisPlan]:
        """List all available plans."""
        plans = []
        for plan_file in self.plans_dir.glob("*.yaml"):
            plan_id = plan_file.stem
            plan = self.get_plan(plan_id)
            if plan:
                plans.append(plan)
        
        return sorted(plans, key=lambda p: p.created_at, reverse=True)
    
    def update_plan_status(self, plan_id: str, status: AnalysisStatus,
                          error_message: Optional[str] = None) -> bool:
        """Update plan status."""
        plan = self.get_plan(plan_id)
        if not plan:
            return False
        
        plan.status = status
        if error_message:
            plan.error_message = error_message
        
        if status == AnalysisStatus.RUNNING and not plan.started_at:
            plan.started_at = datetime.now()
        elif status in [AnalysisStatus.COMPLETED, AnalysisStatus.FAILED]:
            plan.completed_at = datetime.now()
        
        self._save_plan(plan)
        return True
    
    def update_step_status(self, plan_id: str, step_name: str, 
                          status: StepStatus, error_message: Optional[str] = None,
                          output_data: Optional[Dict] = None) -> bool:
        """Update step status."""
        plan = self.get_plan(plan_id)
        if not plan:
            return False
        
        for step in plan.steps:
            if step.name == step_name:
                step.status = status
                if error_message:
                    step.error_message = error_message
                if output_data:
                    step.output_data = output_data
                
                if status == StepStatus.RUNNING and not step.started_at:
                    step.started_at = datetime.now()
                elif status in [StepStatus.COMPLETED, StepStatus.FAILED]:
                    step.completed_at = datetime.now()
                
                break
        
        self._save_plan(plan)
        return True
    
    def delete_plan(self, plan_id: str) -> bool:
        """Delete a plan."""
        plan_file = self.plans_dir / f"{plan_id}.yaml"
        if plan_file.exists():
            plan_file.unlink()
            self._plans_cache.pop(plan_id, None)
            return True
        return False
    
    def _save_plan(self, plan: AnalysisPlan):
        """Save plan to disk."""
        plan_file = self.plans_dir / f"{plan.id}.yaml"
        
        # Convert to dict with string values for YAML compatibility
        data = plan.model_dump()
        
        # Ensure enum values are converted to strings
        data['status'] = plan.status.value
        for step in data.get('steps', []):
            step['status'] = step['status']
        
        with open(plan_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        self._plans_cache[plan.id] = plan