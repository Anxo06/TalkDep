import json
from typing import List, Tuple, Dict, Any

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

def calculate_depression_level_match_percentage(same_level_mismatches: int, total_mismatches: int) -> float:
    """Calculates the percentage of mismatches or ties with the same depression level"""
    return (same_level_mismatches / total_mismatches) * 100 if total_mismatches > 0 else 0

def evaluate_predictions(jsonl_file: str) -> Tuple[float, List[Tuple[str, str, int]], List[Tuple[str, str, str, str, int]], float]:
    """
    Evaluates the predictions in the given JSONL file against the ranking dictionary.
    
    Args:
        jsonl_file (str): Path to the JSONL file containing the predictions.
    
    Returns:
        tuple: A tuple containing the accuracy, neither cases, incorrect cases, and depression level match percentage.
    """
    correct: int = 0
    total: int = 0
    # List of tuples for cases where 'neither' or 'tie' was chosen
    # Each tuple contains (patient_a, patient_b, score_distance)
    neither_cases: List[Tuple[str, str, int]] = []
    # List of tuples for incorrect predictions
    # Each tuple contains (patient_a, patient_b, predicted, actual, score_distance)
    incorrect_cases: List[Tuple[str, str, str, str, int]] = []
    same_level_mismatches: int = 0
    total_mismatches: int = 0

    # Open and read the JSONL file line by line
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line in f:
            data: Dict[str, Any] = json.loads(line.strip())
            patient_a: str = extract_patient_name(data["file_a"])
            patient_b: str = extract_patient_name(data["file_b"])
            result: str = data["more_depressed_patient"].lower()

            score_a, level_a = ranking[patient_a]
            score_b, level_b = ranking[patient_b]

            # Handle cases where the result is "neither" or "tie"
            if (result == "neither") or (result == "tie"):
                score_distance: int = abs(score_a - score_b)
                neither_cases.append((patient_a, patient_b, score_distance))
                if level_a == level_b:
                    same_level_mismatches += 1
                    total_mismatches += 1
                continue

            # Determine the higher ranked patient based on the scores
            higher_ranked: str = patient_a if score_a > score_b else patient_b
            predicted: str = result
            score_distance: int = abs(score_a - score_b)

            # Check if the prediction is correct
            if predicted == higher_ranked:
                correct += 1
            else:
                incorrect_cases.append((patient_a, patient_b, predicted, higher_ranked, score_distance))
                if level_a == level_b:
                    same_level_mismatches += 1
                total_mismatches += 1

            total += 1

    # Calculate accuracy
    accuracy: float = (correct / total) * 100 if total > 0 else 0
    # Calculate depression level match percentage
    depression_level_match_percentage: float = calculate_depression_level_match_percentage(same_level_mismatches, total_mismatches)
    
    return accuracy, neither_cases, incorrect_cases, depression_level_match_percentage

# Example usage
jsonl_file: str = "/mnt/gpu-fastdata/anxo/llms-personas/src/llms/structured_output/results/comparisons-llama3.1-8b-instruct.jsonl"  # Change this to the actual file path
accuracy, neither_cases, incorrect_cases, depression_level_match_percentage = evaluate_predictions(jsonl_file)

print(f"Prediction Accuracy: {accuracy:.2f}%")
print("Cases where 'Neither' was chosen:")
for patient_a, patient_b, distance in neither_cases:
    print(f"{patient_a} vs {patient_b} - Score Distance: {distance}")

print("\nIncorrect Predictions:")
for patient_a, patient_b, predicted, actual, distance in incorrect_cases:
    print(f"{patient_a} vs {patient_b}: Score Distance: {distance}")

print(f"\nPercentage of mismatches or ties with same depression level: {depression_level_match_percentage:.2f}%")