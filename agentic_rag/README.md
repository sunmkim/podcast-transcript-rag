# Agentic RAG

## LangGraph Workflow

![Workflow](../agent_workflow.png)

First step of the workflow is always to run the retrieval first.

## Tools

Web-search using Tavily


## Router
Using LLM-as-judge, we will determine whether the retrieved documents are relevant to the user query.
As we see above, there are two possible paths the agent can take after `evaluate_docs` step. 

If LLM deems the documents relevant, we simply generate the answer with the LLM and end. Else, we call web-search using Tavily and Tavily will search the web for us to get the answer for the query.