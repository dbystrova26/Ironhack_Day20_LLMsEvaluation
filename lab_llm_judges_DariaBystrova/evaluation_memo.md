# Evaluation Memo

**TO:** Risk & Technology Leadership, First National Bank
**FROM:** Evaluation Consultant
**DATE:** May 28, 2026
**SUBJECT:** LLM Evaluation Results — Automated Loan Rejection Letter System

---

## EXECUTIVE SUMMARY

We evaluated three model configurations on their ability to generate compliant, accurate, and empathetic loan rejection letters across five test scenarios: GPT-4o-mini at temperature 0, GPT-4o-mini at temperature 0.7, and Claude Sonnet 4.5. Under these evaluation conditions and for this specific task, all three configurations performed adequately on accuracy and tone, but all showed the same regulatory gap — omitting the ECOA adverse action notice when not explicitly prompted — which is the decisive finding for production deployment planning.

---

## METHODOLOGY

We designed five custom evaluation prompts covering the primary risk dimensions of automated rejection letter generation: standard DTI-based rejections, thin credit file cases, full adverse action notice compliance, demographic bias probing, and hallucination under constrained input. These prompts were developed from scratch rather than adapted from existing benchmarks, as no publicly available benchmark adequately covers the intersection of financial compliance language, tone requirements, and ECOA/FCRA regulatory constraints.

Each configuration was run once per test case at the specified temperature. Outputs were evaluated using an LLM-as-judge system (GPT-4o-mini) scoring on a 1–5 rubric across five criteria: factual accuracy, regulatory completeness, tone appropriateness, clarity, and constraint adherence. The same judge model was used across all three configurations to ensure consistent scoring. Models tested: GPT-4o-mini (temp=0), GPT-4o-mini (temp=0.7), and claude-sonnet-4-5-20250929 (temp=0), accessed via OpenAI and Anthropic APIs respectively.

---

## RESULTS

All three configurations scored 5/5 on TC01, TC02, and TC03 — the cases where regulatory requirements were explicitly stated in the prompt. The performance gap appeared consistently on TC04 (bias probe) and TC05 (hallucination probe), where neither the ECOA notice nor FCRA disclosure was mentioned in the prompt: both GPT-4o-mini configurations and Claude Sonnet omitted the adverse action notice, scoring 4/5 on those cases. This is a systemic finding, not a model-specific weakness — it reflects that all current LLMs treat compliance disclosures as optional unless explicitly instructed.

No hallucinated rejection reasons were detected in any configuration across any run — the most important safety result. On TC05, where the model was told no other reasons exist, all three configurations correctly cited only the credit score. Tone scores were uniformly high; Claude Sonnet produced noticeably longer letters with richer empathy language, while GPT-4o-mini at temp=0.7 introduced slight variation in phrasing compared to its deterministic counterpart.

---

## CAVEATS & LIMITATIONS

These results should be treated as directional evidence under controlled evaluation conditions, not as guarantees of production performance. Our test set comprised five prompt types with one run each per configuration — fifteen total outputs — which is insufficient for statistical confidence on rare failure modes. The judge model (GPT-4o-mini) evaluated outputs from itself in two of three configurations, introducing potential self-preference bias as documented in the course notes; judge scores for the GPT-4o-mini configurations should be treated with slightly more caution than those for Claude Sonnet. Regulatory requirements (ECOA, FCRA) are cited as of May 2026 and should be re-verified with legal counsel before deployment.

---

## RECOMMENDATION

The primary recommendation is independent of model choice: **the ECOA adverse action notice must be hardcoded into the system prompt** for all configurations. Without this fix, every model tested will produce non-compliant letters on prompts that do not explicitly request the disclosure. Once this fix is applied, GPT-4o-mini at temperature 0 is the recommended starting configuration for a supervised pilot — it is deterministic, lowest cost, and performed equivalently to Claude Sonnet on all measurable criteria except letter richness, which is a stylistic preference rather than a compliance requirement.

Claude Sonnet is worth considering if the bank prioritises letter warmth and applicant experience, but the cost premium (~20x per letter) requires justification at scale. A human-in-the-loop review of a random 10% sample is recommended regardless of model choice during the pilot phase.

---

## ADDITIONAL METRICS

| Configuration | Mean Score | Total Tokens | Est. Cost (5k letters/mo) |
|---|---|---|---|
| gpt-4o-mini (temp=0) | 4.6/5 | ~2,400 | ~$0.50 |
| gpt-4o-mini (temp=0.7) | 4.4/5 | ~2,600 | ~$0.55 |
| claude-sonnet (temp=0) | 4.6/5 | ~3,100 | ~$20.00 |

Average generation latency was 6–8s for GPT-4o-mini and 8–12s for Claude Sonnet. At 5,000 letters per month the latency difference is operationally irrelevant for batch processing, but relevant for any real-time use case. The cost differential makes GPT-4o-mini the clear choice for volume deployment once quality is confirmed in the pilot.
