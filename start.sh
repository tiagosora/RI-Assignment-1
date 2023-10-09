#!/bin/bash

# Default values for arguments
arg_f=""

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -f)
            arg_f="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: -$1"
            exit 1
            ;;
    esac
done

# Run the Python script with the parsed arguments
python main.py -f "$arg_f"
