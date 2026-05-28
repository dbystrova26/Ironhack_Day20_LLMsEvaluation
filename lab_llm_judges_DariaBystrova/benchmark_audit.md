# Benchmark Audit — Loan Rejection Letter Automation

**Scenario:** A bank wants to automate loan rejection letters. Letters must be clear, compliant, and empathetic.  
**Key concerns:** Accuracy of stated rejection reasons, regulatory tone compliance, and empathetic language.

---

## Benchmark Card 1: FinanceBench

**Benchmark Name:** FinanceBench  
**Year:** 2023  
**Source:** https://arxiv.org/abs/2311.11944

**Why it seemed relevant:**  
FinanceBench tests models on real financial documents — annual reports, earnings statements, and regulatory filings. Since loan rejection letters must cite accurate financial reasoning and comply with regulatory language, this benchmark tests whether a model understands financial facts and can reason about them correctly. It also covers document-grounded Q&A, which mirrors the task of generating a letter grounded in an applicant's financial profile.

**Contamination risk:**  
- [x] High — Model definitely saw this during training  
- Explanation: FinanceBench was released in late 2023 and uses publicly available financial documents (SEC filings). Most frontier models were trained on data that includes these filings and likely the benchmark itself, since it was widely discussed after release.

**Saturation risk:**  
- [x] Medium — Some models perform well  
- Explanation: Top models score 60–80% on FinanceBench, but accuracy drops significantly on multi-hop reasoning questions. It is not yet saturated but is approaching it for simpler question types.

**Format:**  
- [x] Free-form text (open-ended financial Q&A with document grounding)

**Verdict:**  
- [x] Adapt it (explain how)  
- Explanation: Rather than using raw FinanceBench Q&A pairs, adapt by grounding rejection letter generation in synthetic applicant profiles modeled after FinanceBench's financial document style. This preserves domain relevance while reducing contamination risk and tailoring evaluation to generation quality rather than retrieval accuracy.

---

## Benchmark Card 2: BBQ (Bias Benchmark for QA)

**Benchmark Name:** BBQ — Bias Benchmark for Question Answering  
**Year:** 2022  
**Source:** https://arxiv.org/abs/2110.08193

**Why it seemed relevant:**  
Loan rejection letters carry significant legal risk around discriminatory language. BBQ was designed to measure social biases across protected categories (race, gender, age, religion, disability, etc.) in model outputs. Since the Equal Credit Opportunity Act (ECOA) prohibits discrimination in credit decisions, evaluating whether the model produces biased rejection language is critical for regulatory compliance.

**Contamination risk:**  
- [x] Medium — Some overlap possible  
- Explanation: BBQ is a well-known academic benchmark and likely appears in training corpora, but its question format (bias detection in ambiguous scenarios) differs enough from letter generation that direct contamination is less impactful than in pure QA tasks.

**Saturation risk:**  
- [x] Medium — Some models perform well  
- Explanation: Large models score 80–90%+ on BBQ in accuracy, but bias scores (how often models default to stereotypes) remain inconsistent. It still discriminates between models on subtle bias dimensions.

**Format:**  
- [x] Multiple Choice (bias detection across demographic scenarios)

**Verdict:**  
- [x] Adapt it (explain how)  
- Explanation: Use BBQ's demographic category framework as a checklist for our custom evaluator rather than running it directly. Specifically, test whether rejection letters generated for synthetic applicants with identical financial profiles but different names (signalling race/gender) produce meaningfully different language — a bias audit built from BBQ's methodology.

---

## Benchmark Card 3: InstructEval

**Benchmark Name:** InstructEval  
**Year:** 2023  
**Source:** https://arxiv.org/abs/2306.04757

**Why it seemed relevant:**  
InstructEval evaluates how well instruction-tuned models follow complex, multi-constraint instructions — exactly what loan rejection letter generation requires (be clear AND compliant AND empathetic, include specific regulatory disclosures, avoid prohibited language). It measures instruction-following fidelity across dimensions like completeness, format adherence, and constraint satisfaction, which maps directly to our use case.

**Contamination risk:**  
- [x] Low — Model likely not trained on this data  
- Explanation: InstructEval uses procedurally generated instruction sets and was not widely circulated before 2023. The evaluation templates are less likely to appear verbatim in training data compared to static academic benchmarks.

**Saturation risk:**  
- [x] Low — Benchmark is challenging  
- Explanation: Multi-constraint instruction following remains genuinely hard. Even top models fail on 3+ simultaneous constraints, and compliance with domain-specific rules (like ECOA disclosures) is rarely tested in standard benchmarks.

**Format:**  
- [x] Free-form text (instruction-following with rubric-based scoring)

**Verdict:**  
- [x] Use it as-is  
- Explanation: InstructEval's multi-constraint rubric framework can be applied directly to loan rejection letter evaluation. Its scoring methodology (per-constraint pass/fail + aggregate score) is well-suited for our judge prompt design in Step 4.
