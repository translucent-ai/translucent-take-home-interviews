import argparse
import pandas as pd
import pathlib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI

DATA_PATH = pathlib.Path(__file__).parent / "data" / "denials.csv"

openai_client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def load_docs():
    df = pd.read_csv(DATA_PATH)
    docs = df.apply(
        lambda r: f"Department {r['department']} denied because {r['denial_reason']} on {r['service_date']}", axis=1).tolist()
    return docs, df


def generate_answer(question: str, context: pd.DataFrame) -> str:
    response = openai_client.responses.create(
        model="gpt-4o",
        instructions="Answer the question based on the context.",
        input=f"""
Context:
{context.to_string()}

Question: {question}
        """.strip()
    )
    return response.output_text


def answer(question: str) -> str:
    docs, df = load_docs()
    vect = TfidfVectorizer().fit(docs + [question])
    doc_vecs = vect.transform(docs)
    q_vec = vect.transform([question])
    sims = cosine_similarity(q_vec, doc_vecs).flatten()

    rows = df[sims > sims.mean()]
    reason_counts = rows[['department', 'denial_reason']].groupby(
        ['department', 'denial_reason']).value_counts().sort_values(ascending=False)
    return generate_answer(question, reason_counts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", required=True)
    args = parser.parse_args()
    print(answer(args.question))
