import os, re, json, copy
from tqdm import tqdm
from dotenv import load_dotenv
from google import genai
from google.genai import types
from helper import load_json_file, save_json_file
from prompt import VERIFICATION_PROMPT

load_dotenv()

client = genai.Client(api_key="AIzaSyBG7Rd4avKco5WkAR_11VSP6jTEMAz8UdM")

def verify(question_data):
    json_str = json.dumps(question_data, ensure_ascii=False, indent=2)

    prompt = VERIFICATION_PROMPT.format(JSON=json_str)

    response = client.models.generate_content(
        model = "gemini-2.5-flash",
        config = types.GenerateContentConfig(system_instruction="Bạn là chuyên gia phân tích pháp lý."),
        contents = prompt
    )

    text = response.text

    match = re.search(r'\{.*\}', text, re.DOTALL)
    
    if not match:
        print(f"Warning: Could not extract JSON from verification response")
        return question_data
        
    verification_result = json.loads(match.group(0))
    
    if verification_result.get("verification_result") == "pass":
        print("Verification passed: Conclusion is logically consistent")
        return question_data
    elif verification_result.get("verification_result") == "fixed":
        print("Verification fixed: Updated conclusion for logical consistency")
        return verification_result
    else:
        print(f"Verification error: {verification_result.get('error_message', 'Unknown issue')}")
        return question_data

def find_inconsistent_questions(data):
    inconsistent_questions = []
    for i, item in enumerate(tqdm(data, desc="Checking logical consistency")):
        print(f"\nChecking question {i+1}/{len(data)}")
        original_item = copy.deepcopy(item)
        verified_item = verify(item)
        
        if verified_item != original_item:
            inconsistent_questions.append({"index": i, "original": original_item, "fixed": verified_item})
            print(f"Question {i+1} needs fixing")
        else:
            print(f"Question {i+1} is logically consistent")
    
    return inconsistent_questions

input_file = "generated/train.json"
output_file = "generated/verified_train.json"
data = load_json_file(input_file)

# Create backup of original data
backup_file = f"{input_file}.backup"
save_json_file(data, backup_file)
print(f"Created backup at {backup_file}")

# First check for inconsistencies
print(f"Starting verification of {len(data)} questions...")
inconsistent = find_inconsistent_questions(data)

# Then fix all inconsistent questions
if inconsistent:
    print(f"\nFound {len(inconsistent)} questions with logical inconsistencies")
    
    for item in inconsistent:
        idx = item["index"]
        data[idx] = item["fixed"]
        print(f"Fixed question {idx+1}")
    
    save_json_file(data, output_file)
    print(f"All {len(inconsistent)} fixed questions saved to {output_file}")
else:
    print("\nAll questions are logically consistent!")
    save_json_file(data, output_file)
    print(f"All verified questions saved to {output_file}")