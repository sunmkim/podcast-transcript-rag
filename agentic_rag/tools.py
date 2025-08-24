from dotenv import load_dotenv
from langchain_tavily import TavilySearch

load_dotenv()

# tool for web-searching with Tavily
tavily_tool = TavilySearch(
    max_results=3,
    topic="general"
)