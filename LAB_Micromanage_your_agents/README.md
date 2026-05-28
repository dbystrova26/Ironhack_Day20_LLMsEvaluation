# lab_langsmith_DariaBystrova

**Lab:** Micromanage your agents  
**Domain:** EU Banking — Loan Rejection Letter Quality Evaluation  
**Dataset:** 15 custom examples across 5 categories  

---

## Domain & Dataset Description

A European retail bank wants to automate loan rejection letters compliant with EU Consumer Credit Directive (CCD II) and GDPR. The dataset contains 15 loan rejection scenarios covering standard rejections, thin credit files, business loans, regulatory compliance edge cases, hallucination probes, and bias probes. Each example has an applicant profile as input and a reference checklist of required letter elements as the expected output.

**What makes a good example:**
- Input: applicant profile with name, loan amount, and specific rejection reason(s)
- Output: checklist of elements the letter MUST contain (denial statement, cited reasons, CCD II notice, tone requirements)
- Diversity: easy standard cases + hard multi-regulatory cases + probes for hallucination and bias

---

## File Map

| File | Purpose |
|------|---------|
| `langsmith_evaluation.py` | Main code: dataset creation, target functions, evaluators, experiment execution |
| `evaluation_summary.md` | One-paragraph evaluation report + metrics table |
| `requirements.txt` | Python dependencies |
| `README.md` | This file |

---

## Approach

1. Created a 15-example custom LangSmith dataset (`eu-loan-rejection-letters`) covering 5 difficulty categories
2. Implemented two target functions: `gpt-4o-mini` at temp=0 and temp=0.7, both with `@traceable` for automatic LangSmith tracing
3. Set up two evaluators:
   - **Correctness** (openevals built-in): does the letter contain all required elements?
   - **CCD II Compliance** (custom): is the Article 18 explanation notice present?
4. Ran A/B comparison via `client.evaluate()` — results visible in LangSmith UI

---

## How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file
LANGSMITH_API_KEY=your_langsmith_key
OPENAI_API_KEY=your_openai_key

# 3. Run
python langsmith_evaluation.py
```

Results appear automatically in your LangSmith project:  
**Project:** `eu-banking-loan-rejection`  
**Endpoint:** `https://eu.smith.langchain.com`

---

## LangSmith Links

- Dataset: `eu-loan-rejection-letters` (visible in Datasets & Experiments)
- Experiments: `gpt4o-mini-t0-*` and `gpt4o-mini-t07-*`
