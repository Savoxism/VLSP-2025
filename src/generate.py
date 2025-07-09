import os, json, random, re
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

PROMPT = """
Bạn là chuyên gia pháp luật. Tôi sẽ đưa cho bạn:  
1) Một ví dụ vấn đề mẫu ở định dạng JSON, gồm các trường:  
   - id  
   - instruction (str): dạng câu hỏi 
   - question (str): nội dung câu hỏi  
   - answer (str): đáp án  
   - references (dict): các điều luật liên quan và nội dung của chúng  
   - reasoning_path (str): chuỗi mô tả quá trình suy luận  
{JSON}

2) Một văn bản pháp luật để trích dẫn. Bạn có nhiệm vụ tạo ra MỘT câu hỏi mới dưới dạng JSON, bao gồm toàn bộ các trường như mẫu. Đảm bảo rằng:
- id luôn để -1
- `instruction` giữ nguyên
- Nội dụng `question` & `answer` phải đa dạng và khác biệt so với mẫu
- Trường `references` BẮT BUỘC trích đúng các điều luật từ văn bản pháp luật đính kèm, đảm bảo chính xác tên điều và nội dung điều.

Chỉ xuất ra một JSON object, không thêm bất kỳ chú thích hay văn bản nào khác. Nhắc lại vô cùng quan trọng là câu hỏi phải dựa vào các điều luật trong văn bản đính kèm. Chỉ tạo ra 1 câu hỏi mới.
{DOCUMENT}
"""

def load_random_seed(folder_path):
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

def generate(seed_problem, reference_document):
    prompt = PROMPT.format(JSON=json.dumps(seed_problem, ensure_ascii=False, indent=2), DOCUMENT=reference_document)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(system_instruction="Bạn là chuyên gia pháp luật."),
        contents=prompt
    )
    text = response.text
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found")
    return json.loads(match.group(0))


seed = load_random_seed('src/seed_files')
reference_doc = load_random_reference('src/reference')
new_example = generate(seed, reference_doc)

with open('ex.json', 'w', encoding='utf-8') as f:
    json.dump(new_example, f, ensure_ascii=False, indent=2)

print('DONE')


'''
/Users/nguyenphuan/Documents/Github/VLSP-2025/venv/bin/python /Users/nguyenphuan/Documents/Github/VLSP-2025/src/generate.py
'''