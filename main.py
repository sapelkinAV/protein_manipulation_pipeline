#!/usr/bin/env python3
"""
OPRLM Biology Analysis Tool

Main entry point for the application.
"""

import argparse
import sys
from pathlib import Path

from src.core.plan_manager import PlanManager
from src.core.models import AnalysisStep, StepStatus


def create_sample_plan():
    """Create a sample analysis plan for testing."""
    plan_manager = PlanManager()
    
    # Create a new plan
    plan = plan_manager.create_plan(
        name="Sample PDB Analysis",
        description="Sample plan to test PDB fetching and processing",
        pdb_id="1ABC"
    )
    
    # Add a PDB fetch step
    fetch_step = AnalysisStep(
        name="fetch_pdb",
        description="Download PDB file from OPRLM",
        step_type="pdb_fetch",
        parameters={
            "pdb_id": "1ABC",
            "output_filename": "1abc.pdb"
        }
    )
    plan_manager.add_step(plan.id, fetch_step)
    
    print(f"Created sample plan: {plan.id}")
    print(f"Plan name: {plan.name}")
    print(f"PDB ID: {plan.pdb_id}")
    print(f"Steps: {len(plan.steps)}")
    
    return plan.id


def list_plans():
    """List all available plans."""
    plan_manager = PlanManager()
    plans = plan_manager.list_plans()
    
    if not plans:
        print("No plans found.")
        return
    
    print(f"\nFound {len(plans)} plans:")
    for plan in plans:
        print(f"  {plan.id} - {plan.name} ({plan.status.value})")
        if plan.pdb_id:
            print(f"    PDB: {plan.pdb_id}")
        if plan.local_pdb_path:
            print(f"    Local: {plan.local_pdb_path}")
        print(f"    Steps: {len(plan.steps)}")


def launch_gui():
    """Launch the terminal GUI."""
    from src.gui.main import OprlmApp
    app = OprlmApp()
    app.run()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="OPRLM Biology Analysis Tool")
    parser.add_argument("--gui", action="store_true", help="Launch terminal GUI")
    parser.add_argument("--list", action="store_true", help="List existing plans")
    parser.add_argument("--create-sample", action="store_true", help="Create sample plan")
    
    args = parser.parse_args()
    
    if args.gui:
        launch_gui()
    elif args.list:
        list_plans()
    elif args.create_sample:
        create_sample_plan()
    else:
        print("Use --gui to launch the terminal interface")
        print("Use --list to see existing plans")
        print("Use --create-sample to create a test plan")


if __name__ == "__main__":
    main()