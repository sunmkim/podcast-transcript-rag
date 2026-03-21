# constants for AWS Bedrock Knowledge Base
BEDROCK_KB_NAME = "podcast-transcripts-kb"
BEDROCK_KB_CHUNK_SIZE = 512
KNOWLEDGEBASE_ID = "FEYREV4B6D"

# constants for S3 Vectors
BEDROCK_VECTOR_BUCKET = "podcast-transcripts"
BEDROCK_VECTOR_INDEX_NAME = "podcast-transcripts-index"
VECTOR_DIMENSION = 1024

# define our embedding model
BEDROCK_EMBEDDING_MODEL = "amazon.titan-embed-text-v2:0"

# define our evaluator model for RAGAS
BEDROCK_LLM_MODEL = "anthropic.claude-3-haiku-20240307-v1:0"
EVALUATOR_LLM_MODEL = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"

# set our reranker model
RERANKER_MODEL = "cohere.rerank-v3-5:0"