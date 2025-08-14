from dotenv import load_dotenv
from langchain.tools.retriever import create_retriever_tool
from langchain_tavily import TavilySearch
from functions import load_documents
from SemanticSearchRetriever import SemanticSearchRetriever

load_dotenv()

# load in raw documents
lc_documents = load_documents('data/data.json')

# create retriever for semantic search
retriever = SemanticSearchRetriever(
    documents=lc_documents, 
    k=5
)

# define tools
# tool for retrieval on Elasticsearch vector store
retriever_tool = create_retriever_tool(
    retriever,
    "es_retriever",
    "Retrieves documents from Elasticsearch vector store"
)

# tool for web-searching with Tavily
tavily_tool = TavilySearch(
    max_results=3
)