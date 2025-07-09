"""
performs quality assurance by checking the accuracy and logical conistency of answers, reasoning paths, and legal references in the generated data.
"""
import os
import json
import random

def load_random_seed(folder_path):
    files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    all_seeds = []
    for fn in files:
        with open(os.path.join(folder_path, fn), 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_seeds.extend(data if isinstance(data, list) else [data])
    return random.choice(all_seeds)

seed_problem = load_random_seed('src/seed_files')
print(seed_problem)