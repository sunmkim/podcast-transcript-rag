import boto3
import logging
from dotenv import load_dotenv
from typing import Any, List, Dict
from pathlib import Path
from constants import VECTOR_DIMENSION, RERANKER_MODEL, BEDROCK_EMBEDDING_MODEL
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class KnowledgeBase():
    def __init__(self, name: str, embedding_model: str = BEDROCK_EMBEDDING_MODEL, reranker_model: str = RERANKER_MODEL, region: str = "us-east-1"):
        self.name = name
        self.region = region
        self.embedding_model = embedding_model
        self.reranker_model = reranker_model
        self.bedrock_runtime_client = boto3.client('bedrock-agent-runtime', region_name=region)
        self.bedrock_agent_client = boto3.client('bedrock-agent', region_name=region)
        self.kb_id = None # set id for knowledge base when created in AWS Bedrock


    def create_knowledge_base(self, vector_index_arn: str, role_arn: str) -> str:
        """
        Creates a knowledge base with Amazon S3 Vectors.
        
        Args:
            vector_index_arn (str): ARN of the S3 vector index
            role_arn (str): IAM role ARN for Bedrock service
        
        Returns:
            str: AWS Bedrock knowledge base ID
        """
        try:
            logger.info(f"Creating Bedrock Knowledge Base: {self.name}")
            
            resp = self.bedrock_agent_client.create_knowledge_base(
                name=self.name,
                description="Knowledge base for podcast transcripts stored in S3 Vectors",
                roleArn=role_arn,
                knowledgeBaseConfiguration={
                    'type': 'VECTOR',
                    'vectorKnowledgeBaseConfiguration': {
                        'embeddingModelArn': f'arn:aws:bedrock:{self.region}::foundation-model/{self.embedding_model}',
                        'embeddingModelConfiguration': {
                            'bedrockEmbeddingModelConfiguration': {
                                'dimensions': VECTOR_DIMENSION,
                                'embeddingDataType': 'FLOAT32'
                            }
                        }
                    },
                },
                storageConfiguration={
                    's3VectorsConfiguration': {
                        'indexArn': vector_index_arn
                    },
                    'type': 'S3_VECTORS'
                }
            )
            knowledge_base_id = resp['knowledgeBase']['knowledgeBaseId']
            logger.info(f"✓ Knowledge Base created: {knowledge_base_id}")
            self.kb_id = knowledge_base_id
            return knowledge_base_id
        
        except Exception as err:
            logger.error(f"Error creating knowledge base: {err}")
            raise
    
    def query(self, query_text: str, kb_id: str, num_results: int = 7) -> List[Dict[str, Any]]:
        """
        Queries the knowledge base using the retrieve API.

        Args:
            query_text (str): The text query to search for
            kb_id (str): The knowledge base ID to query
            num_results (int): Number of results to return (default 5)

        Returns:
            List[Dict[str, Any]]: List of retrieval results with content, location, metadata, and score
        """
        try:
            logger.info(f"Querying knowledge base {kb_id} with: {query_text}")
            resp = self.bedrock_runtime_client.retrieve(
                knowledgeBaseId=kb_id,
                retrievalQuery={
                    "text": query_text
                },
                retrievalConfiguration={
                    "vectorSearchConfiguration": {
                        "numberOfResults": num_results,
                        "overrideSearchType": "SEMANTIC", # semantic search
                        "rerankingConfiguration": {
                            # apply reranking with Cohere reranking model
                            "type": "BEDROCK_RERANKING_MODEL",
                            "bedrockRerankingConfiguration": {
                                "modelConfiguration": {
                                    "modelArn": f'arn:aws:bedrock:{self.region}::foundation-model/{self.reranker_model}',
                                },
                                "metadataConfiguration": {
                                    "selectionMode": "SELECTIVE",
                                    "selectiveModeConfiguration": {
                                        "fieldsToInclude": [
                                            {"fieldName": "utterance_text"}
                                        ]
                                    }
                                },
                                "numberOfRerankedResults": num_results
                            }
                        }
                    }
                }
            )
            results = resp.get("retrievalResults", [])
            logger.info(f"Retrieved {len(results)} results")
            return results
        except Exception as err:
            logger.error(f"Error querying knowledge base: {err}")
            raise