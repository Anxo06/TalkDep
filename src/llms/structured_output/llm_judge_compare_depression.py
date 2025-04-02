# compare_depression_ollama_async.py

import asyncio
import os
from typing import List, Literal
from pydantic import BaseModel, create_model, Field
import instructor
from openai import AsyncOpenAI
from itertools import combinations
import json

def create_summaries_comparison_model(patient_a_name: str, patient_b_name: str):
    """
    Dynamically generates a Pydantic model with Literal constraints
    based on the actual patient names.
    """
    return create_model(
        "SummariesComparison",
        summary_patient_a=(str, Field(
            ..., description=f"A concise summary of {patient_a_name}'s therapy conversation."
        )),
        summary_patient_b=(str, Field(
            ..., description=f"A concise summary of {patient_b_name}'s therapy conversation."
        )),
        comparison=(str, Field(
            ..., description="A comparison of each patient's depressive indicators and overall mental health status."
        )),
        conclusion=(str, Field(
            ..., description="A final professional statement about which patient, if either, appears to have more severe depression."
        )),
        more_depressed_patient=(Literal[patient_a_name, patient_b_name, "Tie"], Field(
            ..., description=f"The name of the patient who appears to exhibit a higher level of depressive symptoms. Must be either '{patient_a_name}', '{patient_b_name}', or 'Tie'."
        )),
    )


async def compare_patients_depression_ollama_async(
    patient_a_text: str, patient_a_name: str, patient_b_text: str, patient_b_name: str
):
    """
    Uses Ollama + Instructor to:
    - Summarize each patient's conversation
    - Compare depressive indicators
    - Dynamically return structured JSON with real patient names
    """

    # Dynamically generate a Pydantic model that restricts "more_depressed_patient"
    SummariesComparison = create_summaries_comparison_model(patient_a_name, patient_b_name)

    client = instructor.from_openai(
        AsyncOpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama"
        ),
        mode=instructor.Mode.JSON
    )

    # System Prompt
    system_prompt = """\
You are a licensed mental health professional with extensive experience diagnosing depression.
Your goal is to evaluate and compare two patient conversations with their therapists.
"""

    # User Prompt
    user_prompt = f"""\
Here are two therapy conversation transcripts:

[{patient_a_name}]
{patient_a_text}

[{patient_b_name}]
{patient_b_text}

Your task:
- Summarize {patient_a_name}'s mental health status (summary_patient_a) in one concise sentence.
- Summarize {patient_b_name}'s mental health status (summary_patient_b) in one concise sentence.
- Compare their depressive symptoms (comparison) in a single paragraph.
- Conclude who appears more depressed (conclusion) in one clear sentence.
- Select either "{patient_a_name}", "{patient_b_name}", or "Tie" for the most depressed patient (more_depressed_patient).


Ensure the output follows a JSON schema with the next fields:
- summary_patient_a: **string** 
- summary_patient_b: **string**
- comparison: **string** (must be a string, no lists)
- conclusion: **string** (must be a string, no lists)
- more_depressed_patient: **string** (must be either "{patient_a_name}", "{patient_b_name}", or "Tie")
"""

    # Call Ollama with dynamically generated model
    response = await client.chat.completions.create(
        model="deepseek-r1",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_model=SummariesComparison,  # Enforces structured JSON dynamically
    )

    return response

async def main():
    # Directory containing patient conversation text files
    conversations_dir = "/mnt/gpu-fastdata/anxo/llms-personas/conversation-datasets/conversat_txts"  # Replace with your directory path
    results_file = "/mnt/gpu-fastdata/anxo/llms-personas/src/llms/structured_output/results/comparisons.jsonl"  # File to save the results

    # Read all text files in the directory
    patient_files = [os.path.join(conversations_dir, f) for f in os.listdir(conversations_dir) if f.endswith('.txt')]

    # Read the content and extract names
    patient_texts = {}
    patient_names = {}  # Dictionary to store extracted names

    for file_path in patient_files:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            # Extract patient name from the first line
            patient_name = lines[0].strip().replace("Patient name: ", "").strip()
            patient_names[file_path] = patient_name  # Store the name
            patient_texts[file_path] = "".join(lines[1:])  # Store full conversation (excluding the name)

    # Ensure the results directory exists
    os.makedirs(os.path.dirname(results_file), exist_ok=True)

    # Perform pairwise comparisons
    with open(results_file, 'w', encoding='utf-8') as results:
        for file_a, file_b in combinations(patient_texts.keys(), 2):
            patient_a_text = patient_texts[file_a]
            patient_b_text = patient_texts[file_b]
            patient_a_name = patient_names[file_a]
            patient_b_name = patient_names[file_b]

            # Invoke the async function
            result = await compare_patients_depression_ollama_async(
                patient_a_text, patient_a_name, patient_b_text, patient_b_name
            )

            # Add filenames and names to the result
            result_dict = result.model_dump()
            result_dict["file_a"] = os.path.basename(file_a)
            result_dict["file_b"] = os.path.basename(file_b)
            result_dict["patient_a_name"] = patient_a_name
            result_dict["patient_b_name"] = patient_b_name

            # Reorder the fields to have file_a, file_b, patient names, and more_depressed_patient first
            ordered_result_dict = {
                "file_a": result_dict["file_a"],
                "file_b": result_dict["file_b"],
                "patient_a_name": result_dict["patient_a_name"],
                "patient_b_name": result_dict["patient_b_name"],
                "more_depressed_patient": result_dict["more_depressed_patient"],
                **{k: v for k, v in result_dict.items() if k not in ["file_a", "file_b", "patient_a_name", "patient_b_name", "more_depressed_patient"]}
            }

            # Print the result as JSON
            print(f"Comparison between {patient_a_name} ({os.path.basename(file_a)}) and {patient_b_name} ({os.path.basename(file_b)}):")
            print(json.dumps(ordered_result_dict, indent=2))

            # Save the result as a JSON line
            results.write(json.dumps(ordered_result_dict) + "\n")

# Start the async event loop
if __name__ == "__main__":
    asyncio.run(main())
