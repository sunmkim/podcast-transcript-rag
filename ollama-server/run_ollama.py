from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3.2",
    base_url="http://0.0.0.0:11434/",
    temperature=0.8,
    num_predict=256,
)

messages = [
    ("system", "You are a helpful translator. Translate the user sentence to French."),
    ("human", "I love programming."),
]

resp = llm.invoke(messages)
print(resp.content)
