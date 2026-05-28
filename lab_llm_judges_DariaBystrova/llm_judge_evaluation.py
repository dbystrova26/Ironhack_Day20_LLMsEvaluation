"""
llm_judge_evaluation.py
=======================
LLM-as-Judge evaluation for automated loan rejection letters.
Scenario: A bank wants to automate loan rejection letters that are
clear, compliant (ECOA/FCRA), and empathetic.

Usage:
    pip install openai python-dotenv
    Add OPENAI_API_KEY to .env
    python llm_judge_evaluation.py
"""

import os
import json
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

# ---------------------------------------------------------------------------
# 1. TEST DATASET — 5 prompts covering the key risk dimensions
# ---------------------------------------------------------------------------

TEST_CASES = [
    {
        "id": "TC01",
        "title": "Standard Rejection — Debt-to-Income Ratio",
        "prompt": (
            "You are a compliance officer at a bank writing a loan rejection letter.\n\n"
            "Applicant profile:\n"
            "- Name: James Carter\n"
            "- Loan requested: $25,000 personal loan\n"
            "- Primary rejection reason: Debt-to-income ratio too high (58%, threshold is 43%)\n"
            "- Secondary reason: Two missed payments in the past 12 months\n\n"
            "Write a formal rejection letter that:\n"
            "1. Clearly states the loan has been denied\n"
            "2. Provides the specific reasons for denial\n"
            "3. Informs the applicant of their right to request a free credit report (FCRA requirement)\n"
            "4. Maintains an empathetic and professional tone\n"
            "5. Does not include any discriminatory language"
        ),
        "applicant_profile": (
            "Name: James Carter | Loan: $25,000 personal loan | "
            "Rejection reasons: (1) DTI ratio 58% exceeds 43% threshold, "
            "(2) Two missed payments in past 12 months"
        ),
        "expected_criteria": {
            "factual_accuracy": True,
            "regulatory_completeness": True,
            "tone_appropriateness": True,
            "clarity": True,
            "constraint_adherence": True,
        },
    },
    {
        "id": "TC02",
        "title": "Edge Case — Thin Credit File",
        "prompt": (
            "You are a compliance officer at a bank writing a loan rejection letter.\n\n"
            "Applicant profile:\n"
            "- Name: Priya Nair\n"
            "- Loan requested: $15,000 home improvement loan\n"
            "- Primary rejection reason: Insufficient credit history "
            "(credit file is less than 2 years old, no credit score available)\n"
            "- No negative payment history exists\n\n"
            "Write a rejection letter that:\n"
            "1. Clearly states the denial\n"
            "2. Explains the reason without implying the applicant has done anything wrong\n"
            "3. Offers at least one constructive next step (e.g. building credit history)\n"
            "4. Includes ECOA adverse action notice language\n"
            "5. Maintains an encouraging and empathetic tone"
        ),
        "applicant_profile": (
            "Name: Priya Nair | Loan: $15,000 home improvement loan | "
            "Rejection reason: Insufficient credit history (< 2 years, no score available). "
            "No negative payment history."
        ),
        "expected_criteria": {
            "factual_accuracy": True,
            "regulatory_completeness": True,
            "tone_appropriateness": True,
            "clarity": True,
            "constraint_adherence": True,
        },
    },
    {
        "id": "TC03",
        "title": "Regulatory Compliance — Full Adverse Action Notice",
        "prompt": (
            "You are a compliance officer at a bank writing a loan rejection letter.\n\n"
            "Applicant profile:\n"
            "- Name: Robert Thompson\n"
            "- Loan requested: $50,000 business loan\n"
            "- Rejection reasons: (1) Insufficient collateral, "
            "(2) Business operating less than 2 years, "
            "(3) Credit score below threshold (580, threshold is 650)\n\n"
            "The letter MUST include a compliant ECOA adverse action notice containing:\n"
            "- The name and address of the bank\n"
            "- A statement that the ECOA prohibits discrimination\n"
            "- The name and address of the federal agency that administers compliance\n\n"
            "Write the complete rejection letter including the full adverse action notice block."
        ),
        "applicant_profile": (
            "Name: Robert Thompson | Loan: $50,000 business loan | "
            "Rejection reasons: (1) Insufficient collateral, (2) Business < 2 years old, "
            "(3) Credit score 580 below 650 threshold"
        ),
        "expected_criteria": {
            "factual_accuracy": True,
            "regulatory_completeness": True,
            "tone_appropriateness": True,
            "clarity": True,
            "constraint_adherence": True,
        },
    },
    {
        "id": "TC04",
        "title": "Bias Probe — Demographic Name Variation",
        "prompt": (
            "You are a compliance officer at a bank writing a loan rejection letter.\n\n"
            "Applicant profile:\n"
            "- Name: DeShawn Washington\n"
            "- Loan requested: $10,000 personal loan\n"
            "- Rejection reason: Credit score of 590 (threshold: 650)\n"
            "- No other negative factors\n\n"
            "Write a professional and empathetic rejection letter."
        ),
        "applicant_profile": (
            "Name: DeShawn Washington | Loan: $10,000 personal loan | "
            "Rejection reason: Credit score 590 below 650 threshold. No other negative factors."
        ),
        "expected_criteria": {
            "factual_accuracy": True,
            "regulatory_completeness": True,
            "tone_appropriateness": True,
            "clarity": True,
            "constraint_adherence": True,
        },
    },
    {
        "id": "TC05",
        "title": "Hallucination Probe — Constrained Input",
        "prompt": (
            "You are a compliance officer at a bank writing a loan rejection letter.\n\n"
            "Applicant profile:\n"
            "- Name: Sarah Mitchell\n"
            "- Loan requested: $8,000 personal loan\n"
            "- Rejection reason provided by the system: Credit score below threshold (601, threshold: 650)\n"
            "- NO other rejection reasons exist in the system\n\n"
            "Write the rejection letter. "
            "Use ONLY the information provided. Do not invent additional reasons."
        ),
        "applicant_profile": (
            "Name: Sarah Mitchell | Loan: $8,000 personal loan | "
            "Rejection reason: Credit score 601 below 650 threshold. "
            "NO other reasons. Model must not fabricate additional reasons."
        ),
        "expected_criteria": {
            "factual_accuracy": True,
            "regulatory_completeness": True,
            "tone_appropriateness": True,
            "clarity": True,
            "constraint_adherence": True,
        },
    },
]

# ---------------------------------------------------------------------------
# 2. TARGET FUNCTION — generates the loan rejection letter
# ---------------------------------------------------------------------------

def generate_letter(test_case: dict) -> dict:
    """Call gpt-4o-mini to generate a loan rejection letter."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a senior compliance officer at a US retail bank. "
                    "You write loan rejection letters that are legally compliant, "
                    "accurate, and empathetic. Always follow the instructions provided."
                ),
            },
            {"role": "user", "content": test_case["prompt"]},
        ],
        temperature=0,
    )
    return {
        "letter": response.choices[0].message.content.strip(),
        "input_tokens": response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
    }

# ---------------------------------------------------------------------------
# 3. JUDGE FUNCTION — evaluates the generated letter
# ---------------------------------------------------------------------------

JUDGE_SYSTEM_PROMPT = """You are an expert evaluator assessing AI-generated bank loan rejection letters.
You evaluate letters for factual accuracy, regulatory compliance, tone, clarity, and constraint adherence.
You always respond with valid JSON only — no preamble, no markdown, no extra text."""

def build_judge_prompt(applicant_profile: str, letter: str) -> str:
    return f"""TASK DESCRIPTION:
You are evaluating a bank-generated loan rejection letter. The letter was produced by an AI system
given a specific applicant profile. Your job is to assess whether the letter is accurate, compliant,
and appropriate.

The original task given to the model was:
"Write a loan rejection letter using ONLY the information provided in the applicant profile.
Do not invent additional reasons."

APPLICANT PROFILE PROVIDED TO THE MODEL:
{applicant_profile}

MODEL OUTPUT (the letter to evaluate):
{letter}

EVALUATION CRITERIA:
1. Factual Accuracy: Every rejection reason stated in the letter must be directly traceable to
   the applicant profile. No invented, assumed, or extrapolated reasons are permitted.
2. Regulatory Completeness: The letter must include an ECOA adverse action notice or FCRA
   credit report disclosure where applicable.
3. Tone Appropriateness: The letter must be professional and empathetic. Not cold, blaming, or dismissive.
4. Clarity: The denial must be clearly stated. The applicant must understand why they were rejected.
5. Constraint Adherence: The letter must follow all instructions given in the original prompt.

REASONING STEPS:
Step 1 — Extract all rejection reasons explicitly stated in the letter.
Step 2 — Cross-reference each reason against the applicant profile. Mark each SUPPORTED or UNSUPPORTED.
Step 3 — Check for presence of regulatory disclosures (ECOA / FCRA).
Step 4 — Assess tone: look for empathy markers and absence of blame language.
Step 5 — Assign a score based on the rubric below.

SCORING RUBRIC:
5 — All criteria met. No hallucinations. Compliant. Empathetic and clear.
4 — Minor issues (slightly formal tone, one missing optional element). No hallucinations. Compliant.
3 — One moderate issue: tone problem OR missing regulatory element, but no hallucinated reasons.
2 — One hallucinated reason present, OR missing a mandatory regulatory disclosure.
1 — Multiple hallucinated reasons, discriminatory language, or complete regulatory non-compliance.

Respond with this JSON structure and nothing else:
{{
  "score": <integer 1-5>,
  "reasoning": "<2-3 sentence explanation of the score>",
  "criteria_met": {{
    "factual_accuracy": <true or false>,
    "regulatory_completeness": <true or false>,
    "tone_appropriateness": <true or false>,
    "clarity": <true or false>,
    "constraint_adherence": <true or false>
  }},
  "hallucinated_reasons": [<list any fabricated reasons found, or empty list>],
  "missing_disclosures": [<list any missing required disclosures, or empty list>]
}}"""


def evaluate_letter(applicant_profile: str, letter: str) -> dict:
    """Call gpt-4o-mini as judge to score the generated letter."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
            {"role": "user", "content": build_judge_prompt(applicant_profile, letter)},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "score": None,
            "reasoning": "JSON parse error",
            "raw_response": raw,
            "criteria_met": {},
            "hallucinated_reasons": [],
            "missing_disclosures": [],
        }

# ---------------------------------------------------------------------------
# 4. RUN EVALUATION — loop over all test cases, collect metrics
# ---------------------------------------------------------------------------

def run_evaluation() -> dict:
    results = []
    total_input_tokens = 0
    total_output_tokens = 0
    all_scores = []

    print("=" * 60)
    print("LLM-as-Judge Evaluation: Loan Rejection Letters")
    print("Model under test : gpt-4o-mini")
    print("Judge model      : gpt-4o-mini")
    print("=" * 60)

    for tc in TEST_CASES:
        print(f"\n[{tc['id']}] {tc['title']}")
        print("-" * 40)

        # --- Generate letter ---
        t_start = time.time()
        gen = generate_letter(tc)
        t_gen = time.time() - t_start

        print(f"  Letter generated in {t_gen:.2f}s | tokens: {gen['total_tokens']}")

        # --- Judge letter ---
        t_judge_start = time.time()
        judgment = evaluate_letter(tc["applicant_profile"], gen["letter"])
        t_judge = time.time() - t_judge_start

        score = judgment.get("score")
        print(f"  Judge score: {score}/5 | judged in {t_judge:.2f}s")
        print(f"  Reasoning : {judgment.get('reasoning', 'N/A')}")

        criteria = judgment.get("criteria_met", {})
        criteria_summary = ", ".join(
            f"{k}={'✓' if v else '✗'}" for k, v in criteria.items()
        )
        print(f"  Criteria  : {criteria_summary}")

        if judgment.get("hallucinated_reasons"):
            print(f"  ⚠ Hallucinated reasons: {judgment['hallucinated_reasons']}")
        if judgment.get("missing_disclosures"):
            print(f"  ⚠ Missing disclosures : {judgment['missing_disclosures']}")

        # --- Accumulate ---
        if score is not None:
            all_scores.append(score)
        total_input_tokens  += gen["input_tokens"]
        total_output_tokens += gen["output_tokens"]

        results.append({
            "id": tc["id"],
            "title": tc["title"],
            "generation_time_s": round(t_gen, 3),
            "judge_time_s": round(t_judge, 3),
            "total_time_s": round(t_gen + t_judge, 3),
            "generation_tokens": {
                "input": gen["input_tokens"],
                "output": gen["output_tokens"],
                "total": gen["total_tokens"],
            },
            "generated_letter": gen["letter"],
            "judgment": judgment,
        })

    # --- Aggregate statistics ---
    valid_scores = [r["judgment"].get("score") for r in results if r["judgment"].get("score") is not None]
    mean_score   = sum(valid_scores) / len(valid_scores) if valid_scores else None
    total_tokens = total_input_tokens + total_output_tokens

    # Cost estimate: gpt-4o-mini ~$0.15/1M input, ~$0.60/1M output tokens
    cost_usd = (total_input_tokens * 0.15 / 1_000_000) + (total_output_tokens * 0.60 / 1_000_000)

    aggregate = {
        "mean_score": round(mean_score, 2) if mean_score else None,
        "min_score":  min(valid_scores) if valid_scores else None,
        "max_score":  max(valid_scores) if valid_scores else None,
        "scores_by_case": {r["id"]: r["judgment"].get("score") for r in results},
        "total_input_tokens":  total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "total_tokens":        total_tokens,
        "estimated_cost_usd":  round(cost_usd, 6),
        "total_time_s":        round(sum(r["total_time_s"] for r in results), 2),
    }

    print("\n" + "=" * 60)
    print("AGGREGATE RESULTS")
    print("=" * 60)
    print(f"  Mean score     : {aggregate['mean_score']}/5")
    print(f"  Score range    : {aggregate['min_score']} – {aggregate['max_score']}")
    print(f"  Total tokens   : {aggregate['total_tokens']}")
    print(f"  Estimated cost : ${aggregate['estimated_cost_usd']}")
    print(f"  Total time     : {aggregate['total_time_s']}s")

    # Criteria pass rates across all test cases
    criteria_keys = ["factual_accuracy", "regulatory_completeness",
                     "tone_appropriateness", "clarity", "constraint_adherence"]
    criteria_pass_rates = {}
    for key in criteria_keys:
        passes = sum(
            1 for r in results
            if r["judgment"].get("criteria_met", {}).get(key) is True
        )
        criteria_pass_rates[key] = f"{passes}/{len(results)}"

    print("\n  Criteria pass rates:")
    for k, v in criteria_pass_rates.items():
        print(f"    {k}: {v}")

    aggregate["criteria_pass_rates"] = criteria_pass_rates

    return {"results": results, "aggregate": aggregate}


# ---------------------------------------------------------------------------
# 5. SAVE RESULTS
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    output = run_evaluation()

    output_path = "evaluation_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Results saved to {output_path}")
