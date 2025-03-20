import json
import os
import sys

def parse_conversation(file_path, person_name):
    conversations = []
    
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    
    conversation_id = 0
    current_conversation = None

    for line in lines:
        line = line.strip()
        
        # Check for new conversation start
        if line.startswith("### **Conversation"):
            if current_conversation:  # Save previous conversation before starting a new one
                conversations.append(current_conversation)
            
            conversation_id += 1
            current_conversation = {"conversation_id": conversation_id, "interactions": []}

        # Ensure we're inside a conversation before adding interactions
        elif current_conversation is not None:
            if line.startswith("**Therapist:**"):
                therapist_text = line.replace("**Therapist:**", "").strip()
                current_conversation["interactions"].append({"therapist": therapist_text})
            
            elif line.startswith(f"**{person_name}:**"):
                patient_text = line.replace(f"**{person_name}:**", "").strip()
                if current_conversation["interactions"]:
                    # Attach patient's response to the last therapist entry
                    current_conversation["interactions"][-1][person_name.lower()] = patient_text
                else:
                    current_conversation["interactions"].append({person_name.lower(): patient_text})

    # Append the last conversation to the list if it exists
    if current_conversation:
        conversations.append(current_conversation)

    return conversations

def process_folder(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file_name in os.listdir(input_folder):
        if file_name.endswith(".txt"):
            file_path = os.path.join(input_folder, file_name)
            person_name = file_name.replace("-final-conversation.txt", "").title()  # Extract name dynamically
            output_file = os.path.join(output_folder, f"{person_name.lower()}.json")
            
            conversations = parse_conversation(file_path, person_name)
            data = {person_name: conversations}
            
            with open(output_file, "w", encoding="utf-8") as json_file:
                json.dump(data, json_file, indent=4, ensure_ascii=False)
            
            print(f"Saved JSON for {person_name}: {output_file}")

# Run the script
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_folder> <output_folder>")
        sys.exit(1)

    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    
    process_folder(input_folder, output_folder)
