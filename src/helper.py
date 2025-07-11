import os
import json
import random
import time
import shutil 

def load_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return None
    
def load_seed(folder_path):
    files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    selected = random.choice(files)
    with open(os.path.join(folder_path, selected), 'r', encoding='utf-8') as f:
        data = json.load(f)
    return random.choice(data) if isinstance(data, list) else data

def load_random_reference(folder_path):
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    selected = random.choice(files)
    with open(os.path.join(folder_path, selected), 'r', encoding='utf-8') as f:
        return f.read()

def save_json_file(data, file_path="generated/train.json", append=True):
    try:
        if not os.path.exists("generated"):
            os.makedirs("generated")
            
        existing_data = []
        
        if append and os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                print(f"Loaded {len(existing_data)} existing examples from {file_path}")
            except json.JSONDecodeError:
                print(f"Warning: {file_path} exists but contains invalid JSON. Creating backup.")
                # Create a backup of the corrupted file
                backup_path = f"{file_path}.backup.{int(time.time())}"
                shutil.copy2(file_path, backup_path)
                
        # Combine existing data with new data
        if isinstance(data, list):
            combined_data = existing_data + data
        else:
            combined_data = existing_data + [data]
            
        # Save the combined data
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, ensure_ascii=False, indent=2)
            
        print(f"Successfully saved {len(combined_data)} examples to {file_path} ({len(combined_data) - len(existing_data)} new)")
        return True
    except Exception as e:
        print(f"Error saving file {file_path}: {e}")
        return False