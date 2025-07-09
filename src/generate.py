"""
Generate initial legal QA data by utilizing seed questions from seed.json and legal knowledge from the reference directory.
Uses Claude 4.0 from Amazon Bedrock API.

python src/generate.py --nums 5 --cores 1 --suffix test
"""
import json
import argparse
import os
import tqdm
import multiprocessing
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument('--cores',   default=16, type=int)
parser.add_argument('--nums',    default=1, type=int)
parser.add_argument('--suffix',  default=None, type=str)
args = parser.parse_args()

CONTROL = """
Bạn được cung cấp một câu hỏi và đáp án về lĩnh vực pháp luật ở định dạng JSON. Trường instruction hướng dẫn cách trả lời, trường question chứa câu hỏi, trường answer chứa đáp án.

{JSON}

Bây giờ, dựa trên dữ liệu văn bản pháp luật, bạn muốn tạo câu hỏi tương tự. Hãy trả lời dưới dạng JSON với trường type là "hình sự" hoặc "dân sự".
"""

GENERATE = """
Bạn được cung cấp một câu hỏi và đáp án về lĩnh vực pháp luật ở định dạng JSON. Trường instruction hướng dẫn cách trả lời, trường question chứa câu hỏi, trường answer chứa đáp án.

{JSON}

Dưới đây là nội dung một văn bản pháp luật. Hãy dựa vào đó, giữ nguyên instruction, tạo một câu hỏi và đáp án mới theo định dạng JSON tương tự.
Thêm trường reasoning (giải thích quá trình suy luận ra đáp án) và trường reference (từ điển các điều luật liên quan).
Hãy thay đổi tên riêng, địa danh, doanh nghiệp để đảm bảo ẩn danh. Không lặp lại nguyên văn nội dung văn bản.
Đáp án phải đúng định dạng như instruction yêu cầu.

{DOCS}
"""

def generate(prompt):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    messages = [
        {"role": "system", "content": "Bạn là chuyên gia pháp luật."},
        {"role": "user", "content": prompt},
    ]

    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=messages,
        temperature=0.7,
        max_tokens=1024,
    )
    return response.choices[0].message.content.strip()

    
def tojson(reply):
    reply = reply.strip()
    if reply.startswith("```json"):
        reply = reply[7:]
    if reply.endswith("```"):
        reply = reply[:-3]
    return json.loads(reply.strip())

def solve(seed):
    try:
        ctrl = CONTROL.format(JSON=json.dumps(seed, ensure_ascii=False, indent=4))
        typ_json = generate(ctrl)
        typ = tojson(typ_json).get("type", "")
        # Đọc nội dung từ 0.txt
        with open("src/reference/0.txt", "r") as fr:
            doc = fr.read()
        if not doc.strip():
            return None

        gene = GENERATE.format(JSON=json.dumps(seed, ensure_ascii=False, indent=4), DOCS=doc)
        res_json = generate(gene)
        res = tojson(res_json)
        res["type"] = typ
        res["reference_file"] = "0.txt"
        return res
    except Exception as e:
        print("Error in solve:", e)
        return None
    
if __name__ == "__main__":
    with open(f"src/seed.json", "r") as fr:
        problems = json.load(fr)

    n = len(problems)
    print("#Seed Questions = ", n)

    inputs = []
    for i in range(args.nums):
        inputs.append(problems[i % n])

    start_time = time.time()
    with multiprocessing.Pool(processes=args.cores) as pool:
        res = pool.map(solve, inputs)

    results = []
    path = f"data/GEN{'-' + args.suffix if args.suffix is not None else ''}.json"
    try:
        with open(path, "r") as fr:
            results = json.load(fr)
    except Exception:
        pass

    oks = 0
    for item in res:
        if item is None:
            continue
        results.append(item)
        oks += 1
    print(f"Time: {time.time() - start_time:.2f}s", f"OK: {oks}/{len(inputs)}")

    with open(path, "w") as fw:
        json.dump(results, fw, ensure_ascii=False, indent=4)