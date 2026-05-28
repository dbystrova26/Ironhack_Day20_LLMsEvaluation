# lab_langsmith_DariaBystrova

**Lab:** Micromanage your agents  
**Domain:** EU Banking — Loan Rejection Letter Quality Evaluation  
**Dataset:** `eu-loan-rejection-letters` — 15 custom examples across 7 categories  
**Project:** `eu-banking-loan-rejection` on LangSmith EU endpoint  

---

## Domain & Dataset Description

A European retail bank wants to automate loan rejection letters compliant with EU Consumer Credit Directive (CCD II) and GDPR. The dataset contains 15 loan rejection scenarios covering standard rejections, thin credit files, business loans, regulatory compliance edge cases, hallucination probes, bias probes, and edge cases. Each example has an applicant profile as input and a reference checklist of required letter elements as expected output. A good example has a clear single input (applicant profile), a verifiable output checklist (denial statement + cited reasons + CCD II notice + tone), and belongs to a specific category and difficulty level for categorical analysis.

**Sources:** All 15 examples are custom-designed to reflect real EU banking production scenarios — no existing benchmark was used, as none covers the CCD II/GDPR regulatory intersection.

---

## File Map

| File | Purpose |
|------|---------|
| `langsmith_evaluation.py` | Main code: dataset creation, target functions, evaluators, quick test, experiment execution, summary |
| `cost_performance_analysis.py` | Step 15: cost-performance analysis with categorical breakdown |
| `evaluation_summary.md` | Steps 9-10: evaluation report with metrics, failures, categorical analysis |
| `custom_evaluator_and_ab_comparison.md` | Steps 11-14: custom evaluator design + A/B comparison results |
| `optimization_summary.md` | Step 16: one-paragraph optimization recommendation |
| `requirements.txt` | Python dependencies |
| `langsmith_results_comparison.png` | LangSmith A/B comparison screenshot |
| `langsmith_experiments_overview.png` | LangSmith experiments overview screenshot |
| `README.md` | This file |

---

## Approach

1. **Dataset** — 15 custom EU banking examples with inputs, reference outputs, category + difficulty metadata
2. **Target functions** — `gpt-4o-mini` at temp=0 and temp=0.7, both `@traceable`
3. **Evaluators** — correctness (openevals) + custom CCD II compliance (plain OpenAI call)
4. **Experiments** — A/B via `client.evaluate()`, results in LangSmith UI
5. **Analysis** — categorical breakdown, cost-performance frontier, failure analysis

---

## How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file
LANGSMITH_API_KEY=your_langsmith_key
OPENAI_API_KEY=your_openai_key

# 3. Run evaluation (creates dataset, quick test, both experiments)
python langsmith_evaluation.py

# 4. Run cost-performance analysis
python cost_performance_analysis.py
```

Results appear in LangSmith: **https://eu.smith.langchain.com**  
Project: `eu-banking-loan-rejection` | Dataset: `eu-loan-rejection-letters`

---

## Key Results

| Config | Correctness | CCD Compliance | Cost/letter | Latency P50 |
|---|---|---|---|---|
| gpt-4o-mini (temp=0) | **1.00** | 0.93 | $0.000227 | 7.15s |
| gpt-4o-mini (temp=0.7) | 0.87 | 0.93 | $0.000220 | 6.41s |

**Recommendation:** temp=0 for production — perfect correctness at identical cost.
