import os
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama


information = """
Seasonal allergies affect nearly one-quarter of kids in the United States, per the Centers for Disease Control and Prevention (CDC).
Many people experience sniffly symptoms in the spring. 
That’s when most plants release pollen. Pollen is a powdery substance. It helps plants reproduce. 
But it can also trigger allergy symptoms. People with allergies should “check pollen forecasts, and limit outdoor time during high levels,” the CDC says.
Cities such as Atlanta, Georgia, and Houston, Texas, have already broken spring pollen records this year. That’s according to the Asthma and Allergy Foundation of America. 
Studies suggest that warming global temperatures may be a cause. More pollen is released. 
This makes the spring allergy season last longer.
"""

def main():
    template = """
        You are a helpful assistant from Australia with a heavy Queensland accent and lingo. 
        Summarize the user's input information in bogan dialect: {information}.
    """
    summary_prompt_template = PromptTemplate(
        input_variables=["information"],
        template=template,
    )

    # initialize llm
    llm = ChatOpenAI(
        temperature=0.3,
        model_name="gpt-3.5-turbo"
    )
    # llm = ChatOllama(
    #     model="llama3.2",
    #     base_url="http://0.0.0.0:11434/",
    #     temperature=0.8,
    #     num_predict=256,
    # )
    
    chain = summary_prompt_template | llm | StrOutputParser()
    response = chain.invoke(input={"information": information})
    print(response)

if __name__ == "__main__":
    main()