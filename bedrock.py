import json
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import logging

load_dotenv()
bedrock = boto3.client("bedrock-runtime", region_name="ap-southeast-1")

def generate_text_embeddings(model_id: str, texts: list[str], input_type: str = "search_document"):
    body = json.dumps({
        "texts": texts,
        "input_type": input_type,
        # "truncate": "NONE",
        # "embedding_types": ["float"]
    })

    try:
        response = bedrock.invoke_model(
            modelId = model_id,
            body=body,
            contentType="application/json",
            accept="*/*"
        )

        return json.loads(response["body"].read())
    except ClientError as e:
        logging.error("Error when calling Cohere Embed: %s", e.response["Error"]["Message"])
        raise


model_id = "cohere.embed-english-v4"  # Or "cohere.embed-multilingual-v3"
texts = [
    "Hello world",
]

result = generate_text_embeddings(model_id, texts, input_type="search_document")
print("ID response:", result["id"])
print("Embedding vectors:")
for idx, vec in enumerate(result["embeddings"]):
    print(f" - Text {idx}: vector length {len(vec)}")