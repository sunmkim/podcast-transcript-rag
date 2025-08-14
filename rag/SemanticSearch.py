import numpy as np
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer


class Search():
    def __init__(self, model_name, index_name, url='http://localhost:9200'):
        np.float_ = np.float64
        self.url = url
        self.model_name = model_name
        self.index_name = index_name
        self.es_client = Elasticsearch(url)
        print('ElasticSearch Client:\n', self.es_client.info())
        print(f"Download {model_name} model from HuggingFace")
        self.pretrained_model = SentenceTransformer(self.model_name)


    def get_vector_embeddings(self, input_docs):
        # turn utterances into vector and store them
        vector_data = []
        print("Get vector embeddings")
        for document in input_docs:
            document["vector"] = self.pretrained_model.encode(document["utterance"]).tolist()
            vector_data.append(document)
        return vector_data


    def create_index(self):
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
        self.es_client.indices.delete(index=self.index_name, ignore_unavailable=True)
        self.es_client.indices.create(index=self.index_name, body=index_settings)


    def add_documents_to_index(self, raw_documents):
        data_with_vectors = self.get_vector_embeddings(raw_documents)
        self.create_index()

        for doc in data_with_vectors:
            try:
                self.es_client.index(index=self.index_name, document=doc, refresh=True)
            except Exception as e:
                print(e)

    def encode_search_input(self, input):
        vectorized_input = self.pretrained_model.encode(input)
        return vectorized_input
    
    def semantic_search(self, user_query):
        vectors = self.encode_search_input(user_query)
        query = {
            "field": "vector",
            "query_vector": vectors,
            "k": 5,
            "num_candidates": 10, 
        }
        response = self.es_client.search(
            index=self.index_name,
            knn=query,
            size=5,
            source=["utterance"]
        )
        return response["hits"]["hits"]