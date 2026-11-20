import re, uuid, pathlib
import numpy as np
import chromadb
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, CrossEncoder

DOCS_DIR = pathlib.Path("data/docs")
_embedder = None
_reranker = None

def embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder

def reranker():
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    return _reranker

def tokenize(text):
    return re.findall(r"\w+", text.lower())

# ---------- loading + chunking ----------
def load_docs():
    docs = []
    for p in sorted(DOCS_DIR.rglob("*.md")):
        docs.append((p.relative_to(DOCS_DIR).as_posix(), p.read_text(encoding="utf-8", errors="ignore")))
    if not docs:
        raise SystemExit("No docs found in data/docs. Run: python fetch_docs.py")
    return docs

def fixed_chunks(text, size=200, overlap=40):
    words = text.split()
    step = size - overlap
    chunks = []
    for i in range(0, len(words), step):
        piece = words[i:i + size]
        if piece:
            chunks.append(" ".join(piece))
    return chunks

def heading_chunks(text, max_words=250):
    """Structure-aware chunking: split on markdown headings, then cap long sections."""
    out = []
    for part in re.split(r"\n(?=#{1,4} )", text):
        part = part.strip()
        if not part:
            continue
        if len(part.split()) > max_words:
            out.extend(fixed_chunks(part, max_words, 30))
        else:
            out.append(part)
    return out

def make_chunks(chunker):
    fn = fixed_chunks if chunker == "fixed" else heading_chunks
    chunks = []
    for source, text in load_docs():
        for t in fn(text):
            chunks.append({"text": t, "source": source})
    return chunks

# ---------- index + retrieval ----------
class Index:
    def __init__(self, chunks):
        self.chunks = chunks
        texts = [c["text"] for c in chunks]
        embs = embedder().encode(texts, batch_size=64, show_progress_bar=True, normalize_embeddings=True)
        client = chromadb.EphemeralClient()
        self.col = client.create_collection(name="c" + uuid.uuid4().hex, metadata={"hnsw:space": "cosine"})
        for i in range(0, len(texts), 500):
            j = min(i + 500, len(texts))
            self.col.add(ids=[str(n) for n in range(i, j)],
                         embeddings=embs[i:j].tolist(),
                         documents=texts[i:j])
        self.bm25 = BM25Okapi([tokenize(t) for t in texts])

    def vector(self, query, k):
        q = embedder().encode([query], normalize_embeddings=True)
        res = self.col.query(query_embeddings=q.tolist(), n_results=k)
        return [int(i) for i in res["ids"][0]]

    def keyword(self, query, k):
        scores = self.bm25.get_scores(tokenize(query))
        return list(np.argsort(scores)[::-1][:k])

    def hybrid(self, query, k, pool=30):
        """Reciprocal rank fusion of vector + BM25 results."""
        fused = {}
        for ranking in (self.vector(query, pool), self.keyword(query, pool)):
            for rank, idx in enumerate(ranking):
                fused[int(idx)] = fused.get(int(idx), 0) + 1 / (60 + rank)
        return [i for i, _ in sorted(fused.items(), key=lambda x: -x[1])[:k]]

    def hybrid_rerank(self, query, k, pool=20):
        cands = self.hybrid(query, pool)
        scores = reranker().predict([(query, self.chunks[i]["text"]) for i in cands])
        order = np.argsort(scores)[::-1][:k]
        return [cands[i] for i in order]

    def search(self, query, mode, k=10):
        return getattr(self, mode)(query, k)
