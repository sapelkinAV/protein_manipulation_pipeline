"""
Batch processor for OPRLM batch downloader.

Handles the core processing logic with OPRLM integration.
"""

import json
from pathlib import Path
from typing import Dict

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from api.selenium_oprlm import OprlmSeleniumClient
from api.models import PdbFileOptionRequest, OprlmProcessingResult
from cli.directory_manager import DirectoryManager
from cli.progress_tracker import ProgressTracker


class BatchProcessor:
    """Processes PDB configurations in batch using OPRLM."""
    
    def __init__(
        self,
        directory_manager: DirectoryManager,
        progress_tracker: ProgressTracker,
        max_workers: int = 1,
        headless: bool = True,
        continue_on_error: bool = False
    ):
        """
        Initialize batch processor.
        
        Args:
            directory_manager: Directory manager for output organization
            progress_tracker: Progress tracking and logging
            max_workers: Maximum concurrent jobs (currently only 1 supported)
            headless: Run browser in headless mode
            continue_on_error: Continue processing even if individual jobs fail
        """
        self.directory_manager = directory_manager
        self.progress_tracker = progress_tracker
        self.max_workers = max_workers
        self.headless = headless
        self.continue_on_error = continue_on_error
    
    def process_batch(self, configs: Dict[Path, PdbFileOptionRequest]) -> Dict[str, OprlmProcessingResult]:
        """
        Process all configurations in batch.
        
        Args:
            configs: Dictionary mapping config paths to PdbFileOptionRequest objects
            
        Returns:
            Dictionary mapping PDB IDs to processing results
        """
        self.progress_tracker.log_start(len(configs))
        
        results = {}
        
        for i, (config_path, config) in enumerate(configs.items(), 1):
            pdb_id = config.pdb_id
            
            try:
                self.progress_tracker.log_progress(i, len(configs), pdb_id, "Starting")
                
                # Process individual PDB
                result = self._process_single_pdb(config, config_path)
                results[pdb_id] = result
                
                # Save result
                self.progress_tracker.save_result(pdb_id, result)
                
                if result.success:
                    self.progress_tracker.log_success(pdb_id, result)
                else:
                    self.progress_tracker.log_error(pdb_id, result.error_message or "Unknown error")
                    
                    if not self.continue_on_error:
                        break
                        
            except Exception as e:
                error_result = OprlmProcessingResult(
                    step_name=f"oprlm_process_{pdb_id}",
                    success=False,
                    job_id=pdb_id,
                    error_message=str(e)
                )
                results[pdb_id] = error_result
                
                self.progress_tracker.log_error(pdb_id, str(e))
                
                if not self.continue_on_error:
                    break
        
        # Save summary
        self.progress_tracker.log_summary(results)
        summary_file = self.directory_manager.get_summary_file_path()
        self.progress_tracker.save_summary(summary_file)
        
        return results
    
    def _process_single_pdb(self, config: PdbFileOptionRequest, config_path: Path) -> OprlmProcessingResult:
        """
        Process a single PDB configuration.
        
        Args:
            config: PdbFileOptionRequest configuration
            config_path: Path to the original config file
            
        Returns:
            Processing result
        """
        pdb_id = config.pdb_id
        
        # Create PDB-specific output directory
        pdb_output_dir = self.directory_manager.get_pdb_output_dir(pdb_id)
        
        # Update config with output directory
        config.output_path = pdb_output_dir
        
        # Initialize OPRLM client
        client = OprlmSeleniumClient(headless=self.headless)
        
        try:
            # Process the PDB
            result = client.get_oprlm_processed_pdb(config)
            
            # Save metadata
            metadata_file = self.directory_manager.get_metadata_file_path(pdb_id)
            
            # Load config as dict for metadata
            with open(config_path, 'r') as f:
                config_dict = json.load(f) if config_path.suffix == '.json' else {}
            
            self.progress_tracker.save_metadata(pdb_id, metadata_file, config_dict)
            
            return result
            
        except Exception as e:
            # Create error result
            error_result = OprlmProcessingResult(
                step_name=f"oprlm_process_{pdb_id}",
                success=False,
                job_id=pdb_id,
                error_message=str(e)
            )
            
            return error_result
        
        finally:
            # Ensure driver is closed
            if hasattr(client, 'driver') and client.driver:
                client.driver.quit()