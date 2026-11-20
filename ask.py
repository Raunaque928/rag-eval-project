"""Ask a question. Uses heading chunks + hybrid + rerank, answers with Groq (free tier).
Setup: get a free key at https://console.groq.com, then set GROQ_API_KEY.
Usage: python ask.py "How do I add CORS to FastAPI?"
"""
import os, sys
from groq import Groq
from common import make_chunks, Index

question = " ".join(sys.argv[1:]) or input("Question: ")
index = Index(make_chunks("heading"))
top = index.search(question, "hybrid_rerank", k=4)
context = "\n\n---\n\n".join(f"[source: {index.chunks[i]['source']}]\n{index.chunks[i]['text']}" for i in top)

prompt = f"""Answer the question using ONLY the context below. Cite the source file names you used.
If the context does not contain the answer, reply exactly: "I don't know based on the docs."

Context:
{context}

Question: {question}"""

client = Groq(api_key=os.environ["GROQ_API_KEY"])
resp = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}],
    temperature=0,
)
print(resp.choices[0].message.content)
