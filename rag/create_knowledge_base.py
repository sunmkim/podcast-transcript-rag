import os
import json
import boto3
import logging
from dotenv import load_dotenv
from typing import Any, List, Dict
from pathlib import Path
from constants import (
    BEDROCK_KB_NAME,
    BEDROCK_VECTOR_BUCKET,
    BEDROCK_VECTOR_INDEX_NAME,
    BEDROCK_EMBEDDING_MODEL, 
)
from KnowledgeBase import KnowledgeBase
from S3Vectors import S3Vectors
load_dotenv()


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



def load_podcast_data(data_file: str) -> List[Dict]:
    """
    Load podcast transcript data from JSON file.
    
    Args:
        data_file (str): Path to data.json
    
    Returns:
        List[Dict]: List of {speaker, utterance} dicts
    """
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"✓ Loaded {len(data)} utterances from {data_file}")
        return data
    
    except Exception as err:
        logger.error(f"Error loading data: {err}")
        raise



def main():
    """
    Main workflow to create Bedrock Knowledge Base from podcast transcripts:
    1. Create S3 vector index
    2. Load and embed podcast data from data.json
    3. Upload vectors to S3
    4. Create Bedrock Knowledge Base
    """
    try:
        logger.info("AWS Bedrock Knowledge Base Creation for Podcast Transcripts")
        
        # Configuration
        data_file = Path(__file__).parent.parent / "data" / "data.json"
        role_arn = os.getenv("BEDROCK_ROLE_ARN")
        
        # Validate configuration
        if not role_arn or role_arn == "":
            logger.error("ERROR: role_arn not configured. Set BEDROCK_ROLE_ARN environment variable.")
            raise ValueError("Missing BEDROCK_ROLE_ARN configuration")
        
        s3_vectors = S3Vectors()

        kb_client = KnowledgeBase(
            name=BEDROCK_KB_NAME,
            embedding_model=BEDROCK_EMBEDDING_MODEL
        )
        
        # Step 1: Create S3 vector index
        logger.info("\n[1/4] Creating S3 Vector Index")
        logger.info("-" * 70)
          
        index_arn = s3_vectors.create_index(
            index_name=BEDROCK_VECTOR_INDEX_NAME,
            vector_bucket=BEDROCK_VECTOR_BUCKET
        )
        
        # Step 2: Load podcast data
        logger.info("\n[2/4] Loading Podcast Data")
        logger.info("-" * 70)
        
        if not data_file.exists():
            raise FileNotFoundError(f"Data file not found: {data_file}")
        
        data = load_podcast_data(str(data_file))
        
        # Step 3: Embed and upload vectors
        logger.info("\n[3/4] Embedding Utterances and Uploading Vectors")
        logger.info("-" * 70)
        
        s3_vectors.upload_vectors_to_s3(
            data=data,
            vector_bucket=BEDROCK_VECTOR_BUCKET,
            index_name=BEDROCK_VECTOR_INDEX_NAME
        )
        
        # Step 4: Create Bedrock Knowledge Base
        logger.info("\n[4/4] Creating Bedrock Knowledge Base")
        logger.info("-" * 70)
        
        kb_id = kb_client.create_knowledge_base(
            vector_index_arn=index_arn,
            role_arn=role_arn
        )
        
        logger.info("\n" + "=" * 70)
        logger.info("✓ SUCCESS: Knowledge Base Creation Complete!")
        logger.info("=" * 70)
        logger.info(f"Knowledge Base ID: {kb_id}")
        logger.info(f"Vector Index ARN: {index_arn}")
        logger.info(f"Utterances Embedded: {len(data)}")
        logger.info("=" * 70)
        
        return kb_id
    
    except Exception as err:
        logger.error(f"\n✗ ERROR: {err}")
        raise


if __name__ == "__main__":
    main()
    # kb_client = KnowledgeBase(
    #     name=BEDROCK_KB_NAME,
    #     embedding_model=BEDROCK_EMBEDDING_MODEL
    # )
    # results = kb_client.query(
    #     query_text="Who is the new Prime Minister of Canada? Cite your source in the knowledge base.",
    #     kb_id="OILFBSFZW0"
    # )
    # print(results)