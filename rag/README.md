# RAG with Elasticsearch

## Models

Embedding model used to embed our text into vectors is `all-mpnet-base-v2`, and the LLM for answer generation is `gpt-3.5-turbo`.


## Chaining with Langchain

The RAG process first loads in all the data in `data/data.json`into Elasticsearch, runs a semantic search to fetch relevant documents, and then inject the results into a Langchain prompt template that is chained and invoked to `gpt-3.5-turbo` model. This will allow the LLM to give back our answer.

## Output

To test our RAG pipeline, we ask the question relevant to the podcast episode: Why are Canadians angry at the United States?

If the RAG pipeline was successful, then the LLM should be able to retrieve and summarize the relevant documents that answer the question about the podcast. And we see that it indeed does when we run `python rag/rag.py`:

```
ElasticSearch Client:
 {'name': 'cc05349b72d5', 'cluster_name': 'docker-cluster', 'cluster_uuid': 'dFOa0MkYRPO4ByPmXCcfrg', 'version': {'number': '8.4.3', 'build_flavor': 'default', 'build_type': 'docker', 'build_hash': '42f05b9372a9a4a470db3b52817899b99a76ee73', 'build_date': '2022-10-04T07:17:24.662462378Z', 'build_snapshot': False, 'lucene_version': '9.3.0', 'minimum_wire_compatibility_version': '7.17.0', 'minimum_index_compatibility_version': '7.0.0'}, 'tagline': 'You Know, for Search'}

Download all-mpnet-base-v2 model from HuggingFace
Read in data
Get vector embeddings

Question:
 Why are Canadians angry at the United States? 

Answer:
 Canadians are angry at the United States due to escalating rhetoric about Canadian sovereignty and tariff threats made by the American president, which has fueled anti-US and anti-Trump sentiment in Canada. This anger has led to Canadians booing the American national anthem at hockey games and has even caused Canadians to turn against figures like Wayne Gretzky, who is considered a national hero in Canada. The political climate and tensions between the two countries have contributed to Canadians feeling backed into a corner and becoming hostile towards the United States.
 ```

The Python code downloads the embedding model, reads in the raw json data, retrieves vector embeddings, then generates the answer based on our Elasticsearch results.