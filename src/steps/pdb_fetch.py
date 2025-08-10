import asyncio
from pathlib import Path
from typing import Dict, Any

from .base import BaseStep
from ..api.selenium_oprlm import OprlmSeleniumClient
from ..core.models import AnalysisStep
from .config import PdbFetchStepConfiguration, OprlmProcessingResult
from ..api.models import PdbFileOptionRequest, ProteinStructure, MembraneConfig, IonConfiguration, MDInputOptions


class PDBFetchStep(BaseStep):
    """Step to fetch and process PDB file from OPRLM with unified configuration interface."""

    def __init__(self, step: AnalysisStep, working_dir: Path):
        super().__init__(step, working_dir)
        self.config = PdbFetchStepConfiguration(**step.configuration)

    async def execute(self) -> OprlmProcessingResult:
        """Download and process PDB file from OPRLM."""
        if not self.config.pdb_id:
            raise ValueError("pdb_id parameter is required")

        # Create PdbFileOptionRequest from configuration
        pdb_request = self._create_pdb_request()
        
        client = OprlmSeleniumClient()
        result = client.get_oprlm_processed_pdb(pdb_request)
        
        # Save result metadata
        self.save_result(result)
        
        return result

    def _create_pdb_request(self) -> PdbFileOptionRequest:
        """Create PdbFileOptionRequest from step configuration."""
        
        # Create membrane config
        membrane_config = MembraneConfig(
            membrane_type=self.config.membrane_type,
            popc=self.config.popc,
            dopc=self.config.dopc,
            dspc=self.config.dspc,
            dmpc=self.config.dmpc,
            dppc=self.config.dppc,
            chol_value=self.config.chol_value,
            protein_topology=self.config.protein_topology
        )
        
        # Create ion configuration
        ion_config = IonConfiguration(
            ion_concentration=self.config.ion_concentration,
            ion_type=self.config.ion_type
        )
        
        # Create MD input options
        md_options = MDInputOptions(
            namd_enabled=self.config.namd_enabled,
            gromacs_enabled=self.config.gromacs_enabled,
            openmm_enabled=self.config.openmm_enabled
        )
        
        # Create output directory
        output_dir = self.config.output_dir or (self.data_dir / self.config.pdb_id)
        
        return PdbFileOptionRequest(
            pdb_id=self.config.pdb_id,
            file_input_mode=ProteinStructure(self.config.file_input_mode),
            file_path=self.config.file_path,
            email=self.config.email,
            membrane_config=membrane_config,
            input_protein_size_plus=self.config.input_protein_size_plus,
            water_thickness_z=self.config.water_thickness_z,
            ion_configuration=ion_config,
            temperature=self.config.temperature,
            perform_charmm_minimization=self.config.perform_charmm_minimization,
            md_input_options=md_options,
            output_dir=output_dir
        )