# Agentic RAG

**Goal**

Create an agentic RAG pipeline that with an agent that has 2 tools available:
1. A semantic search retriever to the vector store
2. Web-search tool using Tavily.

## LangGraph Workflow

![Workflow](../agent_workflow.png)

The agent is designed to do the following:

### Retrieval
Since we assume that most queries from the user will be based on the content of the podcast, the first step of the agentic workflow is always to run the retrieval first. 

### Router
Second, once documents based on the query are retrieved, we use LLM as a judge to determine whether the retrieved documents are relevant to the user query. As we see above, there are two possible paths the agent can take after `evaluate_docs` step. If the documents are indeed relevant, then we simply generate the answer using the retrieved documents and a prompt template to provide to the user.

### Tavily Tool

If the documents were NOT deemed relevant and useful to answer the query, then we call web-search using Tavily and Tavily will search the web for us to get the right answer to the query.