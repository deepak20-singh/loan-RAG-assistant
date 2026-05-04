# 🏦 loan-rag-assistant

A Retrieval-Augmented Generation system for answering questions about small business loan policies. Built as a hands-on exercise in production-style RAG: hybrid retrieval, vector + keyword search, and a clean separation between retrieval and generation.

> **Status:** 🚧 Work in progress — retrieval pipeline complete, generation layer in development.

---

## What This Does (and Will Do)

You give it a question about loan policy — _"What credit score do I need for a $200K loan?"_ — and it retrieves the most relevant policy chunks from an internal knowledge base.

The eventual goal is end-to-end Q&A: retrieved chunks become context for an LLM, which produces a grounded answer (with sources).

---

## Project Status

| Component | Status |
|---|---|
| Document chunking | ✅ Done |
| Embedding generation | ✅ Done |
| Vector storage (Qdrant) | ✅ Done |
| Hybrid retrieval (vector + BM25 + RRF) | ✅ Done |
| LLM integration (Groq) | 🔜 Next |
| Structured outputs (Pydantic) | 📋 Planned |
| Tool calling (mock applicant DB) | 📋 Planned |
| Semantic caching (Redis) | 📋 Planned |
| Eval suite | 📋 Planned |
| Containerization | 📋 Planned |

---

## Architecture

### Current (retrieval-only)

```
                ┌──────────────────────────┐
                │   data/loan_policies.md  │
                └────────────┬─────────────┘
                             │
                  ┌──────────▼──────────┐
                  │  Chunking (manual)  │
                  └──────────┬──────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
     ┌────────▼─────────┐         ┌─────────▼──────────┐
     │  Embedding model │         │  BM25 (in-memory)  │
     │ (BGE-small-en)   │         │   keyword index    │
     └────────┬─────────┘         └─────────┬──────────┘
              │                             │
     ┌────────▼─────────┐                   │
     │     Qdrant       │                   │
     │  (vector store)  │                   │
     └────────┬─────────┘                   │
              │                             │
              └──────────────┬──────────────┘
                             │
                   ┌─────────▼──────────┐
                   │  Hybrid retrieval  │
                   │  with Reciprocal   │
                   │   Rank Fusion      │
                   └─────────┬──────────┘
                             │
                             ▼
                       Top-K chunks
```

### Target architecture

```
       Client (curl / API call)
                │
        ┌───────▼────────┐
        │    FastAPI     │
        └───────┬────────┘
                │
        ┌───────▼────────┐
        │ Hybrid retriever│ ──► Qdrant + BM25
        └───────┬────────┘
                │
        ┌───────▼────────┐
        │  LLM router    │ ──► Groq (Llama-3.3-70B)
        │  + Pydantic    │
        │  schemas       │
        └───────┬────────┘
                │
                ▼
       Structured response
       (answer + sources + confidence)
```

---

## Design Choices

A few decisions that shape this project, with the reasoning behind each:

### Why hybrid retrieval over pure vector search?
Pure vector search captures meaning but misses **exact keyword matches** — and lending policies are full of specific values like `"$250,000"`, `"650"`, `"43%"`. BM25 catches those. Vector search and BM25 fail in different ways, so combining them is more robust than either alone.

### Why Reciprocal Rank Fusion instead of weighted score addition?
Vector similarity scores live in `[0, 1]`. BM25 scores can range up to 20+ depending on corpus. Adding them directly would let BM25 dominate. RRF only uses **ranks**, which makes both retrievers commensurable without manual tuning of weights.

### Why Qdrant over Pinecone or pgvector?
- Open source, runs locally in Docker — no API keys, no rate limits during development.
- Fast, written in Rust.
- Cleaner Python client than alternatives.
- Pinecone is fine but adds a managed dependency I don't need at this stage.

### Why BGE-small embeddings over OpenAI's?
- Free and local — no per-call cost or rate limits during development.
- 384 dimensions vs OpenAI's 1536 → 4× smaller index, faster search.
- Good enough for English lending text. For multilingual or highly nuanced domains, I'd reconsider.

### Why store the BM25 index in memory instead of persisting it?
The corpus is small (a few hundred chunks). Rebuilding the BM25 index from Qdrant at app startup takes ~50ms and avoids drift between disk-cached BM25 and the live vector store. Qdrant becomes the single source of truth. At a million-chunk scale, I'd switch to OpenSearch for keyword search.

---

## Tech Stack

| Layer | Choice |
|---|---|
| Vector DB | Qdrant (Docker) |
| Embeddings | `sentence-transformers` with `BAAI/bge-small-en-v1.5` |
| Keyword search | `rank-bm25` |
| Rank fusion | Reciprocal Rank Fusion (custom) |
| Language | Python 3.11 |
| Planned: LLM | Groq (Llama-3.3-70B via OpenAI-compatible API) |
| Planned: API | FastAPI |
| Planned: Cache | Redis |

---

## Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- (Later, for the LLM step) a free [Groq API key](https://console.groq.com)

### 1. Clone and set up

```bash
git clone <your-repo-url>
cd loan-rag-assistant

python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Start Qdrant

```bash
docker-compose up -d qdrant
```

Open the Qdrant dashboard at [http://localhost:6333/dashboard](http://localhost:6333/dashboard) to verify it's running.

### 3. Ingest the policy document

```bash
python -m app.ingestion
```

You should see chunks being embedded and indexed. Confirm in the Qdrant dashboard that a `loan_policies` collection exists with N points.

### 4. Try a retrieval query

```python
from app.retrieval import retriever

results = retriever.search("What credit score do I need for a $200K loan?", top_k=3)
for r in results:
    print(f"Score: {r['score']:.3f}")
    print(r['text'][:200])
    print("---")
```

You should see the eligibility section ranking at the top.

---

## Project Structure

```
loan-rag-assistant/
├── data/
│   └── loan_policies.md        # Source knowledge base
├── app/
│   ├── config.py               # Settings via pydantic-settings
│   ├── ingestion.py            # Chunking + embedding + indexing
│   └── retrieval.py            # Hybrid search (vector + BM25 + RRF)
├── docker-compose.yml          # Qdrant (and Redis later)
├── requirements.txt
├── .env.example
└── README.md
```

---

## What I Learned Building This

A few takeaways worth highlighting:

- **Retrieval quality is the ceiling.** No matter how good the LLM is, if the right chunk isn't in the top-K, the answer will be wrong. Most "RAG quality" issues are retrieval issues in disguise.
- **Chunking strategy matters more than model choice.** Splitting on section headers gave noticeably better results than naive fixed-size chunks.
- **Test retrieval in isolation.** Before plugging in the LLM, query the retriever directly and read the results. If a human can answer the question from the top-3 chunks, the LLM probably can too. If a human can't, no LLM will save you.

---

## Roadmap

- [ ] LLM integration with Groq (Llama-3.3-70B)
- [ ] Pydantic-based structured outputs via Instructor
- [ ] Tool calling — mock applicant DB lookup for loan-decision queries
- [ ] Two response modes: policy Q&A vs full loan assessment
- [ ] Redis-backed exact + semantic caching
- [ ] FastAPI app with `/query` and `/health` endpoints
- [ ] Eval suite with policy questions and assessment scenarios
- [ ] Dockerize the full app

---

## Notes

This is a learning project, not a production system. The "loan policies" are synthetic — do not use this for actual lending decisions. The architectural patterns are real, but the data isn't.
