#!/bin/bash
source .setup.sh

python3 searcher.py batch pubmed_indexer_tiny_folder \
                --path_to_queries collections/question_E8B1_gs.jsonl \
                --output_file tiny_output.jsonl

python3 searcher.py batch pubmed_indexer_small_folder \
                --path_to_queries collections/question_E8B1_gs.jsonl \
                --output_file small_output.jsonl

python3 searcher.py batch pubmed_indexer_medium_folder \
                --path_to_queries collections/question_E8B1_gs.jsonl \
                --output_file medium_output.jsonl

python3 searcher.py batch pubmed_indexer_large_folder \
                --path_to_queries collections/question_E8B1_gs.jsonl \
                --output_file large_output.jsonl