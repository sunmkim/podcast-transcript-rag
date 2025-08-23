# RAG with Elasticsearch

## Models

Embedding model to embed our text into vectors is `all-mpnet-base-v2`, and the LLM for answer generation is `gpt-3.5-turbo`.


## Chaining with Langchain

The RAG process first loads in all the data in `data/data.json`into Elasticsearch, runs a semantic search to fetch relevant documents, and then inject the results into a Langchain prompt template that is chained and invoked to `gpt-3.5-turbo` model. This will allow the LLM to give back our answer.