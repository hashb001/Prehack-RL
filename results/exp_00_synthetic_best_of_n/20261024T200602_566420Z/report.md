# Phase 1: synthetic infrastructure check

These results are from a deliberately constructed toy distribution. No LLM or RL training occurred.

2000 trials per seed; seeds: [42, 43, 44]. Judges share candidate pools; N uses nested prefixes.

| Judge | N | Mean accuracy | Mean proxy reward | Exact expected accuracy |
|---|---:|---:|---:|---:|
| control | 1 | 0.5482 | 0.4289 | 0.5500 |
| control | 2 | 0.7942 | 0.5765 | 0.7975 |
| control | 4 | 0.9588 | 0.6753 | 0.9590 |
| control | 8 | 0.9982 | 0.6989 | 0.9983 |
| control | 16 | 1.0000 | 0.7000 | 1.0000 |
| control | 32 | 1.0000 | 0.7000 | 1.0000 |
| confidence_biased | 1 | 0.5482 | 0.6552 | 0.5500 |
| confidence_biased | 2 | 0.4140 | 0.7225 | 0.4125 |
| confidence_biased | 4 | 0.1738 | 0.7412 | 0.1784 |
| confidence_biased | 8 | 0.0327 | 0.7484 | 0.0319 |
| confidence_biased | 16 | 0.0015 | 0.7499 | 0.0010 |
| confidence_biased | 32 | 0.0000 | 0.7500 | 0.0000 |

Synthetic selection only: no policy training or real LLM judge.
The candidate distribution deliberately excludes correct confident answers.
