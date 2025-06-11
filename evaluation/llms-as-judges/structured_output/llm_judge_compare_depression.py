import asyncio
import os
import argparse
from typing import List, Literal
from pydantic import BaseModel, create_model, Field, ValidationError
import instructor
from openai import AsyncOpenAI
from itertools import combinations
import json
import re
import difflib

"""
This script uses the Ollama API to compare two patients' therapy conversations from LLMs
and determine which patient appears to have more severe depression.
It dynamically generates a Pydantic model with Literal constraints
based on the actual patient names.
It uses fuzzy matching to resolve the closest valid value for the 'more_depressed_patient' field.
"""

def resolve_closest_literal_value(candidate: str, valid_values: list[str], cutoff: float = 0.8) -> str:
    """
    Match a candidate string to the closest valid value using fuzzy matching.
    Returns the best match if similarity is above the cutoff.
    """
    candidate = candidate.strip()
    matches = difflib.get_close_matches(candidate, valid_values, n=1, cutoff=cutoff)
    return matches[0] if matches else candidate  # fallback to original (to force failure if invalid)


def parse_llm_response_to_summaries(content: str, SummariesComparison):
    """
    Parses LLM JSON content into a SummariesComparison object.
    - Fills in missing fields with "foo" (except 'more_depressed_patient')
    - Applies fuzzy matching to 'more_depressed_patient'
    """
    try:
        # Extract JSON from triple backticks or fallback
        match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
        if not match:
            match = re.search(r"(\{.*?\})", content, re.DOTALL)

        if not match:
            print("❌ No JSON block found in LLM response.")
            return None

        json_str = match.group(1)
        parsed_data = json.loads(json_str)

        # Fill default "foo" for any missing field except 'more_depressed_patient'
        expected_fields = SummariesComparison.model_fields.keys()
        for field in expected_fields:
            if field not in parsed_data and field != "more_depressed_patient":
                parsed_data[field] = "foo"

        # Handle 'more_depressed_patient' with fuzzy matching
        if "more_depressed_patient" not in parsed_data:
            print("❌ 'more_depressed_patient' is missing — skipping.")
            return None

        allowed_values = SummariesComparison.model_fields["more_depressed_patient"].annotation.__args__
        cleaned_value = parsed_data["more_depressed_patient"].strip()
        parsed_data["more_depressed_patient"] = resolve_closest_literal_value(
            cleaned_value, list(allowed_values)
        )

        # Return validated model
        return SummariesComparison(**parsed_data)

    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
    except ValidationError as e:
        print(f"❌ Validation error: {e}")
    return None

    
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

    # Use raw client (not instructor)
    raw_client = AsyncOpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama"
    )

    SummariesComparison = create_summaries_comparison_model(patient_a_name, patient_b_name)


    # System Prompt
    system_prompt = """\
You are a licensed mental health professional with extensive experience diagnosing depression.
Your goal is to evaluate and compare two patient conversations with their therapists and provide a structured JSON output as you will be asked.
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


Ensure the output follows a JSON schema with the next fields, such as:
{{
"summary_patient_a": "(a string)" ,
"summary_patient_b": "(a string)",
"comparison": "(a string)",
"conclusion": "(a string)",
"more_depressed_patient": "(a string, must be either "{patient_a_name}", "{patient_b_name}", or "Tie")"
}}
"""

    # Call Ollama with dynamically generated model
    response = await raw_client.chat.completions.create(
        model="deepseek-r1:14b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
    )

    content = response.choices[0].message.content
    print(f"Response content: {content}")
    # Parse the response content to structured JSON
    return parse_llm_response_to_summaries(content, SummariesComparison)

async def main(conversations_dir: str, results_file: str):
    """
    Main function to read patient conversation files, compare depression levels,
    and save results to a file.
    """
    # Read all text files in the directory
    patient_files = [os.path.join(conversations_dir, f) for f in os.listdir(conversations_dir) if f.endswith('.txt')]

    # Read the content and extract names
    patient_texts = {}
    patient_names = {}

    for file_path in patient_files:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            # Extract patient name from the first line of the file
            patient_name = lines[0].strip().replace("Patient name: ", "").strip()
            patient_names[file_path] = patient_name
            patient_texts[file_path] = "".join(lines[1:])  # Remaining lines are the conversation text

    # Ensure the directory for the results file exists
    os.makedirs(os.path.dirname(results_file), exist_ok=True)

    # Open the results file for writing
    with open(results_file, 'w', encoding='utf-8') as results:
        # Compare all pairs of patient conversations
        for file_a, file_b in combinations(patient_texts.keys(), 2):
            patient_a_text = patient_texts[file_a]
            patient_b_text = patient_texts[file_b]
            patient_a_name = patient_names[file_a]
            patient_b_name = patient_names[file_b]

            try:
                # Compare the two patients using the Ollama API
                result = await compare_patients_depression_ollama_async(
                    patient_a_text, patient_a_name, patient_b_text, patient_b_name
                )

                if result is None:
                    print(f"⚠️ Skipping {patient_a_name} vs {patient_b_name}: invalid or missing JSON.")
                    continue

                # Prepare the result dictionary for saving
                result_dict = result.model_dump()
                result_dict["file_a"] = os.path.basename(file_a)
                result_dict["file_b"] = os.path.basename(file_b)
                result_dict["patient_a_name"] = patient_a_name
                result_dict["patient_b_name"] = patient_b_name

                # Order the result dictionary for better readability
                ordered_result_dict = {
                    "file_a": result_dict["file_a"],
                    "file_b": result_dict["file_b"],
                    "patient_a_name": result_dict["patient_a_name"],
                    "patient_b_name": result_dict["patient_b_name"],
                    "more_depressed_patient": result_dict["more_depressed_patient"],
                    **{k: v for k, v in result_dict.items() if k not in ["file_a", "file_b", "patient_a_name", "patient_b_name", "more_depressed_patient"]}
                }

                # Print and save the result
                print(f"\n✅ Comparison: {patient_a_name} vs {patient_b_name}")
                print(json.dumps(ordered_result_dict, indent=2))
                results.write(json.dumps(ordered_result_dict) + "\n")

            except Exception as e:
                print(f"❌ Unexpected error for {patient_a_name} vs {patient_b_name}: {e}")
                continue  # move on to next pair    

# Start the async event loop
if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Compare depression levels between patients using therapy conversation logs.")
    parser.add_argument("conversations_dir", type=str, help="Path to the directory containing patient conversation text files.")
    parser.add_argument("results_file", type=str, help="Path to the file where results will be saved.")
    args = parser.parse_args()

    # Run the main function with the provided arguments
    asyncio.run(main(args.conversations_dir, args.results_file))

# Example usage:
# python llm_judge_compare_depression.py /path/to/conversations /path/to/results.jsonl