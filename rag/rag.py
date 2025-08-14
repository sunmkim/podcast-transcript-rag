import json
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from SemanticSearch import Search
from dotenv import load_dotenv


load_dotenv()

# define RAG template
template = """
    You are a helpful Chatbot assistant. You have the following information available to you:
    {information}

    Based on the above information, answer this question:
    {user_question}
"""


def main():
    rag_prompt_template = PromptTemplate(
        input_variables=["information", "user_question"],
        template=template,
    )

    # initialize llm
    llm = ChatOpenAI(
        temperature=0.3,
        model_name="gpt-3.5-turbo"
    )
    
    # initialize embedding model
    MODEL_NAME = "all-mpnet-base-v2"
    ssearch = Search(MODEL_NAME, "podcast_transcript")

    # read in data from json file
    print('Read in data')
    with open('data/data.json', 'rt') as f_in:
        docs_raw = json.load(f_in)

    # turn utterances into vector and store them
    ssearch.add_documents_to_index(docs_raw)

    # perform semantic search with Elasticsearch
    user_question = "Why are Canadians angry at the United States?"
    retrieval_info = ssearch.semantic_search(user_question)

    # inject results from semantic search into prompt template
    chain = rag_prompt_template | llm | StrOutputParser()
    response = chain.invoke(input={
        "information": retrieval_info, 
        "user_question": user_question
    })
    print(response)

if __name__ == "__main__":
    main()