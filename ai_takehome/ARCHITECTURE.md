# Architecture

## How to run

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optional: add OPENAI_API_KEY for LLM answers

python baseline_agent.py --question "Why are cardiology claims denied most often?"
python semantic_agent.py --question "Why are cardiology claims denied most often?"
python eval.py
```

If you skip the API key, the semantic agent just returns the retrieved chunk text.

## What I built

The exercise came with `baseline_agent.py`. I made a couple tweaks there first, then built `semantic_agent.py` as the main deliverable.

## Data exploration (`explore.ipynb`)

Before building the semantic agent, I spent time in a notebook looking at the CSV directly: groupbys on department and denial reason, value counts, etc. Most of the eval questions aren't really "find similar documents" problems. They're aggregation questions. That exploration is what pushed me away from claim-level chunks toward pre-built count summaries.

I didn't change `eval.py`. Looking at the data, a few expected keywords don't line up perfectly with the top counts (e.g. radiology's most common reasons in the data aren't exactly what the eval checks for). I worked toward the eval as given rather than second-guessing it, but I'd flag that in a real project.

## Baseline (provided, then tweaked)

Running the starter baseline as-is got me 2/5 on eval. Two small changes brought it to 3/5.

I added the department to the answer snippet (e.g. `Cardiology | Coding error: 5`), which helped keyword matching. I also stopped fitting the question into the TF-IDF vectorizer. Any word that only appears in the query gets TF=0 across all documents anyway, so it doesn't help retrieval and you're refitting for no reason.

If I kept going on the baseline, I'd split indexing and retrieval so the vectorizer is built once at startup instead of on every query.

## Semantic retriever

I used `multi-qa-mpnet-base-cos-v1`. The flow is extract chunks at init, embed them once, then for each query embed the question and pull the top-k matches by cosine similarity.

**Chunking.** Following the baseline, I started with one chunk per claim, but most eval questions are really group-level ("what are the most common denial reasons in cardiology?"). I switched to pre-built summaries based on counts: department to denial reason counts, and denial reason to department counts. That shrunk the index from ~300 chunks to ~20 and got eval to 5/5. The catch is you're locked into whatever aggregations you pre-compute. We didn't build payer summaries, so a payer-level question would fail. Same for looking up a specific claim ID.

**Retrieval vs SQL.** For structured tabular data, I think the better long-term approach is giving the LLM a SQL tool (with appropriate permissions) and letting it query until it has an answer. That way the model figures out the right aggregation on the fly instead of relying on summaries we guessed ahead of time. Claim-level retrieval doesn't help when the question is really about a distribution across groups.

## Embeddings and external context

A general-purpose sentence-transformer was fine for a two-hour pass. With more time I'd look at clinical or domain-tuned models and sanity-check whether denial terms cluster the way you'd expect. Could also look at published biomedical retrieval benchmarks rather than rolling my own analysis.

I'd also augment the data with plain-English definitions of denial reasons and some general medical context. The CSV has labels like "authorization missing" and "missing info" but nothing that explains the difference.

## Generation

For synthesis I used a few-shot OpenAI prompt with `gpt-4o-mini`. The prompt tries to handle two cases differently: stats questions should stick to retrieved context and say "I don't know" when the chunks don't have the answer; definitional questions can use general knowledge and pull in counts when they're in context. That was my main approach to avoiding made-up numbers.

The five keyword-matching eval tests aren't great for measuring hallucination though. I'd want faithfulness evals and some out-of-distribution questions before trusting that behavior. No API key means it falls back to returning the chunk text directly.

## If I had more time

**Hybrid routing.** I'd combine embeddings with the SQL tool idea above. Embeddings handle fuzzy matching well ("heart department billing issues" probably means Cardiology). SQL handles exact counts and dimensions you didn't pre-summarize (payer, claim ID, date ranges). Use SQL for straightforward analytical questions; use retrieval when the question is messier or needs domain context like a medical term FAQ.

**Richer evals.** I'd extend the benchmark by adding payer-level questions, specific claim lookups, definitional vs analytical cases, and out-of-distribution phrasing. And actually measure context relevance, factual consistency and whether "I don't know" shows up when it should. I'd measure retrieval and generation steps separately, and either extract ground truths or leverage LLM as a judge. 

**Pluggable retriever and LLM layers.** Retrieval and generation are pretty tied to sentence-transformers and OpenAI right now. I'd put both behind interfaces so the core agent stays the same and you plug in adapters: TF-IDF, sentence-transformers, a cross-encoder for reranking, OpenAI, or a local model. Same flow, different backends, less rewriting when you want to experiment.

**Scaling.** Right now everything fits in memory (~300 rows, ~20 chunks). That's fine for a take-home. At production scale you'd want Postgres (or similar) for structured claims and SQL aggregation, plus a vector DB (pgvector, Pinecone, etc.) once you're indexing millions of chunks instead of twenty. You'd also want async indexing pipelines, caching, and separate services for retrieval vs generation instead of loading models in the same process as the agent.
