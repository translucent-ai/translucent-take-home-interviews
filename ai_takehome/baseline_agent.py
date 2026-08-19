import argparse, pandas as pd, pathlib, json, re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA_PATH = pathlib.Path(__file__).parent / "data" / "denials.csv"

def load_docs():
    """Load the data and return the documents and dataframe."""
    df = pd.read_csv(DATA_PATH)
    docs = df.apply(lambda r: f"Department {r['department']} denied because {r['denial_reason']} on {r['service_date']}", axis=1).tolist()
    return docs, df

def answer(question: str) -> str:
    """Answer the question using the documents and dataframe."""
    docs, df = load_docs()

    # Vectorize the documents and question
    vect = TfidfVectorizer().fit(docs) # removed fit on question as any net new terms would get a score of 0 anyways
    doc_vecs = vect.transform(docs)
    q_vec = vect.transform([question])

    # Calculate the cosine similarity between the question and the documents
    sims = cosine_similarity(q_vec, doc_vecs).flatten()
    top_idx = sims.argsort()[-3:][::-1]

    # Extract the top 3 most similar documents and count the number of times each denial reason appears
    rows = df.iloc[top_idx]
    # Include department and reason in the answer
    reason_counts = {
        f"{dept} | {reason}": count
        for (dept, reason), count in rows[["department", "denial_reason"]].value_counts().items()
    }
    answer_parts = [f"{k}: {v}" for k,v in reason_counts.items()]
    answer = " | ".join(answer_parts)
    return answer

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", required=True)
    args = parser.parse_args()
    print(answer(args.question))
