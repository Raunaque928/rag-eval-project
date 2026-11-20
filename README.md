# RAG with Eval Harness (FastAPI docs)

## Setup (Windows/Mac/Linux, Python 3.10+)
    python -m venv venv
    venv\Scripts\activate          # Mac/Linux: source venv/bin/activate
    pip install -r requirements.txt
    python fetch_docs.py           # downloads FastAPI docs into data/docs
    python eval.py                 # compares 4 retrieval strategies
    set GROQ_API_KEY=your_key      # Mac/Linux: export GROQ_API_KEY=your_key
    python ask.py "How do I add CORS?"

## What to write here (for recruiters)
1. What I built
2. Architecture diagram
3. Results table (paste results/results.md) with real numbers
4. DECISIONS.md: why these chunk sizes, embedding model, RRF, reranker
