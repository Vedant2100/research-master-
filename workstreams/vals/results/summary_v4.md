| Model | Trials | commit_timeout | stale_read | partial_batch | duplicate_delivery | Mean task_success | Agent cost (USD) |
|---|---:|---:|---:|---:|---:|---:|---:|
| GPT-6.1 Terra (Codex) | 3 | 3/3 | 3/3 | 3/3 | 3/3 | 1.00 | 0.00 |
| Claude Haiku 5.5 | 3 | 2/3 | 3/3 | 3/3 | 3/3 | 0.92 | 0.05 |
| Claude Sonnet 5.5 | 3 | 3/3 | 3/3 | 3/3 | 3/3 | 1.00 | 0.32 |

- GPT-6.1 Terra (Codex) per-run scores (tasks passed of 4): [4, 4, 4]
- Claude Haiku 5.5 per-run scores (tasks passed of 4): [3, 4, 4]
- Claude Sonnet 5.5 per-run scores (tasks passed of 4): [4, 4, 4]
- Claude Haiku 5.5 vs Claude Sonnet 5.5: run-level exact permutation p = 1
- Claude Haiku 5.5 vs GPT-6.1 Terra (Codex): run-level exact permutation p = 1
- Claude Sonnet 5.5 vs GPT-6.1 Terra (Codex): run-level exact permutation p = 1
