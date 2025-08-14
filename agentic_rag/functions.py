import json
from langchain_core.documents import Document


def load_documents(datapath: str) -> list:
    documents = []

    with open(datapath, 'rt') as f_in:
        docs_raw = json.load(f_in)

    for doc in docs_raw:
        document = Document(
            page_content=doc["utterance"],
            metadata={ "speaker": doc["speaker"] }
        )
        documents.append(document)
    print(f"{len(documents)} documents loaded!")
    return documents