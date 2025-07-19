import os
import re
import json
from tqdm import tqdm
from dotenv import load_dotenv
from google import genai
from google.genai import types
from helper import load_json_file, save_json_file
from prompt import REFINEMENT_PROMPT

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def check_format(question_text):
    option_patterns = [
        r'A[\.:\)\-\s].*B[\.:\)\-\s].*C[\.:\)\-\s].*D[\.:\)\-\s]',
        r'\(A\).*?\(B\).*?\(C\).*?\(D\)'
    ]
    for pattern in option_patterns:
        if re.search(pattern, question_text, re.DOTALL):
            return True
    return False

def find_incorrect_questions(data):
    incorrect_questions = []
    for i, item in enumerate(data):
        question = item.get('question', "")
        if not check_format(question):
            incorrect_questions.append({"index": i, "question": question})
    return incorrect_questions

def refine(question_data): 
    json_str = json.dumps(question_data, ensure_ascii=False, indent=2)

    prompt = REFINEMENT_PROMPT.format(JSON=json_str)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
            config=types.GenerateContentConfig(system_instruction="Bạn là chuyên gia pháp luật."),
            contents=prompt
    )

    text = response.text
    match = re.search(r'\{.*\}', text, re.DOTALL)

    refined_question = json.loads(match.group(0))

    if check_format(refined_question.get('question', '')):
        print("Successfully refined question")
        return refined_question
    else:
        print("Warning: Refinement did not add A, B, C, D options")
        return question_data  
    

input_file = 'generated/train.json'
fixed_file = 'generated/fixed_train.json'
data = load_json_file(input_file)
incorrect_indices = find_incorrect_questions(data)

if incorrect_indices:
    print(f"Found {len(incorrect_indices)} questions in incorrect formats")

    backup_file = f"{input_file}.backup"
    save_json_file(data, backup_file)

    for item in tqdm(incorrect_indices, desc="Refining questions"):
        idx = item['index']
        original_question = data[idx]
        refined_question = refine(original_question)
        data[idx] = refined_question

    save_json_file(data, input_file)
    remaining_incorrect = find_incorrect_questions(data)
    if remaining_incorrect:
        print(f"Warning: {len(remaining_incorrect)} questions still have incorrect format")
    else:
        print("All questions now have the correct format!")
else:
    print("All questions are already in the correct format!")

# Save all (now correct) questions to fixed_train.json
# save_json_file(data, fixed_file)
print(f"All questions saved to {fixed_file}")
    