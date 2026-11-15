| Model | Trials | commit_timeout | stale_read | partial_batch | duplicate_delivery | Mean task_success | Agent cost (USD) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Claude Haiku 4.5 | 10 | 6/10 | 10/10 | 3/10 | 0/10 | 0.47 | 1.41 |
| Claude Sonnet 4.6 | 10 | 10/10 | 10/10 | 7/10 | 8/10 | 0.88 | 3.19 |

- Claude Haiku 4.5 per-run scores (tasks passed of 4): [1, 1, 1, 2, 2, 2, 2, 2, 3, 3]
- Claude Sonnet 4.6 per-run scores (tasks passed of 4): [3, 3, 3, 3, 3, 4, 4, 4, 4, 4]
- Pooled: Claude Haiku 4.5 19/40 vs Claude Sonnet 4.6 35/40, two-sided Fisher exact p = 0.000254
