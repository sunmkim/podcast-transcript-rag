# Using Local LLMs with Ollama

The current scripts in  `agentic_rag` and `rag` directories are using OpenAI's GPT-5 as the LLM that powers these applications. However, we can also use Ollama to run open-source models locally rather than using closed proprietary models.


##  Containerization

If we were to run an Ollama server in production, it would be good to have it as its own microservice. Hence, I containerized the Ollama server using Docker and Docker compose. Since we have this containerized, we can run the Docker image on a service like AWS App Runner or GCP Cloud Run.


## How to run:

Simply run `docker compose up` to get the LLM up and running locally. The example is using `llama3.2`. If you have this running in the background, we can run a script like `run_ollama.py` with `python run_ollama.py`.