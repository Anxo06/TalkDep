import json
from collections import defaultdict

# Ranking dictionary
ranking = {
    "maria": 40, "marco": 38, "elena": 35, "linda": 28, "laura": 23, 
    "james": 22, "alex": 15, "gabriel": 13, "ethan": 12, "priya": 7, 
    "maya": 6, "noah": 5
}

def extract_patient_name(filename):
    """Extracts patient name from filename assuming the format '<name>-final-conversation.txt'"""
    return filename.split('-final-conversation.txt')[0]

def evaluate_predictions(jsonl_file):
    correct = 0
    total = 0
    neither_cases = []
    incorrect_cases = []
    
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line.strip())
            patient_a = extract_patient_name(data["file_a"])
            patient_b = extract_patient_name(data["file_b"])
            result = data["more_depressed_patient"]
            
            if (result == "Neither") or (result == "Tie"):
                score_distance = abs(ranking[patient_a] - ranking[patient_b])
                neither_cases.append((patient_a, patient_b, score_distance))
                continue
            
            higher_ranked = patient_a if ranking[patient_a] > ranking[patient_b] else patient_b
            predicted = result.lower()
            score_distance = abs(ranking[patient_a] - ranking[patient_b])
            
            if predicted == higher_ranked:
                correct += 1
            else:
                incorrect_cases.append((patient_a, patient_b, predicted, higher_ranked, score_distance))
            
            total += 1
    
    accuracy = (correct / total) * 100 if total > 0 else 0
    return accuracy, neither_cases, incorrect_cases

# Example usage
jsonl_file = "/mnt/gpu-fastdata/anxo/llms-personas/src/llms/structured_output/results/comparisons-llama3.1-8b-instruct.jsonl"  # Change this to the actual file path
accuracy, neither_cases, incorrect_cases = evaluate_predictions(jsonl_file)

print(f"Prediction Accuracy: {accuracy:.2f}%")
print("Cases where 'Neither' was chosen:")
for patient_a, patient_b, distance in neither_cases:
    print(f"{patient_a} vs {patient_b} - Score Distance: {distance}")

print("\nIncorrect Predictions:")
for patient_a, patient_b, predicted, actual, distance in incorrect_cases:
    print(f"{patient_a} vs {patient_b}: Score Distance: {distance}")
