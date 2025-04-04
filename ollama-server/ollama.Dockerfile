FROM ollama/ollama:latest

ARG MODEL_NAME
ENV MODEL_NAME=$MODEL_NAME

EXPOSE 11434

RUN ollama serve & \
    sleep 5 && \
    ollama run $MODEL_NAME