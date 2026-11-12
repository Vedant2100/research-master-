# StaleStream code (v0)

Environment, baselines, reader and GRPO/RLOO loop for the CS258 project. See
`CS258_Design_Doc.md` for the design and `STATUS.md` for evidence. `headroom_gate.py`
is copied unchanged from `Vedant2100/f26@1b30fd7:cs258/stalestream/headroom_gate.py`.

## Setup (this machine)

Home has a hard ~11 GB cap that `quota` does not report, so the venv, models, data and
runs live on `/scratch/vbork001/stalestream`. Always run `source /scratch/vbork001/stalestream/env.sh` first.
It activates the venv (Python 3.12, vllm 0.21, torch 2.11, trl 1.17, peft 0.21) and
points HF/pip/vLLM/Triton caches, TMPDIR and CPATH (extracted Python 3.12 headers,
needed by Triton's JIT) at scratch. vllm 0.33 cannot be installed here because it needs
llguidance 1.7 wheels that require glibc newer than this machine's 2.28.

## Pipeline

```bash
source /scratch/vbork001/stalestream/env.sh && export HF_HUB_OFFLINE=1
D=$S/data
# 1. episodes (entity-disjoint train/test split; ground truth from dates + hidden reliability)
python -m stalestream.generator --mquake $D/MQuAKE-CF-3k-v2.json --out $D/episodes_v0
# 1b. v1 (current): mixed date formats + LLM paraphrase with verbatim label strings
python -m stalestream.generator --mquake $D/MQuAKE-CF-3k-v2.json --out $D/episodes_v1_raw --date-style mixed --seed 2027
CUDA_VISIBLE_DEVICES=0 python -m stalestream.paraphrase --episodes $D/episodes_v1_raw/test.jsonl --out $D/episodes_v1/test.jsonl
CUDA_VISIBLE_DEVICES=0 python -m stalestream.paraphrase --episodes $D/episodes_v1_raw/train_2s.jsonl --out $D/episodes_v1/train_2s.jsonl
cp $D/episodes_v1_raw/{value_aliases,meta}.json $D/episodes_v1/
# (steps 2-5 below: substitute episodes_v1 for episodes_v0)
# 2. prompted LLM writer baseline (GPU 0; add --model Qwen/Qwen3-4B --arm prompted_4b for the 4B writer)
CUDA_VISIBLE_DEVICES=0 python -m stalestream.writer --episodes $D/episodes_v0/test.jsonl --out $S/runs/v0_writer_1.7b.jsonl
# 3. reader over rule arms + writer memories (GPU 1)
CUDA_VISIBLE_DEVICES=1 python -m stalestream.reader --episodes $D/episodes_v0/test.jsonl \
  --aliases $D/episodes_v0/value_aliases.json --mquake $D/MQuAKE-CF-3k-v2.json \
  --arms oracle no_memory write_all newest_wins symbolic prompted_1.7b \
  --memories $S/runs/v0_writer_1.7b.jsonl --out $S/runs/v0_eval.jsonl
# 4. gate
python headroom_gate.py $S/runs/v0_eval.jsonl --baseline newest_wins --baseline write_all \
  --baseline symbolic --baseline prompted_1.7b
# 5. GRPO timing (reader server on GPU 1, writer on GPU 0)
CUDA_VISIBLE_DEVICES=1 vllm serve Qwen/Qwen3-4B --port 8401 --max-model-len 2048 &
CUDA_VISIBLE_DEVICES=0 python -m stalestream.grpo --episodes $D/episodes_v0/train_2s.jsonl \
  --aliases $D/episodes_v0/value_aliases.json --steps 20 --algo grpo --out $S/runs/grpo_timing
```

## Modules
- `stalestream/generator.py`: episodes and label validation.
- `stalestream/baselines.py`: oracle (privileged), no_memory, write_all, newest_wins, symbolic resolver.
- `stalestream/writer.py`: prompted writer (also the RL policy prompt).
- `stalestream/reader.py`: frozen Qwen3-4B reader and EM scoring; output feeds the gate.
- `stalestream/grpo.py`: multi-session GRPO/RLOO with LoRA, vLLM rollouts, reader server.

Not yet built: BM25 arm, prompted Qwen3-32B writer, consistency-check defense, privileged resolver, keep/drop controller, RFT, injections, held-out readers.
