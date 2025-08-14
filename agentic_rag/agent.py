import os
import operator
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langchain_core.messages import AnyMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from tools import retriever_tool, tavily_tool

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

# define tools
tools = [retriever_tool, tavily_tool]

# bind tools to LLM
llm = ChatOpenAI(model="gpt-5", temperature=0.2, streaming=True, api_key=os.getenv("OPENAI_API_KEY"))
llm_with_tools = llm.bind_tools(tools)

# create our graph workflow
workflow = StateGraph(MessagesState)

# define nodes
tool_node = ToolNode(tools)
workflow.add_node("tools", tool_node)
workflow.add_node("rag", ...)
workflow.add_node("websearch", ...)

# define edges



# class Agent:
#     def __init__(self, model, tools, system=""):
#         self.system = system # system message
#         self.graph = self.build_and_compile_graph()
#         self.tools = { t.name: t for t in tools }
#         self.model = model.bind_tools(tools)

#     def build_and_compile_graph(self):
#         graph = StateGraph(AgentState)
#         graph.add_node("rag", self.call_rag)
#         graph.add_node("action", self.take_action)
#         graph.add_conditional_edges(
#             "llm",
#             ..., # function to determine whereto go after llm
#             { True: "action", False: END }
#         )
#         graph.add_edge("action", "llm")
#         graph.set_entry_point("llm")
#         compiled_graph = graph.compile()
#         return compiled_graph


#     def call_rag(self, state: AgentState):
#         messages = state["messages"]
#         if self.system:
#             messages = [SystemMessage(content=self.system)] + messages
#         message = self.model.invoke(messages)
#         return { 'messages': [message] }
    
#     def take_action(self, state: AgentState):
#         pass