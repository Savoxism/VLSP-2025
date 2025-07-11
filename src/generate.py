import os, json, re
from tqdm import tqdm
from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompt import *
from helper import load_seed, load_random_reference, save_json_file

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate(seed_problem, reference_document):
    prompt = RAW_PROMPT.format(JSON=json.dumps(seed_problem, ensure_ascii=False, indent=2), DOCUMENT=reference_document)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(system_instruction="Bạn là chuyên gia pháp luật."),
            contents=prompt
        )
        text = response.text    
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if not match:
            print("Warning: No JSON object found in response")
            return None
        
        return json.loads(match.group(0))
    except Exception as e:
        print(f"Error generating content: {e}")
        return None


num_examples = 20
seed_folder = "src/seed_files"
reference_folder = "src/reference_files"
output_file = "generated/train.json"

new_examples = []

for i in tqdm(range(num_examples), desc="Generating examples"):
    seed = load_seed(seed_folder)
    reference_doc = load_random_reference(reference_folder)

    example = generate(seed, reference_doc)

    if example:
        new_examples.append(example)
        # with open(f'ex_{i+1}.json', 'w', encoding='utf-8') as f:
        #         json.dump(example, f, ensure_ascii=False, indent=2)


if new_examples:
    save_json_file(new_examples, output_file)
    print(f"Successfully generated {len(new_examples)} examples")
else:
    print("No examples were successfully generated")