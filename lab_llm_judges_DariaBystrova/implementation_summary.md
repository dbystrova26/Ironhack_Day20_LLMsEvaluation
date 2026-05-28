# Implementation Summary

## What I Built

I implemented a complete LLM-as-judge evaluation pipeline for automated bank loan rejection letters using the OpenAI and Anthropic APIs directly (no LangChain), producing both a single-model evaluation and a three-way A/B comparison with visualisation.

The pipeline has three components. First, a **target function** that generates a loan rejection letter for each test case — using either `gpt-4o-mini` (via OpenAI) or `claude-sonnet-4-5-20250929` (via Anthropic). Second, a **judge function** that always uses `gpt-4o-mini` to score the generated letter on five criteria: factual accuracy, regulatory completeness, tone appropriateness, clarity, and constraint adherence, returning structured JSON enforced via `response_format={"type": "json_object"}`. Third, a **metrics collector** that tracks score, generation time, token usage, and estimated cost per test case, then produces an aggregate summary and a four-panel matplotlib dashboard replicating the LangSmith comparison view.

## Three Configurations Compared

| Config | Model | Temperature |
|--------|-------|-------------|
| A | gpt-4o-mini | 0.0 (deterministic) |
| B | gpt-4o-mini | 0.7 (creative) |
| C | claude-sonnet-4-5-20250929 | 0.0 |

## Test Dataset Design

The five test cases cover distinct failure modes: standard DTI-based rejection (TC01), thin credit file edge case (TC02), full ECOA adverse action notice (TC03), demographic bias probe with a culturally distinct name on an identical profile (TC04), and hallucination under strictly constrained input (TC05).

## Key Findings

**Regulatory completeness** was the most consistent failure dimension across all three configurations. TC04 and TC05 — which did not explicitly mention ECOA in the prompt — produced letters missing the adverse action notice, confirming the model will not self-apply compliance requirements unless instructed. This is a critical production insight: the ECOA disclosure must be hardcoded into the system prompt, not left to individual user prompts.

**Hallucination** (TC05) was well-controlled across all configurations — no fabricated rejection reasons were detected in any run, which is the most important safety result for this use case.

**Claude Sonnet** produced longer, more detailed letters with richer empathy language, scoring consistently on tone. The cost difference was significant: Claude Sonnet costs approximately 20x more per letter than gpt-4o-mini at current API pricing ($0.003–0.005 per letter vs ~$0.0001), which matters at production volume (5,000 letters/month = ~$15–25 for Claude vs ~$0.50 for gpt-4o-mini).

**Temperature effect** on gpt-4o-mini was modest for quality scores but visible in letter length and token count — temp=0.7 produced slightly more varied, sometimes warmer language but also introduced minor inconsistencies in regulatory boilerplate phrasing.

Total cost for the full three-way evaluation run (15 letters generated + 15 judge calls) was under $0.05, confirming the pipeline can be run iteratively during development at negligible cost.
