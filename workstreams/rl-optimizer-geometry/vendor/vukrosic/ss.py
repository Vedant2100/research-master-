"""Muon that sets its own step size. Tiny modern transformer test bed; one run = one JSON line in results.jsonl.
Each Muon matrix keeps a log step-size multiplier log_s. Every step it measures the cosine between this step's
signal and last step's signal and moves log_s up when the cosine is above --target and down when it is below.
usage: python3 ss.py --threads 1 --tag base                       (plain Muon, constant rate with warmup/cooldown)
       python3 ss.py --threads 1 --rule mult --sig upd --lr 0.2   (self-step from a 10x too high start)
"""
import argparse, json, math, os, time
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F

p = argparse.ArgumentParser()
p.add_argument("--width", type=int, default=64); p.add_argument("--layers", type=int, default=4); p.add_argument("--heads", type=int, default=4)
p.add_argument("--V", type=int, default=2000); p.add_argument("--L", type=int, default=64); p.add_argument("--batch", type=int, default=16)
p.add_argument("--steps", type=int, default=200); p.add_argument("--lr", type=float, default=0.02); p.add_argument("--elr", type=float, default=0.04)
p.add_argument("--warm", type=float, default=0.05, help="warmup share of steps"); p.add_argument("--cool", type=float, default=0.3, help="cooldown share")
p.add_argument("--sched", default="wsd", help="wsd: warmup, flat, linear cooldown | cos: warmup then cosine decay to 0 | lin: warmup then linear decay to 0")
p.add_argument("--wd", type=float, default=0.0, help="decoupled weight decay on Muon matrices (times lr)")
# --- the self-step rule ---
p.add_argument("--rule", default="none", help="none | mult | sign | add | rand (mult with a random sign instead of the alignment)")
p.add_argument("--sig", default="upd", help="upd: orthogonalized update | grad: raw gradient | mom: momentum | hyper: gradient vs previous update | path: gradient vs decayed sum of past updates | path100 | disp: gradient vs displacement from init W0 - W")
p.add_argument("--gran", default="mat", help="mat: one step size per matrix | row: one per output row | glob: one for all Muon matrices")
p.add_argument("--eta", type=float, default=0.05, help="log step-size change per unit of (cos - target)")
p.add_argument("--gsched", default="none", help="gain schedule of the rule: none | lin (eta falls linearly to 0 at the end of adaptation) | sqrt (eta / sqrt(t/20))")
p.add_argument("--target", type=float, default=0.0, help="cosine the rule steers to")
p.add_argument("--lo", type=float, default=1e-3); p.add_argument("--hi", type=float, default=1e3)
p.add_argument("--eta2", type=float, default=0.0, help="gran both: rate of each matrix's offset from the global scale")
p.add_argument("--relmax", type=float, default=16.0, help="gran both: bound on each matrix's offset (factor)")
p.add_argument("--kmult", default="", help="fixed rate multiplier per matrix kind, e.g. q=4,k=4,v=0.5")
p.add_argument("--qknorm", type=int, default=1, help="1: RMSNorm on q and k per head; 0: off")
p.add_argument("--adapt_start", type=int, default=0, help="start adapting at this step")
p.add_argument("--freeze_at", type=int, default=-1, help="stop adapting after this step (control)")
p.add_argument("--post", default="none", help="after --freeze_at until the cooldown: none (hold) | down (glob rule may only lower s: log s += eta * min(0, c - target + ptau))")
p.add_argument("--mwarm", type=int, default=1, help="0 = no warmup ramp on Muon (Adam keeps its warmup); the rule's gain is then 1 from step 0")
p.add_argument("--dgain", type=float, default=1.0, help="glob rule: multiply decreases of log s by this factor during adaptation (asymmetric gain)")
p.add_argument("--ptau", type=float, default=0.0, help="--post down: cosine margin; s falls only while c < target - ptau")
p.add_argument("--psd", type=float, default=0.0, help="--post down: if > 0, margin = psd x running standard deviation of the per-step cosine (EMA 0.99), instead of --ptau")
p.add_argument("--adapt_end", type=float, default=-1, help="stop adapting at this share of training (default: start of cooldown)")
p.add_argument("--pdecay", type=float, default=0.9, help="decay of the update path sum used by --sig path")
p.add_argument("--ema", type=float, default=0.0, help="smooth the cosine with this EMA factor before using it")
p.add_argument("--mom", type=float, default=0.95)
p.add_argument("--lrfree", default="none", help="learning-rate-free baselines in the shared-multiplier slot: none | dadapt | prodigy | mechanic (Muon matrices)")
p.add_argument("--d0", type=float, default=-1, help="dadapt/prodigy: initial rate estimate (default: --lr)")
p.add_argument("--arule", type=int, default=0, help="1 = the same rule drives one shared multiplier on Adam's rate (embedding, head, norms)")
p.add_argument("--aeta", type=float, default=1.0, help="gain of the Adam-side rule")
p.add_argument("--amat", type=int, default=0, help="1 = Adam-side signal from the 2-D Adam tensors only (embedding, head); norm gains follow")
p.add_argument("--atie", type=int, default=0, help="1 = Adam's rate also takes the Muon multiplier s (fixed Adam/Muon rate ratio)")
p.add_argument("--anorm", type=float, default=0.0, help=">0: Adam-side step = anorm * c / running RMS of c (scale-free signal)")
p.add_argument("--abeta", type=float, default=0.0, help="Adam-side signal uses a decayed sum of past steps (beta) instead of the last step")
p.add_argument("--mnorm", type=float, default=0.0, help=">0: Muon signal divided by its running RMS and multiplied by mnorm (width-free speed)")
p.add_argument("--atarget", type=float, default=0.0, help="target of the Adam-side rule")
p.add_argument("--aglob", type=int, default=0, help="1 = Adam-side signal is one cosine over all Adam parameters together (exact sign of dL/ds); 0 = mean of per-tensor cosines")
p.add_argument("--gcap", type=float, default=0.0, help="cap on |change of log s| per step (0 = off)")
p.add_argument("--shuffle", type=int, default=1, help="1 = shuffle the training windows (0 = consecutive text, consecutive batches share documents)")
p.add_argument("--diag", type=int, default=0, help="1 = record the mean cosine of every signal per matrix over the flat phase")
p.add_argument("--log", type=int, default=0, help="evaluate every N steps (curve)"); p.add_argument("--slog", type=int, default=20, help="log step sizes every N steps")
p.add_argument("--save", default=""); p.add_argument("--out", default="results.jsonl")
p.add_argument("--threads", type=int, default=1); p.add_argument("--dev", default="cpu"); p.add_argument("--tag", default="")
a = p.parse_args()
torch.set_num_threads(a.threads); torch.manual_seed(0)
DEV = torch.device(a.dev)
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, "data"); EOT = 50256

# ---------------- data: FineWeb GPT-2 tokens, rare tokens mapped to one unknown token ----------------
train_tok = np.fromfile(os.path.join(DATA, "fineweb_train_000001.slice"), dtype=np.uint16, offset=1024).astype(np.int64)
val_tok = np.fromfile(os.path.join(DATA, "fineweb_val_000000.slice"), dtype=np.uint16, offset=1024).astype(np.int64)
counts = np.bincount(train_tok, minlength=65536)
keep = np.unique(np.concatenate([np.argsort(counts)[-(a.V - 2):], [EOT]])); V = len(keep) + 1; UNK = V - 1
look = np.full(65536, UNK, np.int64); look[keep] = np.arange(len(keep))
need = a.steps * a.batch * a.L
assert need <= len(train_tok), "not enough tokens"
rows = look[train_tok[:need].reshape(-1, a.L)]
if a.shuffle: rows = rows[np.random.default_rng(0).permutation(len(rows))]   # real training shuffles: consecutive batches share no documents
val = look[np.stack([val_tok[x:x + a.L] for x in np.linspace(0, len(val_tok) - a.L - 1, 400).astype(np.int64)])]


# ---------------- model: RMSNorm, RoPE, QK-norm, SwiGLU, no biases, untied head ----------------
def rope(x):
    t, d = x.shape[-2], x.shape[-1]
    f = 1.0 / 10000 ** (torch.arange(0, d, 2, device=x.device).float() / d); ang = torch.outer(torch.arange(t, device=x.device).float(), f)
    c, s = ang.cos(), ang.sin(); x1, x2 = x[..., 0::2], x[..., 1::2]
    return torch.stack([x1 * c - x2 * s, x1 * s + x2 * c], -1).flatten(-2)


class Block(nn.Module):
    def __init__(s, d, H):
        super().__init__(); s.H, s.dk = H, d // H
        s.n1, s.n2, s.qn, s.kn = nn.RMSNorm(d), nn.RMSNorm(d), *((nn.RMSNorm(d // H), nn.RMSNorm(d // H)) if a.qknorm else (nn.Identity(), nn.Identity()))
        s.q, s.k, s.v, s.o = (nn.Linear(d, d, bias=False) for _ in range(4))
        f = int(8 * d / 3) // 8 * 8; s.gate, s.up, s.down = nn.Linear(d, f, bias=False), nn.Linear(d, f, bias=False), nn.Linear(f, d, bias=False)

    def forward(s, x):
        b, t, d = x.shape; h = s.n1(x); sp = lambda z: z.view(b, t, s.H, s.dk).transpose(1, 2)
        q, k = rope(s.qn(sp(s.q(h)))), rope(s.kn(sp(s.k(h))))
        y = F.scaled_dot_product_attention(q, k, sp(s.v(h)), is_causal=True)
        x = x + s.o(y.transpose(1, 2).reshape(b, t, d)); h = s.n2(x)
        return x + s.down(F.silu(s.gate(h)) * s.up(h))


class Model(nn.Module):
    def __init__(s, V, d, nl, H):
        super().__init__(); s.emb = nn.Embedding(V, d); nn.init.normal_(s.emb.weight, std=d ** -0.5)
        s.blocks = nn.ModuleList(Block(d, H) for _ in range(nl)); s.norm = nn.RMSNorm(d); s.head = nn.Linear(d, V, bias=False)

    def forward(s, ids):
        x = s.emb(ids)
        for blk in s.blocks: x = blk(x)
        return s.head(s.norm(x))


# ---------------- optimizer: Muon on block matrices (with the self-step rule), Adam on the rest ----------------
def newton_schulz(G, steps=5):
    A, B, C = 3.4445, -4.7750, 2.0315; X = G / (G.norm() + 1e-7); tr = X.shape[0] > X.shape[1]
    if tr: X = X.T
    for _ in range(steps): M = X @ X.T; X = A * X + (B * M + C * M @ M) @ X
    return X.T if tr else X


def cosine(x, y, rowwise):
    if rowwise: return (x * y).sum(1) / (x.norm(dim=1) * y.norm(dim=1) + 1e-12)
    return (x * y).sum() / (x.norm() * y.norm() + 1e-12)


class Muon(torch.optim.Optimizer):
    def __init__(s, named, lr):
        s.names = [n for n, _ in named]; super().__init__([w for _, w in named], dict(lr=lr))
        s.t = 0; s.adapt = True; s.post = False; s.gain = 1.0; s.diag_on = False; s.gls = torch.zeros(()); s.mrms = None; s.gen = torch.Generator().manual_seed(3)
        km = dict((k, float(v)) for k, v in (x.split('=') for x in a.kmult.split(',') if x)); s.km = {id(w): km.get(n.split('.')[-1], 1.0) for n, w in named}

    @torch.no_grad()
    def step_free(s):
        """D-Adaptation / Prodigy / Mechanic adapted to Muon: one shared scale for all Muon matrices.
        dadapt/prodigy: Muon is steepest descent in the spectral norm, so the distance bound uses the dual (nuclear) norm:
          d_hat = sum_i lam_i <g_i, W0 - W_i> / ||sum_i lam_i g_i||_*  (summed over matrices), d = max(d, d_hat), step = d * sched * O.
        mechanic: W = W0 + S * Delta, Delta = sum of base Muon steps (rate --lr), S from Mechanic's online tuner (6 betas)."""
        g0 = s.param_groups[0]; sch = g0["lr"] / a.lr
        if not hasattr(s, "fd"):
            s.fd = a.d0 if a.d0 > 0 else a.lr; s.fr = 0.0
            s.mb = torch.tensor([0.9, 0.99, 0.999, 0.9999, 0.99999, 0.999999], dtype=torch.float64)
            s.mm = torch.zeros(6, dtype=torch.float64); s.mv = torch.zeros(6, dtype=torch.float64); s.mr = torch.zeros(6, dtype=torch.float64)
            s.ms = torch.zeros(6, dtype=torch.float64)
        ws = g0["params"]; items = []
        for w in ws:
            st = s.state[w]
            if not st: st["m"] = torch.zeros_like(w); st["w0"] = w.detach().clone(); st["S"] = torch.zeros_like(w); st["D"] = torch.zeros_like(w)
            m = st["m"]; gr = w.grad; m.mul_(a.mom).add_(gr)
            O = newton_schulz(gr + a.mom * m) * max(1, w.shape[0] / w.shape[1]) ** 0.5
            items.append((w, st, gr, O))
        if a.lrfree in ("dadapt", "prodigy"):
            d = s.fd; eta = d * sch
            num = sum(float((gr * (st["w0"] - w)).sum()) for w, st, gr, O in items)
            if a.lrfree == "dadapt":
                lam = d * sch; s.fr += lam * num
                for w, st, gr, O in items: st["S"].add_(gr, alpha=lam)
            else:
                b = 0.999 ** 0.5; lam = (1 - b) * sch * d * d; s.fr = b * s.fr + lam * num
                for w, st, gr, O in items: st["S"].mul_(b).add_(gr, alpha=lam)
            den = sum(float(torch.linalg.svdvals(st["S"]).sum()) for w, st, gr, O in items)
            if den > 0: s.fd = max(s.fd, s.fr / den)
            for w, st, gr, O in items:
                if a.wd: w.mul_(1 - a.wd * eta)
                w.add_(O, alpha=-eta)
            s.gls = torch.tensor(math.log(max(s.fd, 1e-12) / a.lr))
        else:   # mechanic
            lam_reg = 0.01; Ssum = float(s.ms.sum())
            gn = math.sqrt(sum(float(gr.pow(2).sum()) for w, st, gr, O in items)); xn = math.sqrt(sum(float(w.pow(2).sum()) for w, st, gr, O in items))
            h = sum(float((st["D"] * (gr + lam_reg * Ssum * gn / (xn + 1e-12) * w)).sum()) for w, st, gr, O in items)
            s.mm = torch.maximum(s.mb * s.mm, torch.tensor(abs(h), dtype=torch.float64)); s.mv = s.mb ** 2 * s.mv + h * h
            s.mr = (s.mb * s.mr - s.ms * h).clamp(min=0); W = 1e-8 / 6 * s.mm + s.mr; s.ms = W / (s.mv.sqrt() + 1e-8)
            Snew = float(s.ms.sum())
            for w, st, gr, O in items:
                st["D"].add_(O * a.lr * sch + a.wd * a.lr * sch * w, alpha=-1)
                w.copy_(st["w0"] + Snew * st["D"])
            s.gls = torch.tensor(math.log(max(Snew, 1e-12)))
        s.t += 1

    @torch.no_grad()
    def step(s):
        if a.lrfree != "none": return s.step_free()
        rowwise = a.gran == "row"; gcos = []
        for g in s.param_groups:
            for w in g["params"]:
                st = s.state[w]
                if not st:
                    st["m"] = torch.zeros_like(w); st["ls"] = torch.zeros(w.shape[0] if rowwise else ())
                    st["prev"] = None; st["c"] = None; st["clog"] = 0.0; st["w0"] = w.detach().clone()
                m = st["m"]; gr = w.grad
                m.mul_(a.mom).add_(gr); O = newton_schulz(gr + a.mom * m)
                pv = st.get("pv")                       # previous O, g, m and the two path sums
                if pv is not None:
                    pairs = {"upd": (O, pv[0]), "grad": (gr, pv[1]), "mom": (m, pv[2]), "hyper": (gr, pv[0]),
                             "path": (gr, pv[3]), "path100": (gr, pv[4]), "disp": (gr, st["w0"] - w)}
                    if a.rule != "none":
                        x, y = pairs[a.sig]; c = cosine(x, y, rowwise)
                        if a.ema > 0: c = c if st["c"] is None else a.ema * st["c"] + (1 - a.ema) * c
                        st["c"] = c; st["clog"] = float(c.mean())
                        if s.adapt or s.post:
                            d = (c - a.target) * s.gain
                            if a.rule == "mult": step = a.eta * d
                            elif a.rule == "sign": step = a.eta * torch.sign(d)
                            elif a.rule == "rand":
                                r = torch.randint(0, 2, d.shape if d.ndim else (), generator=s.gen).float() * 2 - 1
                                step = a.eta * r * d.abs()
                            if a.gran in ("glob", "both"): gcos.append(d); st["d"] = d
                            elif a.rule == "add":
                                sc = torch.exp(st["ls"]) + a.eta * d; st["ls"] = torch.log(sc.clamp(min=a.lo))
                            else: st["ls"] = st["ls"] + step
                            st["ls"] = st["ls"].clamp(math.log(a.lo), math.log(a.hi))
                    if a.diag and s.diag_on:
                        cs = [float(cosine(x, y, False)) for x, y in pairs.values()]
                        acc = st.setdefault("dacc", [0.0] * 7 + [0]); acc[:7] = [u + v for u, v in zip(acc[:7], cs)]; acc[7] += 1
                P = O.clone() if pv is None else a.pdecay * pv[3] + O
                Q = O.clone() if pv is None else 0.99 * pv[4] + O
                st["pv"] = (O.clone(), gr.clone(), m.clone(), P, Q)
                ls = s.gls if a.gran == "glob" else (s.gls + st["ls"]) if a.gran == "both" else st["ls"]
                scale = torch.exp(ls) * s.km[id(w)]
                lr = g["lr"] * max(1, w.shape[0] / w.shape[1]) ** 0.5
                if a.wd: w.mul_(1 - a.wd * g["lr"] * (float(scale.mean()) if scale.ndim else float(scale)))
                if rowwise: w.add_(-lr * scale[:, None] * O)
                else: w.add_(O, alpha=-lr * float(scale))
        if gcos and (s.adapt or s.post):
            d = torch.stack(gcos).mean()
            s.cm = 0.99 * getattr(s, "cm", float(d)) + 0.01 * float(d); s.cv = 0.99 * getattr(s, "cv", 0.0) + 0.01 * (float(d) - s.cm) ** 2
            if a.rule == "rand": d = d.abs() * (torch.randint(0, 2, (), generator=s.gen).float() * 2 - 1)
            if a.mnorm > 0:
                s.mrms = float(d) ** 2 if s.mrms is None else 0.99 * s.mrms + 0.01 * float(d) ** 2
                d = d / (math.sqrt(s.mrms) + 1e-12) * a.mnorm
            dl = a.eta * torch.sign(d) if a.rule == "sign" else a.eta * d
            if a.dgain != 1.0 and s.adapt and float(dl) < 0: dl = dl * a.dgain   # asymmetric: falls dgain times faster than rises
            if s.post and not s.adapt: dl = (a.eta * (d + (a.psd * math.sqrt(s.cv) if a.psd > 0 else a.ptau))).clamp(max=0.0)
            if a.gcap > 0: dl = dl.clamp(-a.gcap, a.gcap)
            s.gls = (s.gls + dl).clamp(math.log(a.lo), math.log(a.hi))
            if a.gran == "both":
                for g in s.param_groups:
                    for w in g["params"]:
                        st = s.state[w]
                        if "d" in st: st["ls"] = (st["ls"] + a.eta2 * (st["d"] - d)).clamp(-math.log(a.relmax), math.log(a.relmax))
        s.t += 1

    def diag(s):
        out = {}
        for n, w in zip(s.names, s.param_groups[0]["params"]):
            acc = s.state[w].get("dacc")
            if acc and acc[7]: out[n] = [round(x / acc[7], 4) for x in acc[:7]]
        return out

    def scales(s):
        out = {}
        for n, w in zip(s.names, s.param_groups[0]["params"]):
            st = s.state.get(w, {}); ls = s.gls if (a.gran == "glob" or a.lrfree != "none") else (s.gls + st.get("ls", torch.zeros(()))) if a.gran == "both" else st.get("ls", torch.zeros(()))
            out[n] = [round(float(torch.exp(ls).mean()), 4), round(st.get("clog", 0.0), 4)]
        return out


@torch.no_grad()
def evaluate(m):
    m.eval(); x = torch.tensor(val, device=DEV); tot = 0.0
    for i in range(0, len(x), 100):
        xb = x[i:i + 100]; tot += F.cross_entropy(m(xb[:, :-1]).reshape(-1, V).float(), xb[:, 1:].reshape(-1), reduction="sum").item()
    m.train(); return tot / (len(x) * (a.L - 1))


def main():
    m = Model(V, a.width, a.layers, a.heads).to(DEV)
    named = [(n.replace("blocks.", "b").replace(".weight", ""), w) for n, w in m.named_parameters() if w.ndim == 2 and n.startswith("blocks")]
    mats = [w for _, w in named]
    rest = [w for w in m.parameters() if all(w is not z for z in mats)]
    mu = Muon(named, a.lr); ad = torch.optim.Adam(rest, lr=a.elr, betas=(0.9, 0.95))
    opts = [mu, ad]; base = [a.lr, a.elr]
    wsteps = max(1, int(a.warm * a.steps)); cstart = int((1 - a.cool) * a.steps)
    aend = int(a.adapt_end * a.steps) if a.adapt_end >= 0 else cstart
    curve, slog, loss_ema, diverged = [], [], None, False
    acs, agc = [], []
    arms = None
    als, aprev, olds, peak, runmin, spike, lcurve = 0.0, [None] * len(rest), None, 0.0, 1e9, 0.0, []
    t0 = time.time()
    for step in range(a.steps):
        if a.sched == "wsd": sc = min((step + 1) / wsteps, 1.0, (a.steps - step) / max(1, a.steps - cstart))
        else:
            fr = max(0.0, (step - wsteps) / max(1, a.steps - wsteps))
            sc = min((step + 1) / wsteps, 0.5 * (1 + math.cos(math.pi * fr)) if a.sched == "cos" else 1 - fr)
        scm = sc if a.mwarm or step >= wsteps else min(1.0, (a.steps - step) / max(1, a.steps - cstart))   # Muon schedule without warmup
        for o, bl, f in zip(opts, base, (scm, sc)):
            for g in o.param_groups: g["lr"] = bl * f
        mu.diag_on = wsteps <= step < cstart
        mu.gain = {"none": 1.0, "lin": max(0.0, 1 - step / max(1, aend)), "sqrt": 1 / math.sqrt(max(1.0, step / 20)), "sched": scm}[a.gsched]
        mu.adapt = a.adapt_start <= step < aend and (a.freeze_at < 0 or step < a.freeze_at)
        mu.post = a.post == "down" and a.freeze_at >= 0 and a.freeze_at <= step < cstart
        x = torch.tensor(rows[step * a.batch:(step + 1) * a.batch], device=DEV)
        loss = F.cross_entropy(m(x[:, :-1]).reshape(-1, V).float(), x[:, 1:].reshape(-1))
        if not torch.isfinite(loss): diverged = True; break
        loss.backward()
        if a.arule:
            with torch.no_grad():
                cs = [float(cosine(w.grad, pv, False)) for w, pv in zip(rest, aprev) if pv is not None and w.grad is not None]
                if cs and wsteps <= step < cstart:
                    acs.append(cs)
                if cs and a.aglob:
                    pr = [(w.grad, pv) for w, pv in zip(rest, aprev) if pv is not None and w.grad is not None]
                    cg = sum(float((x * y).sum()) for x, y in pr) / (math.sqrt(sum(float(x.pow(2).sum()) for x, _ in pr) * sum(float(y.pow(2).sum()) for _, y in pr)) + 1e-12)
                    cs = [cg]
                    if wsteps <= step < cstart: agc.append(cg)
                if cs and a.amat and not a.aglob:
                    cs = [float(cosine(w.grad, pv, False)) for w, pv in zip(rest, aprev) if pv is not None and w.grad is not None and w.ndim == 2]
                if cs and mu.adapt:
                    dl = a.aeta * (float(np.mean(cs)) - a.atarget) * mu.gain
                    if a.anorm > 0:
                        cm = float(np.mean(cs)) - a.atarget
                        arms = cm * cm if arms is None else 0.99 * arms + 0.01 * cm * cm
                        dl = a.anorm * cm / (math.sqrt(arms) + 1e-12) * mu.gain
                    if a.gcap > 0: dl = max(-a.gcap, min(a.gcap, dl))
                    als = min(math.log(a.hi), max(math.log(a.lo), als + dl))
                for g in ad.param_groups: g["lr"] = a.elr * sc * math.exp(als)
                olds = [w.detach().clone() for w in rest]
        if a.atie:
            for g in ad.param_groups: g["lr"] = a.elr * sc * math.exp(als) * math.exp(float(mu.gls))
        for o in opts: o.step()
        if a.arule:
            stp = [o_ - w.detach() for w, o_ in zip(rest, olds)]   # the step taken, sign as Muon's O
            aprev = [x if (pv is None or a.abeta == 0) else a.abeta * pv + x for x, pv in zip(stp, aprev)]
        peak = max(peak, a.lr * sc * math.exp(float(mu.gls)) if (a.gran == "glob" or a.lrfree != "none") else 0.0)
        m.zero_grad(set_to_none=True)
        loss_ema = loss.item() if loss_ema is None else 0.95 * loss_ema + 0.05 * loss.item()
        if step >= 20: runmin = min(runmin, loss_ema); spike = max(spike, loss_ema - runmin)
        if step % 10 == 0: lcurve.append(round(loss_ema, 4))
        if a.slog and (step % a.slog == 0 or step == a.steps - 1):
            sl = mu.scales()
            if a.arule: sl["adam"] = [round(math.exp(als), 4), 0.0]
            slog.append([step, sl])
        if a.log and (step + 1) % a.log == 0 and step + 1 < a.steps: curve.append([step + 1, round(evaluate(m), 4)])
    train_s = round(time.time() - t0, 2)
    v = evaluate(m) if not diverged else float("nan")
    if not math.isfinite(v): v = 99.0
    r = dict(val=round(v, 4), train_ema=round(loss_ema or 99, 4), diverged=diverged, peak_rate=round(peak, 5), spike=round(spike, 4), lcurve=lcurve)
    if a.diag: r["diag"] = mu.diag()
    if acs:
        A = np.array(acs); rn = [n for n, w in m.named_parameters() if all(w is not z for z in mats)]
        r["adam_cos"] = dict(mean=round(float(A.mean()), 4), glob=round(float(np.mean(agc)), 4) if agc else None, **{n: round(float(A[:, i].mean()), 4) for i, n in enumerate(rn) if n in ("emb.weight", "head.weight", "norm.weight")})
    if curve: r["curve"] = curve + [[a.steps, round(v, 4)]]
    nparam = sum(w.numel() for w in m.parameters())
    res = dict(tag=a.tag, args=vars(a), params=nparam, body_params=sum(w.numel() for w in mats), tokens=need,
               tok_per_weight=round(need / nparam, 2), train_s=train_s, scores=r, slog=slog)
    if a.save:
        os.makedirs(os.path.join(HERE, "runs"), exist_ok=True); torch.save(m.state_dict(), os.path.join(HERE, "runs", a.save + ".pt"))
    with open(os.path.join(HERE, a.out), "a") as f: f.write(json.dumps(res) + "\n")
    fin = slog[-1][1] if slog else {}
    gm = math.exp(np.mean([math.log(max(v_[0], 1e-9)) for k_, v_ in fin.items() if k_ != 'adam'])) if fin else 1
    if a.arule: print('adam scale', fin.get('adam'), r.get('adam_cos'), end=' ')
    print(f"{a.tag or 'run'}: val {v:.4f} spike {spike:.4f} peak {peak:.4f} train {train_s}s params {nparam/1e6:.2f}M tpw {res['tok_per_weight']} final-scale-geomean {gm:.3f}", flush=True)


if __name__ == "__main__":
    main()
