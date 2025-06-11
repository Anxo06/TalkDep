import json
import argparse
from typing import List, Tuple, Dict, Any

"""
This script evaluates the predictions of depression levels based on a ranking dictionary.
It reads a JSONL file containing pairs of patients and their predicted depression levels,
and compares these predictions against a predefined ranking of patients based on their BDI-II scores.
It calculates the accuracy of the predictions, identifies cases where 'neither' or 'tie' was chosen,
and computes the percentage of mismatches and ties that were correctly identified as having the same depression level.
"""

# Ranking dictionary with BDI-II levels
ranking: Dict[str, Tuple[int, str]] = {
    "maria": (40, "severe depression"),
    "marco": (38, "severe depression"),
    "elena": (35, "severe depression"),
    "linda": (28, "moderate depression"),
    "laura": (23, "moderate depression"),
    "james": (22, "moderate depression"),
    "alex": (15, "mild depression"),
    "gabriel": (13, "mild depression"),
    "ethan": (12, "mild depression"),
    "priya": (7, "minimal depression"),
    "maya": (6, "minimal depression"),
    "noah": (5, "minimal depression")
}

def extract_patient_name(filename: str) -> str:
    """Extracts patient name from filename assuming the format '<name>-final-conversation.txt'"""
    return filename.split('-final-conversation.txt')[0]

def calculate_percentage(part: int, total: int) -> float:
    """Calculates percentage"""
    return (part / total) * 100 if total > 0 else 0

def evaluate_predictions(jsonl_file: str) -> Tuple[float, List[Tuple[str, str, int]], List[Tuple[str, str, str, str, int]], float, float]:
    """
    Evaluates the predictions in the given JSONL file against the ranking dictionary.
    
    Returns:
        tuple: A tuple containing the accuracy, neither cases, incorrect cases,
               mismatch level match %, tie level match %.
    """
    correct: int = 0
    total: int = 0
    neither_cases: List[Tuple[str, str, int]] = []
    incorrect_cases: List[Tuple[str, str, str, str, int]] = []

    same_level_mismatches: int = 0
    total_mismatches: int = 0
    same_level_ties: int = 0
    total_ties: int = 0

    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line in f:
            data: Dict[str, Any] = json.loads(line.strip())
            patient_a: str = extract_patient_name(data["file_a"])
            patient_b: str = extract_patient_name(data["file_b"])
            result: str = data["more_depressed_patient"].lower()

            score_a, level_a = ranking[patient_a]
            score_b, level_b = ranking[patient_b]

            if (result == "neither") or (result == "tie"):
                score_distance: int = abs(score_a - score_b)
                neither_cases.append((patient_a, patient_b, score_distance))
                if level_a == level_b:
                    same_level_ties += 1
                total_ties += 1
                continue

            higher_ranked: str = patient_a if score_a > score_b else patient_b
            predicted: str = result
            score_distance: int = abs(score_a - score_b)

            if predicted == higher_ranked:
                correct += 1
            else:
                incorrect_cases.append((patient_a, patient_b, predicted, higher_ranked, score_distance))
                if level_a == level_b:
                    same_level_mismatches += 1
                total_mismatches += 1

            total += 1

    accuracy: float = calculate_percentage(correct, total)
    mismatch_level_match_percentage: float = calculate_percentage(same_level_mismatches, total_mismatches)
    tie_level_match_percentage: float = calculate_percentage(same_level_ties, total_ties)

    return accuracy, neither_cases, incorrect_cases, mismatch_level_match_percentage, tie_level_match_percentage

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate depression prediction rankings.")
    parser.add_argument("jsonl_file", type=str, help="Path to the JSONL file containing the results.")
    args = parser.parse_args()

    jsonl_file: str = args.jsonl_file
    accuracy, neither_cases, incorrect_cases, mismatch_level_match_percentage, tie_level_match_percentage = evaluate_predictions(jsonl_file)

    print(f"Prediction Accuracy: {accuracy:.2f}%")
    print("Cases where 'Neither' was chosen:")
    for patient_a, patient_b, distance in neither_cases:
        print(f"{patient_a} vs {patient_b} - Score Distance: {distance}")

    print("\nIncorrect Predictions:")
    for patient_a, patient_b, predicted, actual, distance in incorrect_cases:
        print(f"{patient_a} vs {patient_b}: Score Distance: {distance}")

    print(f"\nPercentage of mismatches with same depression level: {mismatch_level_match_percentage:.2f}%")
    print(f"Percentage of ties with same depression level: {tie_level_match_percentage:.2f}%")

# Example usage:
# python evaluate_ranking_depression_prediction.py results.jsonl