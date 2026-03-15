# RAG Evaluation with Ragas


## Evaluation Dataset

You can find the question and ground truth answers that we evaluate in `eval_datasets.py`.

## Metrics

We evaluated both our retrieval and generation steps with the following built-in metrics from Ragas:
- Answer Relevancy
- Faithfulness
- Answer Correctness
- Context Precision
- Context Recall