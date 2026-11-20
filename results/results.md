| Strategy | Hit@3 | MRR@10 | Latency (ms/query) | #Chunks |
|---|---|---|---|---|
| 1. fixed chunks + vector | 84% | 0.76 | 31 | 1156 |
| 2. heading chunks + vector | 82% | 0.65 | 6 | 2395 |
| 3. heading chunks + hybrid | 78% | 0.66 | 9 | 2395 |
| 4. heading + hybrid + rerank | 76% | 0.65 | 238 | 2395 |
