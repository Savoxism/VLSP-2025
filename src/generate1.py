from dotenv import load_dotenv
from tqdm import tqdm
import os, json, random, re, glob
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

OUTPUT_FILE = "gen.json"
SEED_FILES_PATH = "src/seed_files"
REFERENCE_PATH = "src/reference"

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

2) Một văn bản pháp luật để trích dẫn. Bạn có nhiệm vụ tạo ra MỘT vấn đề mới dưới dạng JSON, bao gồm toàn bộ các trường như mẫu (id luôn để -1). Đảm bảo rằng:
- `instruction` giữ nguyên
- Nội dụng `question` & `answer` phải đa dạng và khác biệt so với mẫu
- Trường `references` BẮT BUỘC trích đúng các điều luật từ văn bản pháp luật đính kèm, đảm bảo chính xác tên điều và nội dung điều.

Chỉ xuất ra một JSON object, không thêm bất kỳ chú thích hay văn bản nào khác. Nhắc lại vô cùng quan trọng là câu hỏi phải dựa vào các điều luật trong văn bản đính kèm.
{DOCUMENT}
"""

def clean_json_response(raw_text):
    match = re.search(r'(\{.*\})', raw_text, re.DOTALL)
    if match:
        raw_text = match.group(1)

    if raw_text.strip().startswith('['):
        try:
            parsed = json.loads(raw_text)
            if isinstance(parsed, list) and len(parsed) > 0:
                return parsed[0]
        except:
            pass

    try:
        return json.loads(raw_text)
    except Exception as e:
        print(f"Lỗi khi parse JSON: {e}")
        return {"error": "Invalid JSON", "raw": raw_text}
    
def chat(prompt: str) -> str:
    messages = [
        {"role": "system", "content": "Bạn là chuyên gia pháp luật. Trả lời chỉ bằng JSON không có thêm bất kỳ text nào khác."},
        {"role": "user", "content": prompt},
    ]

    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=messages,
        temperature=0.7,
        max_tokens=1024,
    )
    return response.choices[0].message.content.strip()

def get_random_seed_problem():
    seed_files = [f for f in os.listdir(SEED_FILES_PATH) if f.endswith('.json')]
    if not seed_files:
        raise ValueError(f"Không tìm thấy file JSON nào trong {SEED_FILES_PATH}")
    
    random_file = random.choice(seed_files)
    file_path = os.path.join(SEED_FILES_PATH, random_file)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        seed_data = json.load(f)
    
    # Nếu là list, chọn ngẫu nhiên một phần tử
    if isinstance(seed_data, list):
        return random.choice(seed_data)
    return seed_data

def get_random_reference_document():
    reference_files = glob.glob(os.path.join(REFERENCE_PATH, '*.txt'))
    if not reference_files:
        raise ValueError(f"Không tìm thấy file văn bản nào trong {REFERENCE_PATH}")
    
    random_file = random.choice(reference_files)
    with open(random_file, 'r', encoding='utf-8') as f:
        reference_content = f.read()
    
    return reference_content, os.path.basename(random_file)


def generate_single_example(output_path=""):
    # 1. Lấy seed problem ngẫu nhiên
    seed = get_random_seed_problem()
    print(f"Đã chọn seed problem với instruction: {seed.get('instruction', 'N/A')}")
    
    # 2. Lấy văn bản pháp luật ngẫu nhiên
    reference_doc, reference_filename = get_random_reference_document()
    print(f"Đã chọn văn bản pháp luật: {reference_filename}")
    
    # 3. Tạo prompt và gọi API
    prompt = PROMPT.format(
        JSON=json.dumps(seed, ensure_ascii=False, indent=2),
        DOCUMENT=reference_doc
    )
    print("Đang tạo mẫu mới...")
    raw = chat(prompt=prompt)
    
    result = clean_json_response(raw)
    if "error" not in result:
        result["id"] = -1
        # result["reference_file"] = reference_filename
    
    try:
        with open(output_path, 'r', encoding='utf-8') as fin:
            existing_data = json.load(fin)
            # Nếu file đã tồn tại, thêm vào cuối và cập nhật ID
            if isinstance(existing_data, list):
                result["id"] = len(existing_data) + 1
                existing_data.append(result)
                results = existing_data
    
    except (FileNotFoundError, json.JSONDecodeError):
        # Nếu file không tồn tại hoặc rỗng, tạo mới
        results = [result]
    
    with open(output_path, 'w', encoding='utf-8') as fout:
        json.dump(results, fout, ensure_ascii=False, indent=2)
    
    print(f"Đã tạo mẫu và lưu vào {output_path}")
    return result

if __name__ == "__main__":
    generate_single_example(OUTPUT_FILE)