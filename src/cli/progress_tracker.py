"""
Progress tracking and logging for OPRLM batch downloader.

Provides real-time progress updates and centralized logging.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from api.models import OprlmProcessingResult


class ProgressTracker:
    """Tracks progress and manages logging for batch processing."""
    
    def __init__(self, logs_dir: Path, verbose: bool = False):
        """
        Initialize progress tracker.
        
        Args:
            logs_dir: Directory for log files
            verbose: Enable verbose logging
        """
        self.logs_dir = logs_dir
        self.verbose = verbose
        self.results = {}
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        simple_formatter = logging.Formatter('%(message)s')
        
        # Setup batch logger
        self.batch_logger = logging.getLogger('oprlm_batch')
        self.batch_logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)
        
        # Remove existing handlers
        self.batch_logger.handlers.clear()
        
        # File handler for batch.log
        batch_handler = logging.FileHandler(self.logs_dir / "batch.log")
        batch_handler.setLevel(logging.DEBUG)
        batch_handler.setFormatter(detailed_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        
        # Error handler for errors.log
        error_handler = logging.FileHandler(self.logs_dir / "errors.log")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        
        self.batch_logger.addHandler(batch_handler)
        self.batch_logger.addHandler(console_handler)
        self.batch_logger.addHandler(error_handler)
    
    def log_start(self, total_configs: int) -> None:
        """Log the start of batch processing."""
        self.batch_logger.info(f"Starting batch processing of {total_configs} configurations")
    
    def log_progress(self, current: int, total: int, pdb_id: str, status: str) -> None:
        """Log processing progress."""
        progress = (current / total) * 100
        self.batch_logger.info(f"[{current}/{total}] {pdb_id}: {status} ({progress:.1f}%)")
    
    def log_success(self, pdb_id: str, result: OprlmProcessingResult) -> None:
        """Log successful processing."""
        self.batch_logger.info(f"✓ {pdb_id}: Successfully processed")
        if self.verbose:
            self.batch_logger.debug(f"  Files: {result.processed_pdb_path}, {result.charmm_gui_path}, {result.md_input_path}")
    
    def log_error(self, pdb_id: str, error: str) -> None:
        """Log processing error."""
        self.batch_logger.error(f"✗ {pdb_id}: {error}")
    
    def log_summary(self, results: Dict[str, OprlmProcessingResult]) -> None:
        """Log batch summary."""
        successful = sum(1 for r in results.values() if r.success)
        failed = len(results) - successful
        
        self.batch_logger.info("=" * 50)
        self.batch_logger.info("BATCH PROCESSING SUMMARY")
        self.batch_logger.info("=" * 50)
        self.batch_logger.info(f"Total configurations: {len(results)}")
        self.batch_logger.info(f"Successful: {successful}")
        self.batch_logger.info(f"Failed: {failed}")
        self.batch_logger.info(f"Success rate: {(successful/len(results))*100:.1f}%")
    
    def save_result(self, pdb_id: str, result: OprlmProcessingResult) -> None:
        """Save individual result to tracking."""
        self.results[pdb_id] = result
    
    def save_summary(self, summary_file: Path) -> None:
        """Save batch summary to JSON file."""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_configs": len(self.results),
            "successful": sum(1 for r in self.results.values() if r.success),
            "failed": sum(1 for r in self.results.values() if not r.success),
            "results": {pdb_id: result.to_dict() for pdb_id, result in self.results.items()}
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
    
    def save_metadata(self, pdb_id: str, metadata_file: Path, config: Dict[str, Any]) -> None:
        """Save metadata for individual PDB processing."""
        metadata = {
            "pdb_id": pdb_id,
            "timestamp": datetime.now().isoformat(),
            "config": config,
            "result": self.results[pdb_id].to_dict() if pdb_id in self.results else None
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)