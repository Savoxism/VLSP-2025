import os
import json
import boto3
import logging
from dotenv import load_dotenv

load_dotenv()
bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

def generate_text(
    model_id: str,
    prompt: str,
    max_tokens: int = 512,
    temperature: float = 0.7
) -> str:
    # Chuẩn bị payload cho text generation
    body = json.dumps({
        "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
        "max_tokens_to_sample": max_tokens,
        "temperature": temperature
    })
    try:
        # Gọi API
        response = bedrock.invoke_model(
            modelId=model_id,
            body=body,
            contentType="application/json",
            accept="application/json"
        )
        # Đọc và parse kết quả
        model_response = json.loads(response["body"].read())
        # Lấy chuỗi sinh ra
        return model_response["results"][0]["outputText"]
    except Exception as e:
        logging.error("Error when generating text: %s", e)
        raise

if __name__ == "__main__":
    model_id = "us.anthropic.claude-sonnet-4-20250514-v1:0"
    prompt = "Viết một đoạn văn ngắn giới thiệu về AI và ứng dụng của nó trong y tế."
    text = generate_text(
        model_id=model_id,
        prompt=prompt,
        max_tokens=256,
        temperature=0.5
    )
    print("Generated text:\n", text)
