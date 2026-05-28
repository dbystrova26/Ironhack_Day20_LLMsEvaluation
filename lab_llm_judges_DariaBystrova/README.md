# lab_llm_judges_bank

**Lab:** LLMs Grading LLMs — with Receipts
**Scenario:** Financial Services — A bank wants to automate loan rejection letters that are clear, compliant with ECOA/FCRA regulations, and empathetic in tone.

---

## File Structure

| File | Description |
|------|-------------|
| `README.md` | This file — overview and run instructions |
| `benchmark_audit.md` | Step 2 — 3 benchmark evaluation cards (FinanceBench, BBQ, InstructEval) |
| `evaluation_design.md` | Steps 3–4 — 5 evaluation prompt cards + full LLM-as-judge prompt with bias analysis |
| `evaluation_memo.md` | Step 5 — 1-page client memo with three-model results, caveats, and recommendation |
| `reflection.md` | Step 6 — Answers to 3 reflection questions |
| `llm_judge_evaluation.py` | Steps 7–11 — Single-model evaluation pipeline (gpt-4o-mini) |
| `ab_comparison.py` | Three-way A/B comparison: gpt-4o-mini (t=0) vs gpt-4o-mini (t=0.7) vs claude-sonnet |
| `evaluation_results.json` | Output from llm_judge_evaluation.py |
| `ab_comparison_results.json` | Output from ab_comparison.py |
| `ab_comparison.png` | Four-panel dashboard chart (scores, latency, tokens, cost) |
| `implementation_summary.md` | Summary of what was built and key findings |
| `requirements.txt` | Python dependencies |

---

## Chosen Scenario

**Option A — Financial Services**
A bank wants to automate loan rejection letters. Letters must be clear, compliant with US consumer credit law (ECOA, FCRA), and empathetic toward applicants. Key concerns are accuracy of stated rejection reasons, regulatory disclosure completeness, and absence of discriminatory language.

---

## Approach

- Designed 5 custom evaluation prompts covering: standard rejection, thin credit file, full adverse action notice, demographic bias probe, and hallucination under constrained input
- Built an LLM-as-judge prompt with a 1–5 rubric scoring factual accuracy, regulatory completeness, tone, clarity, and constraint adherence
- Ran a single-model evaluation (gpt-4o-mini) and a three-way A/B comparison
- Tracked score, time, token usage, and cost per test case
- Produced a matplotlib dashboard replicating the LangSmith comparison view

---

## How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file with your API keys
echo "OPENAI_API_KEY=your_openai_key" > .env
echo "ANTHROPIC_API_KEY=your_anthropic_key" >> .env

# 3. Run single-model evaluation (OpenAI only)
python llm_judge_evaluation.py

# 4. Run three-way comparison (OpenAI + Anthropic)
python ab_comparison.py
```

Results are saved automatically to JSON. The comparison chart is saved as `ab_comparison.png`.

**Estimated cost:** < $0.01 for single-model run | < $0.05 for full three-way comparison.
