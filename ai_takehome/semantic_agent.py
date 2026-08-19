import argparse
import os
import pathlib

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

load_dotenv()


class SemanticRetrievalAgent:
    """Retrieve top-k department chunks via embeddings."""

    def __init__(self, path: str, embed_model: str = "multi-qa-mpnet-base-cos-v1", llm_model: str = "gpt-4o-mini"):
        """Initialize the SemanticRetrievalAgent."""
        
        self._client = None
        key = os.environ.get("OPENAI_API_KEY")
        if key:
            self._client = OpenAI(api_key=key)
        
        self._embed_model = SentenceTransformer(embed_model)
        self._llm_model = llm_model

        self._df = pd.read_csv(path)
        self._chunks: list[str] = []
        self._embeddings: np.ndarray | None = None
        self._index()

    def answer(self, query: str, top_k: int = 3) -> str:
        """Synthesize an answer from retrieved chunks using OpenAI."""
        chunks = self._retrieve(query, top_k=top_k)
        context = "\n\n".join(chunks)
        if not self._client:
            return context
        answer = self._answer(query, context)
        return answer
    
    def _retrieve(self, query: str, top_k: int = 3) -> list[str]:
        """Return the top-k retrieved summary chunks."""
        query_embed = self._embed(query)
        scores = cos_sim(query_embed, self._embeddings).cpu().numpy().flatten()
        top_idx = scores.argsort()[-top_k:][::-1]
        chunks = [self._chunks[idx] for idx in top_idx]
        return chunks

    def _answer(self, query: str, context: str) -> str:
        """Call LLM model to answer a question from retrieved context chunks."""
        system_prompt = """
            You answer questions about healthcare claims based on the provided context.

            How to answer:
            - Analytical questions (counts, trends, "most common", "which department"):
            Use ONLY the provided context. Cite department names, denial reasons, and counts.
            If the context should answer the question but does not contain the information,
            respond with "I don't know".
            - Generic or definitional questions (e.g. "What is authorization missing?"):
            Use your general knowledge to explain the concept briefly.
            Optionally add relevant counts from context if they are present, but do not
            require context to define a term.

            Be concise and factual but sound like a human assistant. Do not invent counts or departments or make up information.

            Examples:

            Question: What are the top denial reasons in Oncology?
            Context: Oncology department denial reasons: Missing info (9), Expired coverage (7), Authorization missing (6)
            Answer: In Oncology, denials most often occur for Missing info (9), Expired coverage (7), and Authorization missing (6).

            Question: What is authorization missing?
            Context: Authorization missing denial reasons by department: Gastroenterology (6), Oncology (6)
            Answer: Authorization missing means a claim was denied because required prior approval from the insurer was not obtained before the service. In this dataset, it appears most often in Gastroenterology (6) and Oncology (6).

            Question: What are the top denial reasons in Psychiatry?
            Context: Oncology department denial reasons: Missing info (9), Expired coverage (7)
            Answer: I don't know.
        """
       
        user_prompt = f"Context:\n{context}\n\nQuestion: {query}"
        response = self._client.chat.completions.create(
            model=self._llm_model,
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}
            ],
        )
        answer = response.choices[0].message.content.strip()
        return answer

    def _index(self) -> None:
        """Build and embed department- and reason-level summary chunks."""
        dept_summaries = self._build_summaries(
            group_cols=["department", "denial_reason"],
            template="{key} department denial reasons: {counts_str}",
        )
        reason_summaries = self._build_summaries(
            group_cols=["denial_reason", "department"],
            template="{key} denial reasons by department: {counts_str}",
        )
        self._chunks = dept_summaries + reason_summaries
        self._embeddings = self._embed(self._chunks)

    def _build_summaries(self, group_cols: list[str], template: str) -> list[str]:
        """Group counts and format one summary string per top-level group."""
        counts = self._df.groupby(group_cols).size()
        summaries = []

        for key in counts.index.get_level_values(0).unique():
            group_counts = counts[key]
            counts_list = [
                f"{label} ({count})" for label, count in group_counts.items()
            ]
            counts_str = ", ".join(counts_list)
            summaries.append(template.format(key=key, counts_str=counts_str))

        return summaries

    def _embed(self, texts: list[str] | str) -> np.ndarray:
        """Embed a list of text strings."""
        texts = [texts] if isinstance(texts, str) else texts
        return self._embed_model.encode(texts, normalize_embeddings=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", required=True)
    args = parser.parse_args()
    data_path = pathlib.Path(__file__).parent / "data" / "denials.csv"
    agent = SemanticRetrievalAgent(data_path)
    print(agent.answer(args.question))
