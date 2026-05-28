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
| `evaluation_memo.md` | Step 5 — 1-page client memo with results, caveats, and recommendation |
| `reflection.md` | Step 6 — Answers to 3 reflection questions |
| `llm_judge_evaluation.py` | Steps 7–11 — Full Python evaluation pipeline |
| `evaluation_results.json` | Output from running the pipeline (generated on run) |
| `implementation_summary.md` | Brief summary of what was built and key findings |

---

## Chosen Scenario

**Option A — Financial Services**  
A bank wants to automate loan rejection letters. Letters must be clear, compliant with US consumer credit law (ECOA, FCRA), and empathetic toward applicants. Key concerns are accuracy of stated rejection reasons, regulatory disclosure completeness, and absence of discriminatory language.

---

## Approach

- Designed 5 custom evaluation prompts covering: standard rejection, thin credit file, full adverse action notice, demographic bias probe, and hallucination under constrained input
- Built an LLM-as-judge prompt with a 1–5 rubric scoring factual accuracy, regulatory completeness, tone, clarity, and constraint adherence
- Implemented everything using the OpenAI API directly (`gpt-4o-mini` for both generation and judging)
- Tracked score, time, token usage, and cost per test case

---

## How to Run

```bash
# 1. Install dependencies
pip install openai python-dotenv

# 2. Create a .env file with your API key
echo "OPENAI_API_KEY=your_key_here" > .env

# 3. Run the evaluation
python llm_judge_evaluation.py
```

Results are saved to `evaluation_results.json` automatically.

**Estimated cost:** < $0.01 for a full 5-case run using `gpt-4o-mini`.
