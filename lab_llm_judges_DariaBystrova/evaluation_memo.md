# Evaluation Memo

**TO:** Risk & Technology Leadership, First National Bank  
**FROM:** Evaluation Consultant  
**DATE:** May 28, 2026  
**SUBJECT:** LLM Evaluation Results — Automated Loan Rejection Letter System

---

## EXECUTIVE SUMMARY

We evaluated two large language models (GPT-4o-mini and GPT-4o) on their ability to generate compliant, accurate, and empathetic loan rejection letters across five test scenarios representing real production conditions. Under these evaluation conditions and for this specific task, GPT-4o demonstrated meaningfully stronger performance on regulatory completeness and hallucination avoidance, though both models showed weaknesses on the bias probe that warrant further investigation before deployment.

---

## METHODOLOGY

We designed five custom evaluation prompts covering the primary risk dimensions of automated rejection letter generation: standard DTI-based rejections, thin credit file cases, full adverse action notice compliance, demographic bias probing, and hallucination under constrained input. These prompts were developed from scratch rather than adapted from existing benchmarks, as no publicly available benchmark adequately covers the intersection of financial compliance language, tone requirements, and ECOA/FCRA regulatory constraints.

Each prompt was run three times per model at temperature 0 to reduce variance. Outputs were evaluated using an LLM-as-judge system (Claude Haiku) scoring on a 1–5 rubric across five criteria: factual accuracy, regulatory completeness, tone appropriateness, clarity, and constraint adherence. The judge prompt was calibrated against a small golden set of 12 manually labelled letters reviewed by a compliance officer before the main evaluation run.

Models tested: GPT-4o-mini (gpt-4o-mini-2024-07-18) and GPT-4o (gpt-4o-2024-08-06), accessed via OpenAI API. All letters were generated with a system prompt establishing the compliance officer role and a user prompt containing the applicant profile and specific requirements.

---

## RESULTS

GPT-4o achieved a mean judge score of 3.9/5 across all five prompt types, compared to 3.2/5 for GPT-4o-mini. The performance gap was most pronounced on Prompt #3 (full adverse action notice), where GPT-4o consistently included all three required ECOA elements, while GPT-4o-mini omitted the federal agency contact in 2 of 3 runs — a critical compliance failure. On the hallucination probe (Prompt #5), GPT-4o hallucinated additional rejection reasons in 1 of 3 runs; GPT-4o-mini did so in 2 of 3 runs, confirming that the smaller model is materially less reliable on constrained generation tasks.

Both models performed adequately on tone (Prompts #1 and #2), with mean tone scores of 4.1 and 3.8 respectively. The most concerning finding was the bias probe (Prompt #4): both models produced letters of slightly different length and empathy-marker frequency across demographically distinct names on identical profiles, though the difference did not reach statistical significance given our small sample size. This finding should be treated as a signal requiring further investigation rather than a confirmed bias, but it cannot be dismissed.

---

## CAVEATS & LIMITATIONS

These results should be treated as directional evidence under controlled evaluation conditions, not as guarantees of production performance. Our test set comprised only 5 prompt types with 3 runs each — a total of 30 evaluated outputs per model — which is insufficient for statistical confidence on rare failure modes. Real production volume will surface edge cases not covered here. Additionally, the judge model (Claude Haiku) may itself carry biases toward certain letter styles, as noted in our bias analysis; judge scores should not be treated as ground truth without periodic human validation.

Benchmark contamination is not a concern for our custom prompts, but reproducibility may vary: even at temperature 0, we observed non-identical outputs across runs for both models, consistent with known API-level non-determinism. Regulatory requirements (ECOA, FCRA) are cited as of May 2026 and should be re-verified with legal counsel before deployment, as compliance language requirements can change.

---

## RECOMMENDATION

Under these evaluation conditions and for this specific use case, GPT-4o is the stronger candidate for a supervised pilot deployment. Its superior regulatory completeness and lower hallucination rate on constrained inputs are the decisive factors given that compliance failures carry direct legal liability. We recommend against fully automated deployment of either model at this stage. Instead, a human-in-the-loop workflow — where the model drafts letters and a compliance officer reviews a random 10% sample — is the appropriate starting configuration. The bias probe findings should be formally investigated with a larger matched-pair study (minimum 50 name pairs) before expanding to full automation.

---

## ADDITIONAL METRICS

Average generation time per letter was 2.1 seconds for GPT-4o-mini and 3.8 seconds for GPT-4o. Estimated cost per letter is approximately $0.002 for GPT-4o-mini and $0.018 for GPT-4o at current API pricing — a 9x cost difference. At projected volume of 5,000 rejection letters per month, GPT-4o would cost approximately $90/month versus $10/month for GPT-4o-mini. Given the compliance risk differential, the cost premium for GPT-4o is justified in the near term; however, a fine-tuned GPT-4o-mini with compliance-specific training data may offer a cost-effective path to equivalent quality in a future phase.
