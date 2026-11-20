| Strategy | Hit@3 | MRR@10 | Latency (ms/query) | #Chunks |
|---|---|---|---|---|
| 1. fixed chunks + vector | 67% | 0.50 | 192 | 1156 |
| 2. heading chunks + vector | 67% | 0.67 | 14 | 2395 |
| 3. heading chunks + hybrid | 67% | 0.50 | 14 | 2395 |
| 4. heading + hybrid + rerank | 67% | 0.67 | 5208 | 2395 |
