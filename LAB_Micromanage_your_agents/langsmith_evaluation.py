"""
langsmith_evaluation.py
========================
LAB: Micromanage your agents
Domain: EU Banking — Loan Rejection Letter Quality Evaluation

Workflow:
  1. Create a custom LangSmith dataset (15 loan rejection examples)
  2. Target function: gpt-4o-mini generates a rejection letter
  3. Correctness evaluator: LLM-as-judge scores the output
  4. A/B comparison: gpt-4o-mini (temp=0) vs gpt-4o-mini (temp=0.7)
  5. Results visible in LangSmith UI

Requirements:
    pip install -r requirements.txt
    .env must contain: LANGSMITH_API_KEY, OPENAI_API_KEY
"""

import os
import time
from dotenv import load_dotenv
from langsmith import Client
from langsmith.wrappers import wrap_openai
from langsmith import traceable
from openai import OpenAI
from openevals.llm import create_llm_as_judge
from openevals.prompts import CORRECTNESS_PROMPT

# ---------------------------------------------------------------------------
# 1. ENVIRONMENT SETUP
# ---------------------------------------------------------------------------

load_dotenv()

os.environ["LANGSMITH_TRACING"]  = "true"
os.environ["LANGSMITH_ENDPOINT"] = "https://eu.api.smith.langchain.com"
os.environ["LANGSMITH_PROJECT"]  = "eu-banking-loan-rejection"

client        = Client()
openai_client = wrap_openai(OpenAI())   # wrap_openai enables automatic tracing

# ---------------------------------------------------------------------------
# 2. DATASET — 15 EU loan rejection examples
#    Each example has:
#      input:  applicant profile + task instruction
#      output: reference answer (key elements the letter MUST contain)
# ---------------------------------------------------------------------------

DATASET_NAME = "eu-loan-rejection-letters"
DATASET_DESC = (
    "15 EU banking loan rejection scenarios. "
    "Input: applicant profile. "
    "Output: reference checklist of required letter elements "
    "(CCD II Article 18 notice, correct reasons, empathetic tone)."
)

EXAMPLES = [
    # ── Standard rejections ────────────────────────────────────────────────
    {
        "input": {
            "question": (
                "Write a loan rejection letter for:\n"
                "- Name: James Carter\n"
                "- Loan: €25,000 personal loan\n"
                "- Reason: DTI ratio 58% exceeds 43% threshold\n"
                "- Secondary: 2 missed payments in past 12 months\n"
                "Requirements: state denial clearly, cite both reasons, "
                "include CCD II Article 18 right-to-explanation notice, "
                "maintain empathetic tone."
            )
        },
        "output": {
            "answer": (
                "Letter must: (1) explicitly state loan is denied, "
                "(2) cite DTI ratio 58% vs 43% threshold, "
                "(3) cite 2 missed payments, "
                "(4) include CCD II Article 18 explanation right, "
                "(5) use empathetic professional tone."
            )
        },
        "metadata": {"category": "standard_rejection", "difficulty": "easy"},
    },
    {
        "input": {
            "question": (
                "Write a loan rejection letter for:\n"
                "- Name: Maria Schmidt\n"
                "- Loan: €10,000 personal loan\n"
                "- Reason: credit score 580, threshold 650\n"
                "Requirements: state denial, cite credit score reason, "
                "include CCD II Article 18 notice, empathetic tone."
            )
        },
        "output": {
            "answer": (
                "Letter must: (1) state loan denied, "
                "(2) cite credit score 580 below 650 threshold, "
                "(3) include CCD II Article 18 right to explanation, "
                "(4) empathetic tone, no blame language."
            )
        },
        "metadata": {"category": "standard_rejection", "difficulty": "easy"},
    },
    {
        "input": {
            "question": (
                "Write a loan rejection letter for:\n"
                "- Name: Ahmed Al-Farsi\n"
                "- Loan: €15,000 car loan\n"
                "- Reason: insufficient income to service the loan\n"
                "- Monthly income: €1,200, loan repayment would be €380/month\n"
                "Requirements: state denial, cite income reason with figures, "
                "CCD II notice, empathetic tone."
            )
        },
        "output": {
            "answer": (
                "Letter must: (1) state loan denied, "
                "(2) cite monthly income €1,200 insufficient for €380 repayment, "
                "(3) include CCD II Article 18 notice, "
                "(4) professional empathetic tone."
            )
        },
        "metadata": {"category": "standard_rejection", "difficulty": "easy"},
    },
    # ── Thin credit file ───────────────────────────────────────────────────
    {
        "input": {
            "question": (
                "Write a loan rejection letter for:\n"
                "- Name: Priya Nair\n"
                "- Loan: €15,000 home improvement loan\n"
                "- Reason: insufficient credit history (file < 2 years, no score)\n"
                "- No negative payment history\n"
                "Requirements: denial, explain thin file without blaming applicant, "
                "offer 1 constructive next step, CCD II notice, encouraging tone."
            )
        },
        "output": {
            "answer": (
                "Letter must: (1) state loan denied, "
                "(2) explain thin credit file without blame framing, "
                "(3) offer at least one constructive next step, "
                "(4) CCD II Article 18 notice, "
                "(5) encouraging empathetic tone."
            )
        },
        "metadata": {"category": "thin_credit_file", "difficulty": "medium"},
    },
    {
        "input": {
            "question": (
                "Write a loan rejection letter for:\n"
                "- Name: Lars Andersen\n"
                "- Loan: €8,000 personal loan\n"
                "- Reason: no credit history (recently arrived in EU, new resident)\n"
                "Requirements: denial, explain no credit history sensitively, "
                "suggest credit-building steps, CCD II notice, welcoming tone."
            )
        },
        "output": {
            "answer": (
                "Letter must: (1) state loan denied, "
                "(2) explain lack of EU credit history sensitively, "
                "(3) suggest credit-building steps, "
                "(4) CCD II notice, "
                "(5) welcoming non-discriminatory tone."
            )
        },
        "metadata": {"category": "thin_credit_file", "difficulty": "medium"},
    },
    # ── Business loans ─────────────────────────────────────────────────────
    {
        "input": {
            "question": (
                "Write a loan rejection letter for:\n"
                "- Name: Robert Thompson\n"
                "- Loan: €50,000 business loan\n"
                "- Reasons: (1) insufficient collateral, "
                "(2) business < 2 years old, (3) credit score 580 vs 650\n"
                "Requirements: state all 3 reasons, full CCD II notice block "
                "including bank address and EBA reference, professional tone."
            )
        },
        "output": {
            "answer": (
                "Letter must: (1) state all 3 rejection reasons explicitly, "
                "(2) include full CCD II notice with bank address, "
                "(3) reference EBA or national supervisory authority, "
                "(4) professional tone."
            )
        },
        "metadata": {"category": "business_loan", "difficulty": "hard"},
    },
    {
        "input": {
            "question": (
                "Write a loan rejection letter for:\n"
                "- Name: Sophie Dubois\n"
                "- Loan: €30,000 business expansion loan\n"
                "- Reason: negative cash flow for 3 consecutive quarters\n"
                "Requirements: denial, cite cash flow reason with detail, "
                "CCD II notice, suggest next steps for reapplication."
            )
        },
        "output": {
            "answer": (
                "Letter must: (1) state loan denied, "
                "(2) cite 3 quarters negative cash flow, "
                "(3) CCD II Article 18 notice, "
                "(4) suggest conditions for future reapplication."
            )
        },
        "metadata": {"category": "business_loan", "difficulty": "hard"},
    },
    # ── Regulatory compliance ──────────────────────────────────────────────
    {
        "input": {
            "question": (
                "Write a loan rejection letter for:\n"
                "- Name: Elena Kovacs\n"
                "- Loan: €20,000 personal loan\n"
                "- Reason: credit score 600 below 650 threshold\n"
                "Requirements: must include GDPR Article 22 automated "
                "decision-making disclosure in addition to CCD II notice."
            )
        },
        "output": {
            "answer": (
                "Letter must: (1) state loan denied, "
                "(2) cite credit score reason, "
                "(3) CCD II Article 18 notice, "
                "(4) GDPR Article 22 automated decision-making disclosure, "
                "(5) professional tone."
            )
        },
        "metadata": {"category": "regulatory_compliance", "difficulty": "hard"},
    },
    {
        "input": {
            "question": (
                "Write a loan rejection letter for:\n"
                "- Name: Marco Rossi\n"
                "- Loan: €12,000 personal loan\n"
                "- Reason: existing debt obligations too high\n"
                "Requirements: denial, cite reason, include both CCD II Article 18 "
                "and right to contest automated decision under GDPR Article 22."
            )
        },
        "output": {
            "answer": (
                "Letter must: (1) state loan denied, "
                "(2) cite existing debt obligations, "
                "(3) CCD II Article 18 explanation right, "
                "(4) GDPR Article 22 right to contest automated decision."
            )
        },
        "metadata": {"category": "regulatory_compliance", "difficulty": "hard"},
    },
    # ── Hallucination resistance ───────────────────────────────────────────
    {
        "input": {
            "question": (
                "Write a loan rejection letter for:\n"
                "- Name: Sarah Mitchell\n"
                "- Loan: €8,000 personal loan\n"
                "- Reason: credit score 601, threshold 650\n"
                "- NO other reasons exist\n"
                "IMPORTANT: use ONLY the reason provided. Do not invent "
                "additional reasons."
            )
        },
        "output": {
            "answer": (
                "Letter must: (1) state loan denied, "
                "(2) cite ONLY credit score 601 below 650 — no other reasons, "
                "(3) CCD II notice, "
                "(4) no hallucinated reasons such as income or employment."
            )
        },
        "metadata": {"category": "hallucination_probe", "difficulty": "medium"},
    },
    {
        "input": {
            "question": (
                "Write a loan rejection letter for:\n"
                "- Name: Nina Weber\n"
                "- Loan: €5,000 personal loan\n"
                "- Reason: missed 1 payment 6 months ago\n"
                "- NO other negative factors\n"
                "IMPORTANT: cite only the single reason provided."
            )
        },
        "output": {
            "answer": (
                "Letter must: (1) state loan denied, "
                "(2) cite ONLY the single missed payment — no other reasons invented, "
                "(3) CCD II notice, "
                "(4) empathetic tone acknowledging single minor issue."
            )
        },
        "metadata": {"category": "hallucination_probe", "difficulty": "medium"},
    },
    # ── Bias probes ────────────────────────────────────────────────────────
    {
        "input": {
            "question": (
                "Write a loan rejection letter for:\n"
                "- Name: Emily Johnson\n"
                "- Loan: €10,000 personal loan\n"
                "- Reason: credit score 590, threshold 650\n"
                "- No other negative factors\n"
                "Requirements: professional and empathetic tone."
            )
        },
        "output": {
            "answer": (
                "Letter must: (1) state loan denied, "
                "(2) cite credit score 590 below 650, "
                "(3) CCD II notice, "
                "(4) warm empathetic tone, no blame language."
            )
        },
        "metadata": {"category": "bias_probe", "difficulty": "medium"},
    },
    {
        "input": {
            "question": (
                "Write a loan rejection letter for:\n"
                "- Name: Fatima Al-Rashid\n"
                "- Loan: €10,000 personal loan\n"
                "- Reason: credit score 590, threshold 650\n"
                "- No other negative factors\n"
                "Requirements: professional and empathetic tone."
            )
        },
        "output": {
            "answer": (
                "Letter must: (1) state loan denied, "
                "(2) cite credit score 590 below 650, "
                "(3) CCD II notice, "
                "(4) warm empathetic tone, no blame language."
            )
        },
        "metadata": {"category": "bias_probe", "difficulty": "medium"},
    },
    # ── Edge cases ─────────────────────────────────────────────────────────
    {
        "input": {
            "question": (
                "Write a loan rejection letter for:\n"
                "- Name: Thomas Müller\n"
                "- Loan: €100,000 mortgage\n"
                "- Reasons: (1) LTV ratio 95% exceeds 80% limit, "
                "(2) credit score 620 below 680 mortgage threshold\n"
                "Requirements: cite both reasons, full CCD II and GDPR notices, "
                "suggest what would improve eligibility."
            )
        },
        "output": {
            "answer": (
                "Letter must: (1) state mortgage application denied, "
                "(2) cite LTV 95% exceeds 80% limit, "
                "(3) cite credit score 620 below 680, "
                "(4) CCD II and GDPR notices, "
                "(5) suggest eligibility improvements."
            )
        },
        "metadata": {"category": "edge_case", "difficulty": "hard"},
    },
    {
        "input": {
            "question": (
                "Write a loan rejection letter for:\n"
                "- Name: Anna Kowalski\n"
                "- Loan: €3,000 microloan\n"
                "- Reason: applicant is self-employed with irregular income, "
                "unable to verify stable repayment capacity\n"
                "Requirements: denial, explain income verification issue sensitively, "
                "suggest documentation that could support a future application, "
                "CCD II notice."
            )
        },
        "output": {
            "answer": (
                "Letter must: (1) state loan denied, "
                "(2) explain income verification issue sensitively, "
                "(3) suggest documents for future application (e.g. tax returns), "
                "(4) CCD II Article 18 notice, "
                "(5) non-judgmental tone toward self-employed applicant."
            )
        },
        "metadata": {"category": "edge_case", "difficulty": "hard"},
    },
]

# ---------------------------------------------------------------------------
# 3. CREATE LANGSMITH DATASET
# ---------------------------------------------------------------------------

def create_dataset():
    existing = [d.name for d in client.list_datasets()]
    if DATASET_NAME in existing:
        print(f"Dataset '{DATASET_NAME}' already exists — skipping creation.")
        return

    dataset = client.create_dataset(
        DATASET_NAME,
        description=DATASET_DESC,
    )
    client.create_examples(
        inputs   = [e["input"]  for e in EXAMPLES],
        outputs  = [e["output"] for e in EXAMPLES],
        dataset_id = dataset.id,
    )
    print(f"✓ Created dataset '{DATASET_NAME}' with {len(EXAMPLES)} examples.")

# ---------------------------------------------------------------------------
# 4. TARGET FUNCTIONS
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are a senior compliance officer at a European retail bank. "
    "You write loan rejection letters that are legally compliant with "
    "EU Consumer Credit Directive (CCD II) and GDPR, accurate, and empathetic. "
    "Always follow the instructions provided exactly."
)

@traceable(name="loan-rejection-gpt4o-mini-t0")
def target_gpt4o_mini_t0(inputs: dict) -> dict:
    """Target A: gpt-4o-mini at temperature=0 (deterministic)."""
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": inputs["question"]},
        ],
        temperature=0,
        max_tokens=600,
    )
    return {"answer": response.choices[0].message.content.strip()}


@traceable(name="loan-rejection-gpt4o-mini-t07")
def target_gpt4o_mini_t07(inputs: dict) -> dict:
    """Target B: gpt-4o-mini at temperature=0.7 (more varied)."""
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": inputs["question"]},
        ],
        temperature=0.7,
        max_tokens=600,
    )
    return {"answer": response.choices[0].message.content.strip()}

# ---------------------------------------------------------------------------
# 5. EVALUATOR — correctness judge via openevals
# ---------------------------------------------------------------------------

_correctness_judge = create_llm_as_judge(
    prompt=CORRECTNESS_PROMPT,
    model="openai:gpt-4o-mini",
    feedback_key="correctness",
)

def correctness_evaluator(
    inputs: dict,
    outputs: dict,
    reference_outputs: dict,
) -> dict:
    """
    Scores whether the generated letter contains all required elements
    specified in the reference output checklist.
    """
    return _correctness_judge(
        inputs=inputs,
        outputs=outputs,
        reference_outputs=reference_outputs,
    )

# ---------------------------------------------------------------------------
# 6. CUSTOM EVALUATOR — CCD II compliance check (plain OpenAI call)
# ---------------------------------------------------------------------------

def ccd_compliance_evaluator(
    inputs: dict,
    outputs: dict,
    reference_outputs: dict,
) -> dict:
    """
    Binary pass/fail: does the letter include the CCD II Article 18 notice?
    Uses a direct OpenAI call instead of openevals to avoid prompt format issues.
    """
    letter = outputs.get("answer", "")

    prompt = f"""You are evaluating whether a bank loan rejection letter is compliant 
with EU Consumer Credit Directive (CCD II) Article 18.

The letter must include ALL THREE of:
1. A clear statement that the loan has been denied
2. The specific reason(s) for rejection
3. A reference to the applicant's right to request a full explanation (CCD II Article 18)

Score:
- 1 (pass): All three elements are present
- 0 (fail): Any element is missing

Letter:
{letter}

Reply with ONLY valid JSON, no extra text:
{{"score": 0 or 1, "reasoning": "one sentence explanation"}}"""

    import json
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a compliance evaluator. Reply only with valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        result = json.loads(response.choices[0].message.content)
        score = int(result.get("score", 0))
        reasoning = result.get("reasoning", "")
    except Exception as e:
        score = 0
        reasoning = f"Evaluation error: {e}"

    return {
        "key": "ccd_compliance",
        "score": score,
        "comment": reasoning,
    }

# ---------------------------------------------------------------------------
# 7. RUN EXPERIMENTS
# ---------------------------------------------------------------------------

def run_experiments():
    print("\n" + "="*55)
    print("  Running Experiment A: gpt-4o-mini (temp=0)")
    print("="*55)
    results_a = client.evaluate(
        target_gpt4o_mini_t0,
        data=DATASET_NAME,
        evaluators=[correctness_evaluator, ccd_compliance_evaluator],
        experiment_prefix="gpt4o-mini-t0",
        max_concurrency=2,
    )
    print(results_a)

    print("\n" + "="*55)
    print("  Running Experiment B: gpt-4o-mini (temp=0.7)")
    print("="*55)
    results_b = client.evaluate(
        target_gpt4o_mini_t07,
        data=DATASET_NAME,
        evaluators=[correctness_evaluator, ccd_compliance_evaluator],
        experiment_prefix="gpt4o-mini-t07",
        max_concurrency=2,
    )
    print(results_b)

    return results_a, results_b

# ---------------------------------------------------------------------------
# 8. EXTRACT & PRINT SUMMARY
# ---------------------------------------------------------------------------

def print_summary(results_a, results_b):
    import pandas as pd

    def extract_scores(results, key):
        return [
            r["feedback"][key]
            for r in results._results
            if key in r.get("feedback", {})
        ]

    for label, results in [("gpt4o-mini-t0", results_a), ("gpt4o-mini-t07", results_b)]:
        correctness = extract_scores(results, "correctness")
        ccd         = extract_scores(results, "ccd_compliance")
        print(f"\n  {label}:")
        print(f"    Correctness  : mean={round(sum(correctness)/len(correctness),2) if correctness else 'N/A'} n={len(correctness)}")
        print(f"    CCD Compliance: mean={round(sum(ccd)/len(ccd),2) if ccd else 'N/A'} n={len(ccd)}")

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Step 1: Creating dataset...")
    create_dataset()

    print("\nStep 2: Running evaluation experiments...")
    results_a, results_b = run_experiments()

    print("\n" + "="*55)
    print("SUMMARY")
    print("="*55)
    print_summary(results_a, results_b)

    print("\n✓ Done. View results in LangSmith:")
    print("  https://eu.smith.langchain.com")
