"""Run a block of ss.py variants one after another (foreground), then print val per run.
usage: python3 drive.py "<base flags>" <tagprefix> <kind:lr> ...
kinds: down0/down1/down2/down5 (safe recipe, then decrease-only while c < -tau, tau = 0/0.01/0.02/0.05), tie (Adam rate also takes s), arule (own Adam multiplier), const, lin (constant rate, linear decay), safe (the safe recipe), dadapt, prodigy, mechanic, rule (adapt to cooldown)
The safe recipe's gain and hold point are computed from the base flags: eta = sqrt(width/32), hold at min(30% of steps, 450).
"""
import json, math, shlex, subprocess, sys

base, pre, items = sys.argv[1], sys.argv[2], sys.argv[3:]
b = shlex.split(base)
def get(flag, d):
    return float(b[b.index(flag) + 1]) if flag in b else d
width, steps = get("--width", 64), int(get("--steps", 200))
eta = round(math.sqrt(width / 32), 3); hold = min(int(0.3 * steps), 450)
extra = {
    "const": [], "lin": ["--sched", "lin"],
    "safe": ["--rule", "mult", "--sig", "hyper", "--gran", "glob", "--eta", str(eta), "--gsched", "sched", "--freeze_at", str(hold)],
    "safelin": ["--sched", "lin", "--rule", "mult", "--sig", "hyper", "--gran", "glob", "--eta", str(eta), "--gsched", "sched", "--freeze_at", str(hold)],
    "down0": None, "down1": None, "down2": None, "down5": None,
    "rule": ["--rule", "mult", "--sig", "hyper", "--gran", "glob", "--eta", "1"],
    "dadapt": ["--lrfree", "dadapt"], "prodigy": ["--lrfree", "prodigy"], "mechanic": ["--lrfree", "mechanic"],
}
for it in items:
    kind, lr = it.split(":")
    tag = f"{pre}-{kind}"
    kind, _, h = kind.partition("@")          # e.g. safelin@750 overrides the hold step
    if kind.startswith("dg") and kind[2:].isdigit():   # safe recipe, decreases dgain = digits times faster
        ex = extra["safe"] + ["--dgain", kind[2:]]
    elif kind.startswith("e") and kind[1:].isdigit():   # safe recipe with gain digits/100
        ex = list(extra["safe"]); ex[ex.index("--eta") + 1] = str(int(kind[1:]) / 100)
    elif kind.startswith("tp"):                # safe recipe with target +digits/1000 (steers to a lower rate)
        ex = extra["safe"] + ["--target", str(int(kind[2:]) / 1000)]
    elif kind.startswith("tg"):                # safe recipe with target -digits/1000
        ex = extra["safe"] + ["--target", str(-int(kind[2:]) / 1000)]
    elif kind.startswith("sd") and kind[2:].isdigit():   # safe recipe, then decrease-only while c < -(digits/10) x running sd of c
        ex = extra["safe"] + ["--post", "down", "--psd", str(int(kind[2:]) / 10)]
    elif kind.startswith("down"):              # safe recipe, then only decreases while c < -tau (tau = digit / 100)
        ex = extra["safe"] + ["--post", "down", "--ptau", str(int(kind[4:]) / 100)]
    elif kind.startswith("tie") or kind.startswith("arule") or kind.startswith("wauto"):
        ex = extra["safe"] + {"tie": ["--atie", "1"], "arule": ["--arule", "1", "--amat", "1"]}.get(kind, [])
    else: ex = list(extra[kind])
    if h: ex[ex.index("--freeze_at") + 1] = h
    cmd = ["nice", "-n", "20", "python3", "ss.py", "--threads", "1", "--wd", "1"] + b + ["--lr", lr, "--tag", tag] + ex
    subprocess.run(cmd, stdout=subprocess.DEVNULL, check=False)
    last = None
    for l in open("results.jsonl"):
        r = json.loads(l)
        if r["tag"] == tag and r["args"]["lr"] == float(lr): last = r
    s = last["scores"] if last else {}
    print(f"{tag:26s} lr {lr:<8} val {s.get('val', 'NA')}  peak {s.get('peak_rate', '')}  {last.get('train_s', '') if last else ''}s", flush=True)
