import boto3
from pprint import pprint
from typing import Dict, Any
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_aws import ChatBedrock
from langchain_aws.retrievers import AmazonKnowledgeBasesRetriever
from dotenv import load_dotenv
from .constants import (
    BEDROCK_LLM_MODEL, 
    KNOWLEDGEBASE_ID, 
    RERANKER_MODEL,
)

load_dotenv()


# define RAG template
template = """
    You are a helpful Chatbot assistant. You have the following context available to you:
    {context}

    Based on the above information, answer this question below.:
    {question}

    Only answer the question and don't add extra context in your answer.
"""

class RAG():
    def __init__(self, knowledgebase_id: str, model_kwargs: Dict[str, Any] = None, region_name: str = "us-east-1"):
        self.region = region_name
        self.knowledgebase_id = knowledgebase_id
        self.results_num = 7
        self.bedrock_client = boto3.client('bedrock-runtime', region_name=self.region)
        if not model_kwargs:
            self.model_kwargs = { 
                "max_tokens": 2048,
                "temperature": 0.0,
                "top_k": 250,
                "top_p": 1,
                "stop_sequences": ["\n\nHuman"],
            }
        else:
            self.model_kwargs = model_kwargs
        
        # initialize llm
        self.llm = ChatBedrock(
            client=self.bedrock_client,
            model_kwargs=model_kwargs,
            model_id=BEDROCK_LLM_MODEL,
        )
        # instantiate Bedrock Knowledge Base; use semantic search
        self.retriever = AmazonKnowledgeBasesRetriever(
            knowledge_base_id=self.knowledgebase_id,
            region_name=self.region,
            retrieval_config={
                "vectorSearchConfiguration": {
                    "numberOfResults": self.results_num, 
                    "overrideSearchType": "SEMANTIC", # semantic search
                    "rerankingConfiguration": {
                        "type": "BEDROCK_RERANKING_MODEL",
                        # use Cohere reranking model
                        "bedrockRerankingConfiguration": {
                            "modelConfiguration": {
                                "modelArn": f'arn:aws:bedrock:{self.region}::foundation-model/{RERANKER_MODEL}',
                            },
                            "metadataConfiguration": {
                                "selectionMode": "SELECTIVE",
                                "selectiveModeConfiguration": {
                                    "fieldsToInclude": [
                                        {"fieldName": "utterance_text"}
                                    ]
                                }
                            },
                            "numberOfRerankedResults": self.results_num
                        }
                    }
                }
            }
        )

        # set prompt template
        self.prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=template,
        )

    
    def init_rag_chain(self):
        # define rag chain
        self.chain = (
            RunnableParallel({"context": self.retriever, "question": RunnablePassthrough()})
            .assign(response = self.prompt | self.llm | StrOutputParser())
            .pick(["response", "context"])
        )

    def invoke(self, user_question: str) -> Dict:
        answer = self.chain.invoke(user_question)
        return answer


def main(knowledgebase_id: str):
    rag = RAG(knowledgebase_id)
    question = "What's the significance of tariffs in US-Canada relationship?"

    rag.init_rag_chain()
    answer = rag.invoke(question)

    print("Question:\n", question, "\n")
    print("Answer:\n", answer['response'])


if __name__ == "__main__":
    main(KNOWLEDGEBASE_ID)