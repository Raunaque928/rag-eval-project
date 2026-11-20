"""Compare retrieval strategies on your hand-labelled questions.

Usage:
  python eval.py                      # run all 4 strategies
  python eval.py --min-hit 0.70       # exit code 1 if the best strategy's hit@3 is below 0.70 (for CI)
"""
import json, time, argparse, pathlib, sys
from common import make_chunks, Index

STRATEGIES = {
    "1. fixed chunks + vector":        ("fixed",   "vector"),
    "2. heading chunks + vector":      ("heading", "vector"),
    "3. heading chunks + hybrid":      ("heading", "hybrid"),
    "4. heading + hybrid + rerank":    ("heading", "hybrid_rerank"),
}

def is_hit(chunk, q):
    if chunk["source"] != q["source"]:
        return False
    must = q.get("must_contain")
    return (must.lower() in chunk["text"].lower()) if must else True

def main(min_hit):
    questions = [q for q in json.load(open("eval/questions.json", encoding="utf-8")) if q.get("source")]
    print(f"{len(questions)} answerable questions loaded")
    indexes, rows = {}, []
    for name, (chunker, mode) in STRATEGIES.items():
        if chunker not in indexes:
            print(f"Building index for '{chunker}' chunking...")
            indexes[chunker] = Index(make_chunks(chunker))
        idx = indexes[chunker]
        hits3, rr_sum, t0 = 0, 0.0, time.time()
        for q in questions:
            ranked = idx.search(q["question"], mode, k=10)
            flags = [is_hit(idx.chunks[i], q) for i in ranked]
            if any(flags[:3]):
                hits3 += 1
            if any(flags):
                rr_sum += 1 / (flags.index(True) + 1)
        latency_ms = (time.time() - t0) / len(questions) * 1000
        rows.append({"strategy": name, "hit@3": hits3 / len(questions),
                     "MRR@10": rr_sum / len(questions), "latency_ms": latency_ms,
                     "chunks": len(idx.chunks)})

    lines = ["| Strategy | Hit@3 | MRR@10 | Latency (ms/query) | #Chunks |", "|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['strategy']} | {r['hit@3']:.0%} | {r['MRR@10']:.2f} | {r['latency_ms']:.0f} | {r['chunks']} |")
    table = "\n".join(lines)
    print("\n" + table)
    pathlib.Path("results").mkdir(exist_ok=True)
    pathlib.Path("results/results.md").write_text(table + "\n", encoding="utf-8")
    json.dump(rows, open("results/results.json", "w"), indent=2)

    if min_hit is not None:
        best = max(r["hit@3"] for r in rows)
        if best < min_hit:
            print(f"\nFAIL: best hit@3 {best:.0%} < required {min_hit:.0%}")
            sys.exit(1)
        print(f"\nPASS: best hit@3 {best:.0%} >= {min_hit:.0%}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-hit", type=float, default=None)
    main(ap.parse_args().min_hit)
