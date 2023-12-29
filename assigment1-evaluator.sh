#!/bin/bash
source .setup.sh

python3 evaluator.py collections/question_E8B1_gs.jsonl tiny_output.jsonl

python3 evaluator.py collections/question_E8B1_gs.jsonl small_output.jsonl

python3 evaluator.py collections/question_E8B1_gs.jsonl medium_output.jsonl

python3 evaluator.py collections/question_E8B1_gs.jsonl large_output.jsonl