import json
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-mpnet-base-v2"


# read in data from json file
with open('/workspaces/podcast-transcript-rag/data/data.json', 'rt') as f_in:
    docs_raw = json.load(f_in)

# download embedding model
pretrained_model = SentenceTransformer(MODEL_NAME)

# turn utterances into vector and store them
data_with_vector = []
for document in docs_raw:
    document["vector"] = pretrained_model.encode(doc["utterance"]).tolist()
    operations.append(doc)

print(operations[1])