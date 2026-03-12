import boto3
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_aws import ChatBedrock
from langchain_aws.retrievers import AmazonKnowledgeBasesRetriever
from dotenv import load_dotenv
from constants import (
    BEDROCK_LLM_MODEL,
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


def main(knowledgebase_id: str):
    bedrock_client = boto3.client('bedrock-runtime', region_name="us-east-1")
    model_kwargs =  { 
        "max_tokens": 2048,
        "temperature": 0.0,
        "top_k": 250,
        "top_p": 1,
        "stop_sequences": ["\n\nHuman"],
    }

    # initialize llm
    llm = ChatBedrock(
        client=bedrock_client,
        model_kwargs=model_kwargs,
        model_id=BEDROCK_LLM_MODEL,
    )
    
    # instantiate our Bedrock Knowledge Base
    retriever = AmazonKnowledgeBasesRetriever(
        knowledge_base_id=knowledgebase_id,
        retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 3}},
    )

    # set prompt template
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=template,
    )

    chain = (
        RunnableParallel({"context": retriever, "question": RunnablePassthrough()})
        .assign(response = prompt | llm | StrOutputParser())
        .pick(["response", "context"])
    )

    user_question = "What did Wayne Gretzky do that made Canadians dislike him?"
    answer = chain.invoke(user_question)

    print("Question:\n", user_question, "\n")
    print("Answer:\n", answer['response'])

if __name__ == "__main__":
    knowledgebase_id = "OILFBSFZW0"
    main(knowledgebase_id)