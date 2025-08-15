import json
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer


class SemanticSearchRetriever(BaseRetriever):
    documents: list[Document]
    k: int = 5
    url: str = 'http://localhost:9200'
    model_name: str = 'all-mpnet-base-v2'

    def _get_relevant_documents(self, query: str) -> list[Document]:
        """Return the first k documents from the list of documents"""
        index_name = "podcast_transcript"
        es_client = Elasticsearch(self.url)
        matching_documents = []

        print('ElasticSearch Client:\n', es_client.info(), '\n')
        print(f"Download {self.model_name} model from HuggingFace\n")
        pretrained_model = SentenceTransformer(self.model_name)
        
        embedded_data = self.get_vector_embeddings(pretrained_model, self.documents)
        self.add_documents_to_index(embedded_data, es_client, index_name)
        
        query_embedding_vector = pretrained_model.encode(query)
        query = {
            "field": "vector",
            "query_vector": query_embedding_vector,
            "k": self.k,
            "num_candidates": 10, 
        }
        response = es_client.search(
            index=index_name,
            knn=query,
            size=self.k,
        )

        for returned_doc in response["hits"]["hits"]:
            matching_documents.append(
                Document(
                    page_content=returned_doc["_source"]["utterance"],
                    metadata={ "speaker": returned_doc["_source"]["speaker"] },
                )
            )
        return matching_documents
        
    def get_vector_embeddings(self, model, input_docs):
        # turn utterances into vector and store them
        vector_data = []
        print("Get vector embeddings")
        for document in input_docs:
            encoded_content = model.encode(document.page_content).tolist()
            vector_data.append({
                "speaker": document.metadata["speaker"],
                "utterance": document.page_content,
                "vector": encoded_content,
            })
        return vector_data
    
    def create_index(self, elasticsearch_client, idx_name):
        # create mapping first
        index_settings = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            "mappings": {
                "properties": {
                    "utterance": {"type": "text"},
                    "speaker": {"type": "text"},
                    "vector": {"type": "dense_vector", "dims": 768, "index": True, "similarity": "cosine"},
                }
            }
        }
        elasticsearch_client.indices.delete(index=idx_name, ignore_unavailable=True)
        elasticsearch_client.indices.create(index=idx_name, body=index_settings)

    def add_documents_to_index(self, embedded_docs, es_client, index_name):
        self.create_index(es_client, index_name)
        for doc in embedded_docs:
            try:
                es_client.index(index=index_name, document=doc, refresh=True)
            except Exception as e:
                print(e)
