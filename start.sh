#!/bin/bash

# Default values for arguments
arg_a="default_a"
arg_b="default_b"

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -a)
            arg_a="$2"
            shift 2
            ;;
        -b)
            arg_b="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run the Python script with the parsed arguments
python main.py -a "$arg_a" -b "$arg_b"
