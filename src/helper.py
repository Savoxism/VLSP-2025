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
    if not os.path.exists("generated"):
        os.makedirs("generated")
    existing = []
    if append and os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except json.JSONDecodeError:
            backup = f"{file_path}.backup.{int(time.time())}"
            shutil.copy2(file_path, backup)
    combined = existing + (data if isinstance(data, list) else [data])
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(combined)} examples ({len(combined)-len(existing)} new) to {file_path}")
