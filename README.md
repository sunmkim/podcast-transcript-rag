# RAG on Podcast Transcripts

Directory:

```
├── rag
│   ├── rag.py
│   ├── SemanticSearch.py
│   └── README.md
├── agentic_rag
│   ├── agent.py
│   ├── SemanticSearchRetriever.py
│   ├── tools.py
│   ├── prompt_templates.py
│   ├── schema.py
│   └── README.md
├── data
│   ├── raw_data
│   │   └── the_daily_03_13_2025.docx
│   ├── data_processing.ipynb
│   ├── data.json
│   └── README.md
├── ollama-server
│   ├── docker-compose.yaml
│   ├── ollama.Dockerfile
│   ├── run_ollama.py
│   └── README.md
├── requirements.txt
└── README.md
```

**Goal**

As an avid listener of The Daily podcast from the New York Times, I had an initial idea where I wanted to create some kind of a chatbot that could answer questions about the content of The Daily episode based on the podcast transcript. This naturally lends itself to a RAG project.

I created 2 RAG projects based on the same knowledge base of data using ElasticSearch: one agentic RAG, and the other non-agentic RAG.


## Semantic Search using ElasticSearch

The retrieveal step of the RAG process is being handled by an Elasticsearch vector store running on a local server (not Elastic Cloud). The embedding model being used is `all-mpnet-base-v2`. The document search step of the RAG pipeline can be found in `rag/SemanticSearch.py`, and `agentic_rag/SemanticSearchRetriever.py`. These are nearly identical code. The only difference is that the latter was slightly modified in a wrapper to allow it to be used as a Langchain tool.

At a high-level, the semantic search does the following:
1) Embeds the text into vectors
2) Creates an index
3) Loads the documents into Elasticsearch vector store using the index.
4) Uses cosine similarity to search for relevant documents.


## How to run

Run the following to run Elasticsearch server:
```
docker run -it \
    --rm \
    --name elasticsearch \
    -p 9200:9200 \
    -p 9300:9300 \
    -e "discovery.type=single-node" \
    -e "xpack.security.enabled=false" \
    docker.elastic.co/elasticsearch/elasticsearch:8.4.3
```

You can run the agentic RAG pipeline by running `python agentic_rag/agent.py`, and the non-agentic rag by running `python rag/rag.py`