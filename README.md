# RAG on Podcast Transcripts

Directory:

```
├── rag
│   ├── KnowledgeBase.py
│   ├── S3Vectors.py
│   ├── constants.py
│   ├── create_knowledge_base.py
│   ├── rag.py
│   └── README.md
├── infra
│   ├── main.tf
│   ├── outputs.tf
│   ├── variables.tf
│   └── README.md
├── data
│   ├── raw_data
│   │   ├── the_daily_03_13_2025.docx
│   │   └── the_daily_03_19_2026.docx
│   ├── data_processing.ipynb
│   ├── 03_13_2025.json
│   ├── 03_19_2026.json
│   └── README.md
├── evals
│   ├── evaluation.py
│   └── eval_datasets.py
├── requirements.txt
└── README.md
```

**Goal**

As an avid listener of The Daily podcast from the New York Times, I had an initial idea where I wanted to create some kind of a chatbot that could answer questions about the content of The Daily episodes based on the podcast transcript. This naturally lends itself to a RAG project.

This RAG system is deveolped on top of AWS Bedrock services, mainly Knowledge Base and S3 Vectors.


## How to use

You can access the RAG application (created with Streamlit) at "". Select an episode from the dropdown options on the left.

## Semantic Search using S3 Vectors

The retrieveal step of the RAG process is being handled by an AWS S3 Vectors, which is a cloud object store with native support to store and query vectors. The embedding model being used is `amazon.titan-embed-text-v2:0`. We created the Bedrock Knowledge Base using the vector index from  S3 Vectors.

At a high-level, the semantic search does the following:
1) Embeds the text into vectors and stores them
2) Creates an index (using cosine similarity)
3) Creates the Knowledge Base

The Knowledge Base object handles the retrieval with just a few configurations. Each episode is using its own Knowledge Base in AWS.