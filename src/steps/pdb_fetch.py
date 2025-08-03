import asyncio
from pathlib import Path
from typing import Dict, Any

from .base import BaseStep
from ..api.selenium_oprlm import OprlmSeleniumClient
from ..core.models import AnalysisStep


class PDBFetchStep(BaseStep):
    """Step to fetch PDB file from OPRLM."""

    def __init__(self, step: AnalysisStep, working_dir: Path):
        super().__init__(step, working_dir)
        self.pdb_id = step.parameters.get('pdb_id')
        self.output_filename = step.parameters.get('output_filename', 'structure.pdb')

    async def execute(self) -> Dict[str, Any]:
        """Download PDB file from OPRLM."""
        if not self.pdb_id:
            raise ValueError("pdb_id parameter is required")

        output_path = self.data_dir / self.output_filename

        client = OprlmSeleniumClient()
        success = await client.download_pdb(self.pdb_id, output_path)

        if not success:
            raise RuntimeError(f"Failed to download PDB {self.pdb_id}")

        return {
            'pdb_file': str(output_path),
            'pdb_id': self.pdb_id,
            'file_size': output_path.stat().st_size
        }


class PDBUploadStep(BaseStep):
    """Step to upload and orient PDB file via OPRLM."""

    def __init__(self, step: AnalysisStep, working_dir: Path):
        super().__init__(step, working_dir)
        self.local_path = step.parameters.get('local_path')
        self.output_filename = step.parameters.get('output_filename', 'oriented_structure.pdb')

    async def execute(self) -> Dict[str, Any]:
        """Upload and orient PDB file."""
        if not self.local_path:
            raise ValueError("local_path parameter is required")
        
        input_path = Path(self.local_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        output_path = self.data_dir / self.output_filename
        
        client = OprlmSeleniumClient()
        success = await client.orient_pdb(input_path, output_path)
        
        if not success:
            raise RuntimeError("Failed to orient PDB file")
        
        return {
            'pdb_file': str(output_path),
            'original_file': str(input_path),
            'file_size': output_path.stat().st_size
        }