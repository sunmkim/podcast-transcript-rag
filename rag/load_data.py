import boto3
import json
from typing import List

class Embedder():
    def __init__(self, model_name: str, region: str = "us-east-1"):
        self.model_name = model_name
        self.bedrock_client = boto3.client("bedrock-runtime", region_name=region)
    
    def embed_text(text: str) -> List[float]:
        pass
    
