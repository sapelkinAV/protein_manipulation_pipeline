#!/bin/bash
# OPRLM Batch Downloader wrapper script

# Set PYTHONPATH to include src directory
export PYTHONPATH="$(dirname "$0")/src:$PYTHONPATH"

# Run the CLI with all arguments
python -m cli.oprlm_batch_downloader "$@"