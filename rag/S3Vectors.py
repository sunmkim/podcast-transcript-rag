import json
import boto3
import logging
from dotenv import load_dotenv
from typing import List, Dict
from constants import VECTOR_DIMENSION, BEDROCK_EMBEDDING_MODEL
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class S3Vectors():
    def __init__(self, embedding_model: str = BEDROCK_EMBEDDING_MODEL, region: str = "us-east-1"):
        self.region = region
        self.embedding_model = embedding_model
        self.bedrock_runtime_client = boto3.client('bedrock-runtime', region_name=region)
        self.s3_vectors_client = boto3.client("s3vectors", region_name=self.region)

    def create_index(self, index_name: str, vector_bucket: str) -> str:
        """
        Create S3 vector index for storing embeddings.
        
        Args:
            index_name (str): Name of the vector index
            vector_bucket (str): S3 bucket for vector storage
        
        Returns:
            str: Index ARN
        """

        # check that index doesn't already exist
        logger.info(f"Checking for S3 vector index: {index_name}")
        try:
            response = self.s3_vectors_client.get_index(
                vectorBucketName=vector_bucket,
                indexName=index_name,
            )
            index_arn = response["index"]["indexArn"]
            logger.info(f"Index '{index_name}' already exists. Skipping index creation.")
            return index_arn
        except self.s3_vectors_client.exceptions.NotFoundException as e:
            # create index if it doesn't already exist
            resp = self.s3_vectors_client.create_index(
                vectorBucketName=vector_bucket,
                indexName=index_name,
                dimension=VECTOR_DIMENSION,
                distanceMetric="cosine",
                dataType="float32"
            )
            index_arn = resp["indexArn"]
            logger.info(f"✓ Vector index created: {index_arn}")
            return index_arn
        except Exception as err:
            logger.error(f"Error creating index: {err}")
            raise
    
    def convert_to_vector(self, text: str, embedding_model: str = BEDROCK_EMBEDDING_MODEL) -> List[float]:
        """
        Convert text to vector embedding using Amazon Bedrock Titan embedding model.
        
        Args:
            text (str): Text to embed
        
        Returns:
            List[float]: Vector embedding
        """
        try:
            bedrock_runtime_client = boto3.client('bedrock-runtime')

            # Call Bedrock embedding model
            response = bedrock_runtime_client.invoke_model(
                modelId=embedding_model,
                body=json.dumps({"inputText": text}),
            )
            # Parse response
            response_body = json.loads(response['body'].read().decode('utf-8'))
            return response_body['embedding']
                    
        except Exception as err:
            logger.error(f"Error converting text to vector: {err}")
            raise


    def upload_vectors_to_s3(self, data: List[Dict], vector_bucket: str, index_name: str):
        """
        Embed podcast utterances and upload vectors to S3 Vectors.
        
        Args:
            data (List[Dict]): Podcast data with speaker and utterance
            vector_bucket (str): S3 vector bucket name
            index_name (str): Name of the S3 vector index
        """
        try:            
            logger.info(f"Embedding and uploading {len(data)} utterances to S3 Vectors...")
            
            vectors_to_upload = []
            successful_uploads = 0
            
            for idx, item in enumerate(data):
                try:
                    utterance = item.get('utterance', '')
                    speaker = item.get('speaker', 'unknown')
                    
                    if not utterance:
                        logger.warning(f"Skipping item {idx}: empty utterance")
                        continue
                    
                    # Embed the utterance
                    vector = self.convert_to_vector(utterance)

                    # Create vector object with metadata
                    vector_obj = {
                        "key": f"utterance-{idx}",
                        "data": {"float32": vector},
                        "metadata": {
                            "speaker": speaker,
                            "utterance_text": utterance,
                        }
                    }
                    
                    vectors_to_upload.append(vector_obj)
                    logger.info(f"[{idx+1}/{len(data)}] Embedded utterance by {speaker}")
                    
                    # Upload vectors in batches of 100 to avoid overwhelming the API
                    if (idx + 1) % 100 == 0 or (idx + 1) == len(data):
                        batch_size = len(vectors_to_upload)
                        logger.info(f"Uploading batch of {batch_size} vectors to S3 Vectors...")
                        
                        try:
                            response = self.s3_vectors_client.put_vectors(
                                vectorBucketName=vector_bucket,
                                indexName=index_name,
                                vectors=vectors_to_upload
                            )
                            logger.info(f"Response from `put_vectors`:\n {response}")
                            successful_uploads += batch_size
                            logger.info(f"✓ Successfully uploaded {batch_size} vectors")
                            vectors_to_upload = []  # Clear batch for next upload
                        except Exception as upload_err:
                            logger.error(f"Error uploading vector batch: {upload_err}")
                            raise
                
                except Exception as err:
                    logger.error(f"Error processing item {idx}: {err}")
                    continue
            
            logger.info(f"✓ Completed embedding and uploading {successful_uploads} utterances to S3 Vectors")
        
        except Exception as err:
            logger.error(f"Error uploading vectors: {err}")
            raise