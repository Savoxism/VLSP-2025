import json
import os
import random
import re

from dotenv import load_dotenv

from llm import gemini
from prompt import GENQA_PROMPT

_ = load_dotenv()


def load_random_seed(folder_path: str):
    files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.endswith(".json") and os.path.isfile(os.path.join(folder_path, f))
    ]
    if not files:
        raise FileNotFoundError(f"No JSON files found in {folder_path}")
    selected_file = random.choice(files)
    with open(selected_file, "r", encoding="utf-8") as f:
        data: dict | list = json.load(f)
    if not data:
        raise ValueError(f"The file {selected_file} is empty or invalid")
    return random.choice(data) if isinstance(data, list) else data


def load_random_reference(folder_path: str):
    files = [
        f
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f))
    ]
    selected = random.choice(files)
    with open(os.path.join(folder_path, selected), "r", encoding="utf-8") as f:
        return f.read()


def generate(seed_problem: dict, reference_document: str):
    prompt = GENQA_PROMPT.format(
        JSON=json.dumps(seed_problem, ensure_ascii=False, indent=2),
        DOCUMENT=reference_document,
    )

    response = gemini.generate(prompt)

    match = re.search(r"\{.*\}", response, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found")
    return json.loads(match.group(0))


seed = load_random_seed("src/seed_files")
reference_doc = load_random_reference("src/reference")
new_example = generate(seed, reference_doc)

with open("ex.json", "w", encoding="utf-8") as f:
    json.dump(new_example, f, ensure_ascii=False, indent=2)

print("DONE")
