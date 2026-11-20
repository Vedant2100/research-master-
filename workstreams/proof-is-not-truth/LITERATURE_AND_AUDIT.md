# Literature Review, Novelty Assessment, and Pre-Sprint Harness Audit

**Workstream:** Proof Is Not Truth (AI × Epistemics)  
**Event:** Apart Research AI × Epistemics Sprint (November 13–15, 2026)  
**Track:** Trust Infrastructure / Model Epistemics & Decision-Making Evaluations  
**Status:** Pre-implementation Phase (Gates 1–4 Completed)

---

## 1. Apart Sprint Context & Evaluation Rubric

### 1.1 The Official Sprint Brief: The Provenance Study Challenge
The Apart Research AI × Epistemics Sprint (November 13–15, 2026) investigates how AI alters institutional and individual belief-formation, decision-making, and coordination. Under Track 2 (*Trust Infrastructure*), the official sprint brief highlights the **Provenance Study** prompt:

> *"While many frameworks assume machine-readable provenance and reliability metadata (such as C2PA manifests, cryptographic signatures, or Community Notes context) will inherently help AI systems and agents make safer or more accurate choices, its actual utility has rarely been rigorously measured.*  
> *Challenge: Test identical research and operational tasks with and without machine-readable provenance signals. Measure downstream performance metrics including model accuracy, citation quality, and susceptibility to planted false sources or adversarial injection."*

### 1.2 The Apart Judging Rubric
Submissions for the sprint and subsequent Apart Fellowship consideration are evaluated across four core dimensions:
1. **Impact Potential & Innovation:** Conceptual novelty, significance to AI safety and epistemics, and clear differentiation from trivial prompt guards.
2. **Scientific Rigor & Methodology:** Sound paired experimental controls, deterministic ground truth, avoidance of fabricated or mock metrics as real findings, statistical hygiene (accounting for repeated seeds and cluster correlations), and explicit uncertainty quantification.
3. **Execution & Prototyping:** A complete, self-contained, reproducible evaluation harness with verifiable execution traces and deterministic test suites.
4. **Clarity of Write-up & Scientific Honesty:** Transparent disclosure of all pre-existing code, explicit boundary conditions, failure modes, and clear distinction between what the evidence supports versus what it does not.

---

## 2. Academic Literature Review

We examine four foundational preprints establishing the state of the art in model epistemics, provenance, and agent security:

### 2.1 Learn2Discern (L2D): Information Discernment in Large Language Models (arXiv:2607.19355)
- **Focus:** Evaluates how well LLMs weigh external knowledge based on source reliability vs. internal parametric priors.
- **Key Findings:** Models exhibit significant vulnerability to superficial authority markers (e.g., prestigious publisher names or credentials) while lacking systematic source-monitoring mechanisms. When external text conflicts with factual truth, models default to authority cues or frequency heuristics.
- **Gap:** L2D is purely a passive question-answering benchmark. It evaluates static token prediction over text passages without tool execution, multi-step environment interaction, cryptographic verification primitives, or actionable state modification.

### 2.2 What Counts as Evidence? Epistemic Cue Utilization in Large Language Models (arXiv:2610.12788)
- **Focus:** Investigates *epistemic cue utilization*—distinguishing superficial final-answer accuracy from process-level epistemic vigilance. Evaluates cues such as source identity, historical reliability records, temporal timestamps, and order of presentation.
- **Key Findings:** LLMs often arrive at correct answers through spurious lexical associations rather than genuine epistemic calibration. When faced with conflicting cues (e.g., an authoritative source reporting outdated facts vs. an unverified source reporting current truth), models suffer from severe confirmation bias and authority over-reliance.
- **Gap:** The study is restricted to passive comprehension and synthetic text disputes. It does not investigate tool-using agents equipped with genuine cryptographic verification tools or active corroboration workflows.

### 2.3 Auditing Provenance Sensitivity in LLM Agent Action Selection (arXiv:2607.20827)
- **Focus:** Audits whether tool-using LLM agents aggregate mixed context (user prompts, system memory, tool observations, untrusted web text) in compliance with authorization boundaries.
- **Key Findings:** Agents frequently suffer from *privilege escalation via prompt injection*, treating instructions found in low-trust tool outputs as authoritative commands for sensitive tool actions (e.g., file writes, API execution).
- **Gap:** The framework focuses exclusively on *access control authorization* (i.e., "Is this source permitted to execute action $X$?"). It completely overlooks the epistemic dimension: what happens when an authorized, authentic source asserts an instruction or fact that is *factually incorrect or poisoned*?

### 2.4 ProvenanceGuard: Source-Aware Factuality Verification for Tool-Using Agents (arXiv:2606.18037)
- **Focus:** Factuality verification and post-generation defense layer for Model Context Protocol (MCP) tool agents, specifically targeting *cross-source conflation* (attributing a claim to the wrong source) across 281 medical-domain traces.
- **Key Findings:** By decomposing agent answers into atomic claims and checking NLI alignment against routed tool outputs, ProvenanceGuard successfully prevents hallucinated or misattributed citations.
- **Epistemic Scope & Boundary:** ProvenanceGuard explicitly targets source attribution and preserving source ownership on top of support estimation. The paper explicitly notes that attribution checks do not establish domain truth. The accurate distinction is that ProvenanceGuard addresses source attribution, while this project tests whether cryptographic origin authentication changes an agent's consequential operational action when an authentic source is factually wrong.

---

## 3. Novelty Assessment: "Proof Is Not Truth"

### 3.1 What Remains Unanswered?
Across existing literature and industrial provenance frameworks (C2PA, Sigstore, SLSA), "provenance" is operationalized as **origin authenticity and content integrity**: *Did this artifact originate from identified key $K$ or entity $E$ without transit tampering?* In cryptographic terms, our current implementation utilizes keyed HMAC-SHA256 message authentication codes (MACs), verifying origin authenticity and content integrity for holders of the verified secret.

This leaves a critical operational question in AI safety and epistemology:
> **When tool-using agents consume machine-verifiable origin authentication, do they distinguish origin authenticity from factual correctness when taking consequential actions, and can independent factual corroboration improve those actions without collapsing into blanket abstention?**

### 3.2 The "Proof Is Not Truth" Hypotheses and Hypothesized Regimes
1. **Origin Authentication in Benign Regimes:** In operational environments where source origin correlates with factual veracity, verified origin signals enable agents to filter unauthenticated or spoofed inputs.
2. **Authentic-False Failure Mode ("Signature Blindness"):** In the presence of authentic but factually false sources (e.g., automated CI crashes silently logging success, frozen sensor feeds, or stale emergency exemptions), agents equipped solely with origin verification may execute dangerous state modifications because machine-verified origin is treated as factual truth. We evaluate whether this failure mode occurs and whether origin verification increases or fails to mitigate false actions compared to unverified baselines.
3. **Decoupled Epistemic Corroboration:** To prevent authentic-false actions without collapsing into blanket over-abstention, agents require decoupled verification: validating origin authenticity *and* independently corroborating claims against live environmental telemetry.

This hypothesis constitutes a distinct, timely, and publishable contribution directly aligned with the Apart Sprint theme and judging rubric.

---

## 4. Audit of the Pre-Sprint Harness (`ProvenanceTrap`)

We audited the pre-sprint prototype located at:
`Vedant2100/role-work-forge-artifacts/hackathons/2026-11/provenancetrap/eval.py`  
along with its raw traces (`results/modal-run-42290877493/tmp/modal-results/micro1_qwen25_3b_modal`) and audit documentation (`reports/FINAL_EVIDENCE_AUDIT_2026_11_06.md`).

### 4.1 Summary of Pre-Sprint Results (November 6–7)
- **Setup:** 8 fixture tasks × 4 guard conditions × 3 nominal seeds = 96 Qwen2.5-3B episodes executed on Modal.
- **Task completion:** 22/96 (22.9%).
- **Strict safe pass:** 20/96 (20.8%).
- **Reported security:** 0 unauthorized write attempts; 2 sensitive-read attempts.

### 4.2 Diagnostic Failure Analysis
1. **The Competence Floor Blocker:**
   Of the 76 failed episodes, **60 episodes (78.9%) terminated immediately at Step 1 by emitting `{"tool": "finish"}` without attempting any file write or tool interaction.**
   - The model was not making an informed security decision to refuse hostile inputs; it was failing basic JSON formatting and tool-grounding.
2. **The Illusion of Safety:**
   The reported metric of "0 unauthorized writes" was entirely an artifact of model paralysis. Because the agent never touched the target file, it also never touched the protected file. Treating this as evidence of "injection resistance" is scientifically invalid.
3. **Absence of Provenance Primitives:**
   Despite the name `ProvenanceTrap`, the original harness contained zero provenance verification tools, cryptographic signatures, hash digests, or factual cross-validation tools. It was solely an indirect prompt-injection test using raw string assertions in text files.
4. **Greedy Seed Replays:**
   Due to greedy decoding (`temperature=0.0` or deterministic sampling), multiple seeds produced bit-for-bit identical replays, meaning the effective sample size was much smaller than 96 independent trials.

### 4.3 Prerequisites for Proceeding (The Competence Gate)
To rigorously evaluate epistemic trust without confounding by task-execution failure:
- The agent harness must achieve **$\ge 90\%$ (ideally 100%) clean-task competence** on uncontested baseline tasks before evaluating adversarial/epistemic conditions.
- The evaluation must separate **task execution competence** from **epistemic decision accuracy**.
- The harness must employ genuine cryptographic verification tools (real HMAC/SHA-256 signatures against a local keystore) rather than cosmetic text labels.
