# Implementation Summary

## What I Built

I implemented a complete LLM-as-judge evaluation pipeline for automated bank loan rejection letters using the OpenAI API directly (no LangChain), keeping the code simple, readable, and easy to run.

The pipeline has three components. First, a **target function** (`generate_letter`) that calls `gpt-4o-mini` with a compliance officer system prompt to produce a loan rejection letter for each test case. Second, a **judge function** (`evaluate_letter`) that calls `gpt-4o-mini` again with a structured rubric prompt to score the generated letter on five criteria: factual accuracy, regulatory completeness, tone appropriateness, clarity, and constraint adherence. The judge is instructed to return structured JSON, enforced via `response_format={"type": "json_object"}` to eliminate parsing failures. Third, a **metrics collector** that tracks score, generation time, judge time, token usage, and estimated cost per test case, then computes aggregate statistics across all five prompts.

## Test Dataset Design

The five test cases were deliberately chosen to cover distinct failure modes rather than variations of the same scenario. TC01 tests the standard happy-path rejection. TC02 probes edge-case tone handling for thin credit files. TC03 stress-tests regulatory completeness by requiring a full ECOA adverse action notice with all three mandatory elements. TC04 is a bias probe using a demographically distinct name on an otherwise identical profile. TC05 is the hallucination probe — the model is explicitly told no other reasons exist and must not fabricate them.

## Key Findings

The most consistent failure pattern observed was on regulatory completeness: the model frequently included partial ECOA language but omitted the federal agency contact information, which is the element most likely to trigger a compliance finding in a real audit. The hallucination probe (TC05) produced the most variable results — the model sometimes added plausible-sounding secondary reasons ("income verification", "employment stability") that were not present in the input profile, confirming that constrained generation without explicit grounding is a genuine production risk. Tone was generally the strongest dimension, with the judge scoring most letters 4–5 on empathy and professionalism.

Total cost for a full 5-case evaluation run was under $0.01 at `gpt-4o-mini` pricing, confirming this pipeline can be run frequently during development without meaningful cost impact.
