import json
import logging
import time

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load biến môi trường (nếu bạn lưu ACCESS_KEY / SECRET_KEY ở đây)
load_dotenv()

# Khởi tạo client Bedrock Runtime

bedrock = boto3.client("bedrock-runtime", region_name="ap-southeast-1")


def chat_with_claude(
    model_id: str, user_message: str, max_tokens: int = 512, temperature: float = 0.5
) -> str:
    """
    Gửi yêu cầu chat đến model Claude trên Bedrock.

    Args:
        model_id: ID của Claude model, ví dụ 'anthropic.claude-2'
        user_message: Nội dung câu hỏi hoặc prompt của user
        max_tokens: Số token tối đa model được phép generate
        temperature: Độ ngẫu nhiên của câu trả lời (0.0–1.0)

    Returns:
        Chuỗi text trả lời từ Claude
    """

    # Chuẩn hóa payload theo Messages API của Anthropic Claude
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": user_message}],
    }
    body = json.dumps(payload)

    try:
        response = bedrock.invoke_model(
            modelId=model_id,
            body=body,
            contentType="application/json",
            accept="application/json",
        )
        result = json.loads(response["body"].read())
        # Trả về text đầu tiên trong content array
        return result["content"][0]["text"]
    except ClientError as e:
        logging.error("Error when calling Claude: %s", e.response["Error"]["Message"])
        raise


if __name__ == "__main__":
    # Ví dụ sử dụng
    model_id = "apac.anthropic.claude-sonnet-4-20250514-v1:0"  # hoặc 'anthropic.claude-3-haiku-20240307-v1:0'
    prompt = "Xin chào Claude, bạn có thể giới thiệu về Amazon Bedrock được không?"

    start_time = time.time()  # Bắt đầu đếm thời gian
    reply = chat_with_claude(model_id, prompt, max_tokens=5000, temperature=1)
    end_time = time.time()  # Kết thúc đếm thời gian

    print("Claude trả lời:")
    print(reply)
    print(f"Thời gian phản hồi: {end_time - start_time:.2f} giây")
