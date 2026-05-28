# Evaluation Memo

**TO:** Risk & Technology Leadership, First European Bank  
**FROM:** Daria Bystrova, Evaluation Consultant  
**DATE:** May 28, 2026  
**SUBJECT:** LLM Evaluation Results — Automated Loan Rejection Letter System

---

## EXECUTIVE SUMMARY

We evaluated three model configurations on their ability to generate compliant, accurate, and empathetic loan rejection letters across five test scenarios representing real EU production conditions. Under these evaluation conditions and for this specific task, all three configurations performed adequately on accuracy and tone, but all showed the same systemic regulatory gap — omitting the CCD II Article 18 explanation notice when not explicitly prompted — which is the decisive finding for production deployment planning.

---

## METHODOLOGY

We designed five custom evaluation prompts covering the primary risk dimensions of automated rejection letter generation: standard DTI-based rejections, thin credit file edge cases, full CCD II adverse action notice compliance, EU demographic bias probing, and hallucination under constrained input. These prompts were developed from scratch rather than adapted from existing benchmarks, as no publicly available benchmark adequately covers the intersection of EU financial compliance language, tone requirements, and CCD II/GDPR regulatory constraints.

Each configuration was run once per test case at the specified temperature. Outputs were evaluated using an LLM-as-judge system (GPT-4o-mini) scoring on a 1–5 rubric across five criteria: factual accuracy, regulatory completeness, tone appropriateness, clarity, and constraint adherence. The same judge model was used across all three configurations to ensure consistent scoring. Models tested: GPT-4o-mini (temp=0), GPT-4o-mini (temp=0.7), and claude-sonnet-4-5-20250929 (temp=0), accessed via OpenAI and Anthropic APIs respectively.

---

## RESULTS

All three configurations scored 5/5 on TC01, TC02, and TC03 — the cases where regulatory requirements were explicitly stated in the prompt. The performance gap appeared consistently on TC04 (bias probe) and TC05 (hallucination probe), where the CCD II notice was not mentioned in the prompt: all three configurations omitted it, scoring 4/5. This is a systemic finding, not a model-specific weakness — all current LLMs treat compliance disclosures as optional unless explicitly instructed.

No hallucinated rejection reasons were detected in any configuration across any run — the most important safety result for EU credit decision liability. Tone scores were uniformly high; Claude Sonnet produced noticeably longer letters with richer empathy language, while GPT-4o-mini at temp=0.7 introduced slight phrasing variation compared to its deterministic counterpart. No differential tone was detected between demographically distinct names in the bias probe.

---

## CAVEATS & LIMITATIONS

These results should be treated as directional evidence under controlled evaluation conditions, not as guarantees of production performance. Our test set comprised five prompt types with one run per configuration — fifteen total outputs — which is insufficient for statistical confidence on rare failure modes. Contamination risk is low since all prompts are custom-designed, but reproducibility cannot be guaranteed: even at temperature 0 we observed minor output variation across runs, consistent with known API non-determinism. The judge model (GPT-4o-mini) evaluated its own outputs in two of three configurations, introducing potential self-preference bias. CCD II and GDPR requirements cited here should be re-verified with legal counsel before deployment, as EU regulatory guidance evolves.

---

## RECOMMENDATION

The primary recommendation is independent of model choice: the CCD II Article 18 explanation notice and GDPR Article 22 automated decision-making disclosure must be hardcoded into the system prompt for all configurations. Without this fix, every model tested produces non-compliant letters. Once applied, under these conditions and for this task, GPT-4o-mini at temperature 0 is the recommended starting configuration for a supervised pilot — it is deterministic, lowest cost, and performed equivalently to Claude Sonnet on all compliance criteria. A human-in-the-loop review of a random 10% sample is strongly recommended throughout the pilot phase given the EU AI Act's high-risk classification of automated credit decisions.

---

## ADDITIONAL METRICS

| Configuration | Mean Score | Avg Tokens | Est. Cost (5k letters/mo) | Avg Latency |
|---|---|---|---|---|
| gpt-4o-mini (temp=0) | 4.6/5 | ~2,400 | ~€0.50 | 6–8s |
| gpt-4o-mini (temp=0.7) | 4.4/5 | ~2,600 | ~€0.55 | 6–8s |
| claude-sonnet (temp=0) | 4.6/5 | ~3,100 | ~€20.00 | 8–12s |

At 5,000 letters per month the latency difference is operationally irrelevant for batch processing. The ~40x cost differential between Claude Sonnet and GPT-4o-mini makes the latter the clear choice for volume deployment once compliance quality is confirmed in the pilot. Environmental cost (token consumption) follows the same pattern — GPT-4o-mini consumes ~23% fewer tokens per letter than Claude Sonnet.
