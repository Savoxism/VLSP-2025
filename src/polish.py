"""
Enhances the generated data by validating legal references and optimizing reasoning paths.
Uses OpenAI API (DeepSeek or OpenAI compatible).

python src/polish.py --nums 3 --cores 1 --suffix test
"""
import json
import argparse
import os
import multiprocessing
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument('--cores',   default=16, type=int)
parser.add_argument('--nums',    default=1000000, type=int)
parser.add_argument('--suffix',  default=None, type=str)
args = parser.parse_args()

REFINE = """
You are given a JSON dictionary containing several legal articles. The field is a dictionary, where the Key is the legal article referenced in the reasoning process, and the Value is the content of the legal article.

{JSON}

The content of the articles may be incorrect. Please correct the Value to match the correct content for each Key, and return the result in JSON format only, with no extra explanation.
"""

CORRECT = """
You are given a legal question and answer in JSON format. The 'instruction' field guides how to answer, the 'question' field contains the question, the 'answer' field contains the answer, the 'reference' field contains the legal articles, and 'reasoning' contains the reasoning process.

{JSON}

The reasoning process and answer may have issues. Please improve the reasoning and answer based on the question and legal articles.
If the reasoning and answer are already correct, just return the original JSON. Otherwise, modify the 'reasoning' and 'answer' fields and return the updated JSON only, with no extra explanation.
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
    reply = reply.replace("'", '"')
    if reply.startswith("```json"):
        reply = reply[7:-3]
    if reply.startswith("```"):
        reply = reply[3:-3]
    return json.loads(reply.strip())

def toprob(item):
    return {
        "instruction": item["instruction"],
        "reference": item["reference"],
        "question": item["question"],
        "reasoning": item["reasoning"],
        "answer": item["answer"]
    }

def solve(data):
    try:
        ref = REFINE.format(JSON=json.dumps(data["reference"], ensure_ascii=False, indent=4))
        new_ref = tojson(generate(ref))
        if data["reference"] != new_ref:
            print("Diff =>", data["reference"], new_ref)
            data["reference_old"] = data["reference"]
            data["reference"] = new_ref
            cor = CORRECT.format(JSON=json.dumps(toprob(data), ensure_ascii=False, indent=4))
            new_item = tojson(generate(cor))
            data["answer_old"] = data["answer"]
            data["reasoning_old"] = data["reasoning"]
            data["answer"] = new_item["answer"]
            data["reasoning"] = new_item["reasoning"]
        return data
    except Exception as err:
        print(err)
        return None

if __name__ == "__main__":
    ori_path = f"data/GEN{'-' + args.suffix if args.suffix is not None else ''}.json"
    tar_path = f"data/POL{'-' + args.suffix if args.suffix is not None else ''}.json"

    # Check if the original file exists
    with open(ori_path, "r") as fr:
        data = json.load(fr)
    n = len(data)
    print("#Data = ", len(data))

    inputs = []
    for i in range(min(args.nums, n)):
        inputs.append(data[i])

    start_time = time.time()
    with multiprocessing.Pool(processes=args.cores) as pool:
        res = pool.map(solve, inputs)

    results = []
    oks = 0
    for item in res:
        if item is None:
            continue
        results.append(item)
        oks += 1
    print(f"Time: {time.time() - start_time:.2f}s", f"OK: {oks}/{len(inputs)}")

    with open(tar_path, "w") as fw:
        json.dump(results, fw, ensure_ascii=False, indent=4)