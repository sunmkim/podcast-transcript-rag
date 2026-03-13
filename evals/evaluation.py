import os
import sys
import boto3
from typing import List
from langchain_aws import BedrockEmbeddings, ChatBedrock
from ragas import evaluate, EvaluationDataset, SingleTurnSample
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.metrics import AnswerRelevancy, Faithfulness, AnswerCorrectness, ContextPrecision, ContextRecall
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "rag"))

from rag import RAG
from constants import BEDROCK_EMBEDDING_MODEL, EVALUATOR_LLM_MODEL, KNOWLEDGEBASE_ID
from eval_datasets import EVAL_QUESTIONS, EVAL_GROUND_TRUTHS

load_dotenv()


llm_config = {
    "region_name": "us-east-1",
    "llm": EVALUATOR_LLM_MODEL,
    "embeddings": BEDROCK_EMBEDDING_MODEL,
    "temperature": 0.4,
}


def generate_responses(rag):
    responses = []
    for question in EVAL_QUESTIONS:
        result = rag.invoke(question)
        response = result["response"]
        # store retrieved context for evals
        contexts = [doc.metadata['source_metadata']['utterance_text'] for doc in result["context"]]
        responses.append({"response": response, "contexts": contexts})
    return responses


def build_eval_dataset(responses) -> EvaluationDataset:
    samples = []
    for i, question in enumerate(EVAL_QUESTIONS):
        sample = SingleTurnSample(
            user_input=question,
            response=responses[i]["response"],
            retrieved_contexts=responses[i]["contexts"],
            reference=EVAL_GROUND_TRUTHS[i],
        )
        samples.append(sample)
    return EvaluationDataset(samples=samples)


def run_evaluation():
    print("Building RAG chain...")
    rag = RAG(KNOWLEDGEBASE_ID)
    rag.init_rag_chain()
    
    print("Set up RAG models")
    bedrock_client = boto3.client("bedrock-runtime", region_name=llm_config["region_name"])
    evaluator_llm = LangchainLLMWrapper(
        ChatBedrock(
            client=bedrock_client,
            model_id=EVALUATOR_LLM_MODEL,
            model_kwargs={"temperature": llm_config["temperature"]},
        )
    )
    bedrock_embeddings = LangchainEmbeddingsWrapper(
        BedrockEmbeddings(model_id=BEDROCK_EMBEDDING_MODEL, client=bedrock_client)
    )

    print("Generating responses for eval questions...")
    responses = generate_responses(rag)

    print("Building evaluation dataset...")
    eval_dataset = build_eval_dataset(responses)


    metrics = [
        AnswerRelevancy(),
        Faithfulness(),
        AnswerCorrectness(),
        ContextPrecision(), 
        ContextRecall(),
    ]

    print("Running RAGAS evaluation...")
    results = evaluate(
        dataset=eval_dataset,
        metrics=metrics,
        llm=evaluator_llm,
        embeddings=bedrock_embeddings
    )

    results_df = results.to_pandas()
    print(results_df.columns)
    print(results_df[
        ['user_input', 'response', 'answer_relevancy', 'faithfulness', 'answer_correctness','context_precision', 'context_recall']
    ])
    return results


if __name__ == "__main__":
    run_evaluation()
