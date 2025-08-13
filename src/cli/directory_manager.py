"""
Directory manager for OPRLM batch downloader.

Handles creation and organization of output directories with
username_timestamp format.
"""

from pathlib import Path
from datetime import datetime


class DirectoryManager:
    """Manages directory creation and organization for batch processing."""
    
    def __init__(self, output_dir: Path, launch_id: str):
        """
        Initialize directory manager.
        
        Args:
            output_dir: Base output directory
            launch_id: Launch identifier (username_timestamp format)
        """
        self.output_dir = output_dir
        self.launch_id = launch_id
        self.launch_dir = output_dir / launch_id
        self.logs_dir = self.launch_dir / "logs"
        
        # Create directories
        self._create_directories()
    
    def _create_directories(self) -> None:
        """Create all necessary directories."""
        self.launch_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    def get_pdb_output_dir(self, pdb_id: str) -> Path:
        """
        Get the output directory for a specific PDB ID.
        
        Args:
            pdb_id: PDB identifier
            
        Returns:
            Path to the PDB-specific output directory
        """
        pdb_dir = self.launch_dir / pdb_id
        pdb_dir.mkdir(parents=True, exist_ok=True)
        return pdb_dir
    
    def get_summary_file_path(self) -> Path:
        """
        Get the path for the batch summary JSON file.
        
        Returns:
            Path to summary.json
        """
        return self.launch_dir / "summary.json"
    
    def get_batch_log_path(self) -> Path:
        """
        Get the path for the batch log file.
        
        Returns:
            Path to batch.log
        """
        return self.logs_dir / "batch.log"
    
    def get_error_log_path(self) -> Path:
        """
        Get the path for the error log file.
        
        Returns:
            Path to errors.log
        """
        return self.logs_dir / "errors.log"
    
    def get_metadata_file_path(self, pdb_id: str) -> Path:
        """
        Get the path for a PDB-specific metadata file.
        
        Args:
            pdb_id: PDB identifier
            
        Returns:
            Path to metadata.json for the PDB
        """
        pdb_dir = self.get_pdb_output_dir(pdb_id)
        return pdb_dir / "metadata.json"
    
    @staticmethod
    def generate_launch_id(username: str) -> str:
        """
        Generate a launch ID with username and timestamp.
        
        Args:
            username: Username for the launch
            
        Returns:
            Launch ID in format: username_YYYYMMDD_HHMMSS
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{username}_{timestamp}"