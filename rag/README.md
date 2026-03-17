# RAG with Elasticsearch

## Models

Embedding model used to embed our text into vectors is `amazon.titan-embed-text-v2`, as offered on AWS Bedrock, and the LLM for answer generation is Claude 3 Haiku.


## Chaining with Langchain

The script `create_knowledge_base.py` loads the text data in `data/data.json` into S3 Vectors, and creates a Bedrock Knowledge Base.

The `rag.py` contains our RAG object that creates the RAG chain (using Langchain, of course)
that uses the AWS Bedrock Knowledge Base as our retriever. The retriever runs a semantic search to fetch relevant documents, and then inject the results into a Langchain prompt template that is chained and invoked to the Claude 3 Haiku model. This will allow the LLM to give back our answer.

## Output

To test our RAG pipeline, we ask the question relevant to the podcast episode: "Who is the Prime Minister of Canada? Who did he succeed as Prime Minister?"

If the RAG pipeline was successful, then the LLM should be able to retrieve and summarize the relevant documents that answer the question about the podcast. And we see that it indeed does when we run `python rag/rag.py`:

```
 Who is the Prime Minister of Canada? Who did he succeed as Prime Minister? 

Answer:
 Based on the information provided, the new Prime Minister of Canada is Mr. Carney, who has been elected as the leader of the Liberal Party and will be sworn in as Prime Minister. Mr. Carney is succeeding Justin Trudeau as Prime Minister.

Context:
[Document(metadata={'location': {'s3Location': {'uri': ''}, 'type': 'S3'}, 'score': 0.7494660019874573, 'type': 'TEXT', 'source_metadata': {'x-amz-bedrock-kb-chunk-id': 'utterance-74', 'speaker': 'matina stevis-gridneff', 'utterance_text': 'Absolutely. It is a little complicated. But Canada has a sort of parliamentary system where the leader of the party in power is the prime minister. And so Mr. Carney has been elected as leader of the Liberal Party. And so he will be sworn in as prime minister. But by Canadian political rules, the country needs to hold an election by October. And so our expectation — and Mr. Carney’s campaign has indicated this — is that he will call for a federal election really early on after he is sworn in, and seek to capitalize on his momentum to get a mandate at a national level from Canadians.'}}, page_content=''),
 Document(metadata={'location': {'s3Location': {'uri': ''}, 'type': 'S3'}, 'score': 0.7343379259109497, 'type': 'TEXT', 'source_metadata': {'x-amz-bedrock-kb-chunk-id': 'utterance-68', 'speaker': 'matina stevis-gridneff', 'utterance_text': 'Well, Kim, back in January, when this problem was gathering pace, Justin Trudeau was resigning. His party, the Liberal Party, who have been in power for nearly 10 years, were facing dismal polls. They were 20-plus percentage points behind the opposition, the conservatives, led by Pierre Poilievre. And in the federal elections looming, it was sort of a foregone conclusion that the conservatives were going to win. Poilievre was going to be the new prime minister. He had these ideological and stylistic affiliations to the MAGA movement and the sort of more right-wing populist movement. And that was kind of what was going to happen in Canadian politics. But things started to rapidly change, just as Trump escalated his menacing rhetoric about Canadian sovereignty and went ahead with his tariff threats. Something, I mean, truly remarkable happens, and I spoke to pollsters. One of them, a really seasoned pollster, told me that he’s never seen this in his entire career. We go from “the Liberal Party’s dead, and they’re going to be going into political exile for a long, long time” to this liberal revival. The anti-US, anti-Trump sentiment is basically doing huge favors to the Liberal Party, even rehabilitating the image of Justin Trudeau to a certain extent, who was loathed to the extent that he had to resign in early January, right? And so it sets the scene for a stunning and pretty rapid reversal of fortunes for the Liberal Party as it goes into a leadership race to elect its new leader, the person who’s going to replace Justin Trudeau as party chief and as prime minister.'}}, page_content=''),
 Document(metadata={'location': {'s3Location': {'uri': ''}, 'type': 'S3'}, 'score': 0.7222195565700531, 'type': 'TEXT', 'source_metadata': {'x-amz-bedrock-kb-chunk-id': 'utterance-73', 'utterance_text': 'OK, can you remind me how this works? So he’s serving as prime minister, and then he has to run fairly soon again as prime minister? Can you just give me the little Canadian Parliament 101?', 'speaker': 'kim severson'}}, page_content='')]
 ```

The output from running `rag.py` shows the user query, LLM-generated answer, and the context given to our LLM to answer the question with S3 vector.