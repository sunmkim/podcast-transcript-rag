FROM ollama/ollama:latest

# retrieve model name from docker-compose so users can change it easily
ARG MODEL_NAME
ENV MODEL_NAME=$MODEL_NAME

EXPOSE 11434

# start ollama server, wait for it to be active, then run llm
RUN ollama serve & \
    sleep 5 && \
    ollama run $MODEL_NAME