# podcast-transcript-rag
My RAG project

To activate the development environment, run this line: `source .venv/bin/activate`

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