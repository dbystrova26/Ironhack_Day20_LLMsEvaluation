# Benchmark Audit — Loan Rejection Letter Automation

**Scenario:** A European retail bank wants to automate loan rejection letters. Letters must be clear, compliant with EU Consumer Credit Directive (CCD II), GDPR, and EBA Guidelines, and empathetic in tone.  
**Key concerns:** Accuracy of stated rejection reasons, regulatory disclosure completeness, and empathetic language.

---

## Benchmark Card 1: FinanceBench

**Benchmark Name:** FinanceBench  
**Year:** 2023  
**Source:** https://arxiv.org/abs/2311.11944

**Why it seemed relevant:**  
FinanceBench tests models on real financial documents — annual reports, earnings statements, and regulatory filings. Since loan rejection letters must cite accurate financial reasoning and comply with regulatory language, this benchmark tests whether a model understands financial facts and can reason about them correctly. It also covers document-grounded Q&A, which mirrors the task of generating a letter grounded in an applicant's financial profile.

**Contamination risk:**  
- [x] High — Model definitely saw this during training  
- Explanation: FinanceBench was released in late 2023 and uses publicly available financial documents. Most frontier models were trained on data that includes these filings and likely the benchmark itself, since it was widely discussed after release.

**Saturation risk:**  
- [x] Medium — Some models perform well  
- Explanation: Top models score 60–80% on FinanceBench, but accuracy drops on multi-hop reasoning questions. It is not yet saturated but approaching it for simpler question types.

**Format:**  
- [x] Free-form text (open-ended financial Q&A with document grounding)

**Verdict:**  
- [x] Adapt it (explain how)  
- Explanation: FinanceBench is US-centric (SEC filings, US GAAP). For a EU bank, adapt by replacing source documents with EU regulatory filings (EBA reports, ECB supervisory data) and reframing questions around CCD II and GDPR compliance rather than US disclosure requirements.

---

## Benchmark Card 2: BBQ (Bias Benchmark for QA)

**Benchmark Name:** BBQ — Bias Benchmark for Question Answering  
**Year:** 2022  
**Source:** https://arxiv.org/abs/2110.08193

**Why it seemed relevant:**  
Loan rejection letters carry significant legal risk around discriminatory language. BBQ measures social biases across protected categories (race, gender, age, religion, disability) in model outputs. EU Equal Treatment Directives and the EU AI Act (which classifies credit scoring as high-risk AI) both require that automated credit decisions be non-discriminatory, making bias evaluation critical for regulatory compliance.

**Contamination risk:**  
- [x] Medium — Some overlap possible  
- Explanation: BBQ is a well-known academic benchmark and likely appears in training corpora, but its question format differs enough from letter generation that direct contamination is less impactful than in pure QA tasks.

**Saturation risk:**  
- [x] Medium — Some models perform well  
- Explanation: Large models score 80–90%+ on BBQ accuracy, but bias scores remain inconsistent across subtle demographic dimensions. It still discriminates between models meaningfully.

**Format:**  
- [x] Multiple Choice (bias detection across demographic scenarios)

**Verdict:**  
- [x] Adapt it (explain how)  
- Explanation: BBQ's demographic categories are US-centric. For a EU context, extend to include EU-specific protected characteristics under the Equal Treatment Directives (nationality, ethnic origin across EU member states). Use BBQ's matched-pair methodology — identical profiles, different names — as the basis for our bias probe (TC04), but with names representative of EU demographic diversity.

---

## Benchmark Card 3: InstructEval

**Benchmark Name:** InstructEval  
**Year:** 2023  
**Source:** https://arxiv.org/abs/2306.04757

**Why it seemed relevant:**  
InstructEval evaluates how well instruction-tuned models follow complex, multi-constraint instructions — exactly what loan rejection letter generation requires (be clear AND compliant AND empathetic, include specific regulatory disclosures, avoid prohibited language). It measures instruction-following fidelity across completeness, format adherence, and constraint satisfaction, which maps directly to our use case.

**Contamination risk:**  
- [x] Low — Model likely not trained on this data  
- Explanation: InstructEval uses procedurally generated instruction sets and was not widely circulated. The evaluation templates are less likely to appear verbatim in training data compared to static academic benchmarks.

**Saturation risk:**  
- [x] Low — Benchmark is challenging  
- Explanation: Multi-constraint instruction following remains genuinely hard. Even top models fail on 3+ simultaneous constraints, and compliance with domain-specific EU regulatory rules is rarely tested in standard benchmarks.

**Format:**  
- [x] Free-form text (instruction-following with rubric-based scoring)

**Verdict:**  
- [x] Use it as-is  
- Explanation: InstructEval's multi-constraint rubric framework applies directly to loan rejection letter evaluation. Its per-constraint pass/fail scoring methodology is well-suited for our judge prompt design, and its difficulty level remains appropriate even for frontier models on EU-specific compliance tasks.
