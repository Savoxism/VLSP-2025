import os, json, random
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

Chỉ xuất ra một JSON object, không thêm bất kỳ chú thích hay văn bản nào khác. Nhắc lại vô cùng quan trọng là câu hỏi phải dựa vào các điều luật trong văn bản đính kèm.
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
    prompt = PROMPT.format(
        JSON=json.dumps(seed_problem, ensure_ascii=False, indent=2),
        DOCUMENT=reference_document
    )

    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": "Bạn là chuyên gia pháp luật."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=1024,
    )
    return response.choices[0].message.content.strip()


seed = load_random_seed('src/seed_files')
reference_doc = load_random_reference('src/reference')
new_example = generate(seed, reference_doc)

# print(seed)

try:
    new_example_json = json.loads(new_example)
except json.JSONDecodeError:
    print("Invalid JSON", new_example)

with open('ex.json', 'w', encoding='utf-8') as f:
    json.dump(new_example_json, f, ensure_ascii=False, indent=2)