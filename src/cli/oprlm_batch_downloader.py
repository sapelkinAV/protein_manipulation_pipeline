#!/usr/bin/env python3
"""
OPRLM Batch Downloader CLI

A command-line utility for batch processing PDB files through OPRLM
using YAML configuration files.
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
import getpass

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from cli.config_loader import ConfigLoader
from cli.directory_manager import DirectoryManager
from cli.batch_processor import BatchProcessor
from cli.progress_tracker import ProgressTracker


def create_parser():
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="Batch download PDB files processed through OPRLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i ./configs -o ./results
  %(prog)s -i ./configs -o ./results --user alice --max-workers 2
  %(prog)s -i ./configs -o ./results --dry-run
  %(prog)s -i ./configs -o ./results --continue-on-error --headless
        """
    )
    
    parser.add_argument(
        "-i", "--input-dir",
        type=Path,
        required=True,
        help="Input directory containing YAML configuration files"
    )
    
    parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        required=True,
        help="Output directory for processed results"
    )
    
    parser.add_argument(
        "--user",
        type=str,
        default=getpass.getuser(),
        help="Username for launch identification (default: current user)"
    )
    
    parser.add_argument(
        "--config-pattern",
        type=str,
        default="*.yml",
        help="File pattern for YAML configs (default: *.yml)"
    )
    
    parser.add_argument(
        "--max-workers",
        type=int,
        default=1,
        help="Maximum concurrent jobs (default: 1)"
    )
    
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode"
    )
    
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue processing even if individual jobs fail"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate configs without processing"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser


def validate_directories(input_dir: Path, output_dir: Path) -> None:
    """Validate input and output directories."""
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")
    
    if not input_dir.is_dir():
        raise NotADirectoryError(f"Input path is not a directory: {input_dir}")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)


def generate_launch_id(username: str) -> str:
    """Generate launch ID with username and timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{username}_{timestamp}"


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Validate directories
        validate_directories(args.input_dir, args.output_dir)
        
        # Generate launch ID
        launch_id = generate_launch_id(args.user)
        
        # Initialize components
        config_loader = ConfigLoader(args.input_dir, args.config_pattern)
        directory_manager = DirectoryManager(args.output_dir, launch_id)
        progress_tracker = ProgressTracker(directory_manager.logs_dir, args.verbose)
        batch_processor = BatchProcessor(
            directory_manager=directory_manager,
            progress_tracker=progress_tracker,
            max_workers=args.max_workers,
            headless=args.headless,
            continue_on_error=args.continue_on_error
        )
        
        # Load configurations
        configs = config_loader.load_configs()
        
        if not configs:
            print("No configuration files found.")
            return 0
        
        print(f"Found {len(configs)} configuration files")
        
        if args.dry_run:
            print("DRY RUN: Validating configurations...")
            for config_path, config in configs.items():
                print(f"  ✓ {config_path.name}: {config.pdb_id}")
            return 0
        
        # Process batch
        print(f"Starting batch processing with launch ID: {launch_id}")
        results = batch_processor.process_batch(configs)
        
        # Print summary
        successful = sum(1 for r in results.values() if r.success)
        failed = len(results) - successful
        
        print(f"\nBatch processing complete:")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        print(f"  Results saved to: {directory_manager.launch_dir}")
        
        return 0 if failed == 0 else 1
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())