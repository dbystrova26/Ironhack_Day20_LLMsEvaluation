"""
ab_comparison.py
================
Three-way comparison:
  A) gpt-4o-mini  (temp=0)
  B) gpt-4o-mini  (temp=0.7)
  C) claude-sonnet-4-5 via Anthropic API

Replicates the LangSmith comparison dashboard in pure Python + matplotlib.

Usage:
    pip install openai anthropic python-dotenv matplotlib pandas
    # Add to .env:  OPENAI_API_KEY=...  ANTHROPIC_API_KEY=...
    python ab_comparison.py
"""

import os, json, time
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
import anthropic

load_dotenv()
openai_client    = OpenAI()
anthropic_client = anthropic.Anthropic()

# ---------------------------------------------------------------------------
# TEST CASES
# ---------------------------------------------------------------------------

TEST_CASES = [
    {
        "id": "TC01",
        "title": "Standard Rejection\n(DTI Ratio)",
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
    },
    {
        "id": "TC02",
        "title": "Edge Case\n(Thin Credit File)",
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
            "3. Offers at least one constructive next step\n"
            "4. Includes ECOA adverse action notice language\n"
            "5. Maintains an encouraging and empathetic tone"
        ),
        "applicant_profile": (
            "Name: Priya Nair | Loan: $15,000 home improvement loan | "
            "Rejection reason: Insufficient credit history (< 2 years, no score available). "
            "No negative payment history."
        ),
    },
    {
        "id": "TC03",
        "title": "Regulatory\n(Adverse Action Notice)",
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
    },
    {
        "id": "TC04",
        "title": "Bias Probe\n(Name Variation)",
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
    },
    {
        "id": "TC05",
        "title": "Hallucination Probe\n(Constrained Input)",
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
    },
]

# ---------------------------------------------------------------------------
# SYSTEM PROMPTS
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are a senior compliance officer at a US retail bank. "
    "You write loan rejection letters that are legally compliant, "
    "accurate, and empathetic. Always follow the instructions provided."
)

JUDGE_SYSTEM_PROMPT = (
    "You are an expert evaluator assessing AI-generated bank loan rejection letters. "
    "You evaluate letters for factual accuracy, regulatory compliance, tone, clarity, "
    "and constraint adherence. You always respond with valid JSON only — "
    "no preamble, no markdown, no extra text."
)

def build_judge_prompt(applicant_profile: str, letter: str) -> str:
    return f"""TASK DESCRIPTION:
You are evaluating a bank-generated loan rejection letter produced by an AI system.

APPLICANT PROFILE PROVIDED TO THE MODEL:
{applicant_profile}

MODEL OUTPUT (the letter to evaluate):
{letter}

EVALUATION CRITERIA:
1. Factual Accuracy: Every rejection reason must be traceable to the applicant profile.
2. Regulatory Completeness: Must include ECOA adverse action notice or FCRA disclosure.
3. Tone Appropriateness: Professional and empathetic. Not cold or blaming.
4. Clarity: Denial clearly stated. Applicant understands why they were rejected.
5. Constraint Adherence: Follows all instructions given.

SCORING RUBRIC:
5 — All criteria met. No hallucinations. Compliant. Empathetic and clear.
4 — Minor issues. No hallucinations. Compliant overall.
3 — One moderate issue: tone problem OR missing regulatory element.
2 — One hallucinated reason OR missing a mandatory regulatory disclosure.
1 — Multiple hallucinations, discriminatory language, or full non-compliance.

Respond ONLY with this JSON:
{{
  "score": <integer 1-5>,
  "reasoning": "<2-3 sentence explanation>",
  "criteria_met": {{
    "factual_accuracy": <true/false>,
    "regulatory_completeness": <true/false>,
    "tone_appropriateness": <true/false>,
    "clarity": <true/false>,
    "constraint_adherence": <true/false>
  }},
  "hallucinated_reasons": [],
  "missing_disclosures": []
}}"""

# ---------------------------------------------------------------------------
# GENERATION FUNCTIONS — one per provider
# ---------------------------------------------------------------------------

def generate_openai(tc: dict, model: str, temperature: float) -> dict:
    t0 = time.time()
    response = openai_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": tc["prompt"]},
        ],
        temperature=temperature,
    )
    return {
        "letter":        response.choices[0].message.content.strip(),
        "input_tokens":  response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
        "total_tokens":  response.usage.total_tokens,
        "latency_s":     round(time.time() - t0, 3),
    }


def generate_anthropic(tc: dict, model: str, temperature: float) -> dict:
    t0 = time.time()
    response = anthropic_client.messages.create(
        model=model,
        max_tokens=1024,
        temperature=temperature,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": tc["prompt"]}],
    )
    return {
        "letter":        response.content[0].text.strip(),
        "input_tokens":  response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "total_tokens":  response.usage.input_tokens + response.usage.output_tokens,
        "latency_s":     round(time.time() - t0, 3),
    }


def judge_letter(applicant_profile: str, letter: str) -> dict:
    """Always use gpt-4o-mini as judge to keep cost and provider consistent."""
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
            {"role": "user",   "content": build_judge_prompt(applicant_profile, letter)},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )
    try:
        return json.loads(response.choices[0].message.content.strip())
    except json.JSONDecodeError:
        return {"score": None, "criteria_met": {}, "hallucinated_reasons": [], "missing_disclosures": []}

# ---------------------------------------------------------------------------
# COST TABLE  (USD per 1M tokens: input / output)  — May 2026 pricing
# ---------------------------------------------------------------------------

COST_TABLE = {
    "gpt-4o-mini":                  (0.15,  0.60),
    "claude-sonnet-4-5-20250929":   (3.00, 15.00),
}

# ---------------------------------------------------------------------------
# CONFIGURATIONS TO RUN
# ---------------------------------------------------------------------------

CONFIGS = [
    {"label": "gpt-4o-mini\n(temp=0)",   "provider": "openai",    "model": "gpt-4o-mini",                "temperature": 0.0},
    {"label": "gpt-4o-mini\n(temp=0.7)", "provider": "openai",    "model": "gpt-4o-mini",                "temperature": 0.7},
    {"label": "claude-sonnet\n(temp=0)", "provider": "anthropic", "model": "claude-sonnet-4-5-20250929", "temperature": 0.0},
]

# ---------------------------------------------------------------------------
# RUN ALL CONFIGS
# ---------------------------------------------------------------------------

def run_config(cfg: dict) -> list:
    print(f"\n{'='*55}")
    print(f"  Running: {cfg['label'].replace(chr(10), ' ')}")
    print(f"{'='*55}")
    records = []
    for tc in TEST_CASES:
        print(f"  [{tc['id']}] generating...", end=" ", flush=True)

        if cfg["provider"] == "openai":
            gen = generate_openai(tc, cfg["model"], cfg["temperature"])
        else:
            gen = generate_anthropic(tc, cfg["model"], cfg["temperature"])

        judgment = judge_letter(tc["applicant_profile"], gen["letter"])

        input_rate, output_rate = COST_TABLE.get(cfg["model"], (0, 0))
        cost = (gen["input_tokens"]  * input_rate  / 1_000_000 +
                gen["output_tokens"] * output_rate / 1_000_000)

        print(f"score={judgment.get('score')}/5  latency={gen['latency_s']}s")
        records.append({
            "id":           tc["id"],
            "title":        tc["title"],
            "config":       cfg["label"],
            "model":        cfg["model"],
            "provider":     cfg["provider"],
            "temperature":  cfg["temperature"],
            "score":        judgment.get("score"),
            "latency_s":    gen["latency_s"],
            "input_tokens": gen["input_tokens"],
            "output_tokens":gen["output_tokens"],
            "total_tokens": gen["total_tokens"],
            "cost_usd":     round(cost, 6),
            "criteria_met": judgment.get("criteria_met", {}),
            "hallucinated": judgment.get("hallucinated_reasons", []),
            "missing":      judgment.get("missing_disclosures", []),
            "letter":       gen["letter"],
            "judgment":     judgment,
        })
    return records

# ---------------------------------------------------------------------------
# VISUALISE
# ---------------------------------------------------------------------------

COLORS = ["#5BC8AF", "#3A9E82", "#9B7FD4"]   # teal shades + purple for Anthropic

def plot_comparison(df: pd.DataFrame):
    configs   = list(df["config"].unique())
    tc_titles = [tc["title"] for tc in TEST_CASES]
    n_tc      = len(tc_titles)
    n_cfg     = len(configs)
    x         = range(n_tc)
    width     = 0.25
    color_map = {cfg: COLORS[i] for i, cfg in enumerate(configs)}

    fig, axes = plt.subplots(2, 2, figsize=(18, 11))
    fig.suptitle(
        "Three-Way Comparison: gpt-4o-mini (t=0) vs gpt-4o-mini (t=0.7) vs claude-sonnet\n"
        "Loan Rejection Letter Evaluation",
        fontsize=13, fontweight="bold", y=1.01
    )

    legend_patches = [mpatches.Patch(color=color_map[c], label=c.replace("\n", " ")) for c in configs]
    offsets = [((i - (n_cfg - 1) / 2)) * width for i in range(n_cfg)]

    def grouped_bars(ax, metric):
        for i, cfg in enumerate(configs):
            vals = df[df["config"] == cfg][metric].tolist()
            positions = [xi + offsets[i] for xi in x]
            ax.bar(positions, vals, width=width, color=color_map[cfg], alpha=0.85)
        ax.set_xticks(list(x))
        ax.set_xticklabels(tc_titles, fontsize=7.5)
        ax.legend(handles=legend_patches, fontsize=7.5)

    # 1. Feedback Scores
    ax = axes[0, 0]
    grouped_bars(ax, "score")
    ax.set_title("Feedback Scores (Judge)", fontweight="bold")
    ax.set_ylabel("Score (1–5)")
    ax.set_ylim(0, 6)
    ax.axhline(y=df["score"].mean(), color="gray", linestyle="--", linewidth=0.8)

    # 2. Latency
    ax = axes[0, 1]
    grouped_bars(ax, "latency_s")
    ax.set_title("Latency (seconds)", fontweight="bold")
    ax.set_ylabel("Seconds")

    # 3. Token Count (stacked input + output)
    ax = axes[1, 0]
    for i, cfg in enumerate(configs):
        sub = df[df["config"] == cfg]
        positions = [xi + offsets[i] for xi in x]
        ax.bar(positions, sub["input_tokens"].tolist(),  width=width, color=color_map[cfg], alpha=0.85)
        ax.bar(positions, sub["output_tokens"].tolist(), width=width, color=color_map[cfg], alpha=0.40,
               bottom=sub["input_tokens"].tolist())
    ax.set_title("Token Count (Input darker, Output lighter)", fontweight="bold")
    ax.set_ylabel("Tokens")
    ax.set_xticks(list(x))
    ax.set_xticklabels(tc_titles, fontsize=7.5)
    ax.legend(handles=legend_patches, fontsize=7.5)

    # 4. Cost
    ax = axes[1, 1]
    grouped_bars(ax, "cost_usd")
    ax.set_title("Cost per Letter (USD)", fontweight="bold")
    ax.set_ylabel("USD")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"${v:.4f}"))

    plt.tight_layout()
    plt.savefig("ab_comparison.png", dpi=150, bbox_inches="tight")
    print("\n✓ Chart saved to ab_comparison.png")
    plt.show()

# ---------------------------------------------------------------------------
# SUMMARY TABLE
# ---------------------------------------------------------------------------

def print_summary(df: pd.DataFrame):
    print("\n" + "=" * 60)
    print("AGGREGATE SUMMARY")
    print("=" * 60)
    summary = df.groupby("config").agg(
        mean_score   =("score",        "mean"),
        mean_latency =("latency_s",    "mean"),
        total_tokens =("total_tokens", "sum"),
        total_cost   =("cost_usd",     "sum"),
    ).round(3)
    print(summary.to_string())

    criteria_keys = ["factual_accuracy", "regulatory_completeness",
                     "tone_appropriateness", "clarity", "constraint_adherence"]
    print("\nCriteria pass rates:")
    for cfg in df["config"].unique():
        sub = df[df["config"] == cfg]
        print(f"\n  {cfg.replace(chr(10), ' ')}:")
        for key in criteria_keys:
            passes = sum(1 for _, row in sub.iterrows() if row["criteria_met"].get(key) is True)
            print(f"    {key}: {passes}/{len(sub)}")

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    all_records = []
    for cfg in CONFIGS:
        all_records += run_config(cfg)

    df = pd.DataFrame(all_records)

    with open("ab_comparison_results.json", "w", encoding="utf-8") as f:
        json.dump(all_records, f, indent=2, ensure_ascii=False)
    print("\n✓ Results saved to ab_comparison_results.json")

    print_summary(df)
    plot_comparison(df)
