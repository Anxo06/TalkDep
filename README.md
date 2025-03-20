# LLM Judge Compare Depression

## Overview

This project is designed to compare the depressive symptoms of patients based on their therapy conversation transcripts. The main functionality is implemented in the `src/llms/structured_output/llm_judge_compare_depression.py` script, which uses an Ollama server to generate structured comparisons between patients.


## Key Files and Scripts

### `src/llms/structured_output/llm_judge_compare_depression.py`

This script compares the depressive symptoms of patients based on their therapy conversation transcripts. It uses the Ollama model to generate structured comparisons between patients.


### `conversation-datasets/conversat_txts`

This directory contains the therapy conversation transcripts of various patients in text format.


### `src/llms/structured_output/results`

This directory contains the results of the comparisons in JSONL format.


## Usage

1. Ensure you have the necessary dependencies installed.
2. Place the patient conversation text files in the [conversat_txts](http://_vscodecontentref_/0) directory.
3. Run the [llm_judge_compare_depression.py](http://_vscodecontentref_/1) script to perform the comparisons and save the results.

