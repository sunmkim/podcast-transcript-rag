import os, json
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import ToolNode
from langchain.tools.retriever import create_retriever_tool
from tools import tavily_tool
from prompt_templates import RAG_TEMPLATE, EVALUATION_TEMPLATE
from schema import AgentState, GradeDocuments
from SemanticSearchRetriever import SemanticSearchRetriever
load_dotenv()


def load_documents(datapath: str) -> list:
    """ Load raw documents json file into Document objects """
    documents = []

    with open(datapath, 'rt') as f_in:
        docs_raw = json.load(f_in)

    for doc in docs_raw:
        document = Document(
            page_content=doc["utterance"],
            metadata={ "speaker": doc["speaker"] }
        )
        documents.append(document)
    print(f"{len(documents)} documents loaded!\n")
    return documents

# instantiate retriever
lc_documents = load_documents('data/data.json')
rag_retriever = SemanticSearchRetriever(documents=lc_documents, k=5)

# instantiat our LLM
llm = init_chat_model(model="gpt-5", model_provider="openai")


def retrieval(state: AgentState):
    """ Retrieve documents from Elasticsearch store knowledge base """

    # get last human message to fetch user query
    messages = state["messages"]
    query = messages[-1].content if hasattr(messages[-1], "content") else str(messages[-1])

    retriever_tool = create_retriever_tool(
        rag_retriever,
        "retrieve_elasticsearch",
        "Search and return relevant documents from Elasticsearch.",
    )
    fetched_documents = retriever_tool.invoke({"query": query})
    messages = [AIMessage(content=fetched_documents)]
    return {"messages": messages}


def evaluate_docs(state: AgentState) -> dict:
    """ Determine whether the retrieved documents are relevant to the question. """
    question = state["messages"][0].content
    context = state["messages"][-1].content

    # inject question and context to prompt template and call LLM-as-judge
    prompt = EVALUATION_TEMPLATE.format(context=context, question=question)
    response = (
        llm.with_structured_output(GradeDocuments).invoke(
            [{"role": "user", "content": prompt}]
        )
    )
    score = response.binary_score

    # route to next node depending on LLM's retrieval evaluation
    if score == 'yes':
        print("Next: generate_answer")
        return { "next": "generate_answer" }
    else:
        print("Next: websearch")
        return { "next": "websearch" }
    

def generate_answer(state: AgentState):
    """ Generate answer based on information context and user query """
    user_question = state["messages"][0].content
    information = state["messages"][-1].content

    # define RAG template
    rag_prompt_template = PromptTemplate(
        input_variables=["information", "user_question"],
        template=RAG_TEMPLATE,
    )
    # define our LLM that generates RAG response
    chain = rag_prompt_template | llm | StrOutputParser()

    # generate answer by injecting relevant context from retrieval
    response = chain.invoke(input={
        "information": information, 
        "user_question": user_question
    })

    return {"messages": [AIMessage(content=response)]}


def main():        
    # create our graph workflow
    workflow = StateGraph(AgentState)

    # define nodes
    workflow.add_node("retrieval", retrieval)
    workflow.add_node("evaluate_docs", evaluate_docs)
    workflow.add_node("websearch", ToolNode([tavily_tool]))
    workflow.add_node("generate_answer", generate_answer)
    workflow.set_entry_point("retrieval")
    workflow.set_finish_point("generate_answer")

    # define edges
    workflow.add_edge(START, "retrieval")
    workflow.add_edge("retrieval", "evaluate_docs")
    workflow.add_conditional_edges(
        "evaluate_docs", 
        lambda state: state["next"], 
        {
            "generate_answer": "generate_answer",
            "websearch": "websearch",
        }
    )
    workflow.add_edge("websearch", "generate_answer")
    workflow.add_edge("generate_answer", END)

    graph = workflow.compile()

    png_graph = graph.get_graph().draw_mermaid_png()
    with open("agent_workflow.png", "wb") as f:
        f.write(png_graph)
    print(f"Graph saved as 'agent_workflow.png' in {os.getcwd()}")

    # call agent and pretty print the results
    user_query = input("Enter your query: ")
    messages = [HumanMessage(content=user_query)]
    messages = graph.invoke({"messages": messages})
   
    question = messages['messages'][0]
    answer = messages['messages'][-1] 
    question.pretty_print()
    answer.pretty_print()


if __name__ == '__main__':
    main()