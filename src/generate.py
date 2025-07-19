import os, json, re
from tqdm import tqdm
from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompt import *
from helper import load_seed, load_random_reference, save_json_file

load_dotenv()

API_KEY = "AIzaSyBG7Rd4avKco5WkAR_11VSP6jTEMAz8UdM"

client = genai.Client(api_key=API_KEY)

def generate(seed_problem, reference_document):
    prompt = GENERATE_PROMPT.format(
        JSON=json.dumps(seed_problem, ensure_ascii=False, indent=2),
        CONTEXT=reference_document
    )
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        ),
    ]
    cfg = types.GenerateContentConfig(response_mime_type="text/plain")
    stream = client.models.generate_content_stream(
        model="gemma-3n-e4b-it",
        contents=contents,
        config=cfg,
    )
    text = ""
    for chunk in tqdm(stream, desc="Generating response"):
        text += chunk.text or ""
    start = text.find("{")
    end   = text.rfind("}")
    if start < 0 or end < 0 or end <= start:
        raise ValueError(f"JSON braces not found in\n{text}")
    json_str = text[start : end+1]
    return json.loads(json_str)


num_examples     = 5
seed_folder      = "src/seed_files"
reference_folder = "src/reference_files"
output_file      = "generated/train.json"

new_examples = []
for _ in tqdm(range(num_examples), desc="Generating examples with gemma"):
    seed          = load_seed(seed_folder)
    reference_doc = load_random_reference(reference_folder)
    try:
        example = generate(seed, reference_doc)
        new_examples.append(example)
    except Exception as e:
        print("Failed to parse JSON from response:", e)

if new_examples:
    save_json_file(new_examples, output_file)
else:
    print("No examples were successfully generated with gemma model")

