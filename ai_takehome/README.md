# Take‑Home (2‑3 hrs) – Lead AI Engineer

**Objective:** Improve the answer quality of a retrieval‑augmented QA pipeline on a claims‑denial dataset.

## Provided

* `baseline_agent.py` – already answers questions using simple BM25 retrieval.
* `data/denials.csv` – synthetic dataset (no PHI).
* `eval.py` – runs five pre‑written tests that compare your answers to expected key phrases.
* `requirements.txt` – only open‑source libs; no paid API keys required.

## Your Tasks (**aim for 2 hrs of coding time**)

1. **Replace the retrieval layer** with an embedding‑based approach (e.g., `sentence-transformers`) or improve ranking logic.
2. **Add a brief relevance‑aware answer synthesizer** (few‑shot prompt to OpenAI *optional*, but not required).
3. Write a **short `ARCHITECTURE.md`** (≤1 page) explaining trade‑offs you considered—this will fuel onsite discussion.

## Running locally

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python baseline_agent.py --question "Why are cardiology claims denied most often?"
python eval.py         # should output score; target ≥3/5
```

## Submission

* Push to a Git repo or share a zip.
* Make sure `eval.py` runs without errors.
* Commit only open‑source models or download scripts (no large checkpoints).
