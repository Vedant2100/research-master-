| Model | Trials | commit_timeout | stale_read | partial_batch | duplicate_delivery | Mean task_success | Agent cost (USD) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Claude Haiku 4.5 | 10 | 6/10 | 10/10 | 3/10 | 0/10 | 0.47 | 1.41 |
| Claude Haiku 5.5 | 10 | 10/10 | 10/10 | 10/10 | 9/10 | 0.97 | 0.10 |
| Claude Opus 5.5 | 10 | 10/10 | 10/10 | 10/10 | 10/10 | 1.00 | 2.19 |
| Claude Sonnet 4.6 | 10 | 10/10 | 10/10 | 7/10 | 8/10 | 0.88 | 3.19 |
| Claude Sonnet 5.5 | 10 | 10/10 | 10/10 | 10/10 | 10/10 | 1.00 | 0.91 |

- Claude Haiku 4.5 per-run scores (tasks passed of 4): [1, 1, 1, 2, 2, 2, 2, 2, 3, 3]
- Claude Haiku 5.5 per-run scores (tasks passed of 4): [3, 4, 4, 4, 4, 4, 4, 4, 4, 4]
- Claude Opus 5.5 per-run scores (tasks passed of 4): [4, 4, 4, 4, 4, 4, 4, 4, 4, 4]
- Claude Sonnet 4.6 per-run scores (tasks passed of 4): [3, 3, 3, 3, 3, 4, 4, 4, 4, 4]
- Claude Sonnet 5.5 per-run scores (tasks passed of 4): [4, 4, 4, 4, 4, 4, 4, 4, 4, 4]
- Claude Haiku 4.5 vs Claude Sonnet 4.6: run-level exact permutation p = 0.00023
- Claude Haiku 4.5 vs Claude Haiku 5.5: run-level exact permutation p = 3.2e-05
- Claude Haiku 4.5 vs Claude Sonnet 5.5: run-level exact permutation p = 1.1e-05
- Claude Haiku 4.5 vs Claude Opus 5.5: run-level exact permutation p = 1.1e-05
- Claude Sonnet 4.6 vs Claude Haiku 5.5: run-level exact permutation p = 0.14
- Claude Sonnet 4.6 vs Claude Sonnet 5.5: run-level exact permutation p = 0.033
- Claude Sonnet 4.6 vs Claude Opus 5.5: run-level exact permutation p = 0.033
- Claude Haiku 5.5 vs Claude Sonnet 5.5: run-level exact permutation p = 1
- Claude Haiku 5.5 vs Claude Opus 5.5: run-level exact permutation p = 1
- Claude Sonnet 5.5 vs Claude Opus 5.5: run-level exact permutation p = 1
