# Reflection

---

## Question 1: What would change if the client's data was in French?

The most immediate challenge would be benchmark availability: virtually all the benchmarks we considered (FinanceBench, BBQ, InstructEval) are English-language resources with no validated French equivalents. We would need to either find French-language financial NLP benchmarks — which are sparse and less peer-reviewed than their English counterparts — or translate our custom prompts, which introduces its own risk. Machine-translated evaluation prompts can carry subtle meaning shifts that alter what is actually being tested, particularly for legally precise language like ECOA adverse action notices, which have no direct French equivalent since ECOA is a US regulation. A French-speaking bank operating under French consumer credit law (Code de la consommation) has entirely different mandatory disclosure requirements, so the compliance criteria in our judge prompt would need to be redesigned from scratch with input from a French legal expert.

Quality verification would also become significantly harder. Our LLM-as-judge approach relies on the judge model being equally capable in French as in English — which is not guaranteed, especially for domain-specific compliance language. We would need to validate the judge's French-language performance separately before trusting its scores, ideally by running it against a set of manually labelled French letters reviewed by a native-speaking compliance officer. Human evaluation would become even more essential as a calibration anchor, since automated quality signals are less reliable in lower-resource language settings.

---

## Question 2: How do you respond if the client asks "is this model AGI-level?"

The honest answer is that "AGI-level" is not a well-defined evaluation target, and no current benchmark can answer that question — including ours. I would respond to the client by first clarifying what they likely mean in practical terms: are they asking whether the model can replace a human compliance officer entirely, or whether it performs well enough on this specific task to be trusted in production? These are very different questions, and only the second one is answerable with the evaluation we ran. For that narrower question, our results give a directional yes for supervised use with human review, and a qualified no for full automation at this stage.

If pressed on the AGI framing specifically, I would explain that even benchmarks designed to probe general reasoning — such as Humanity's Last Exam or ARC-AGI — do not measure real-world judgment, contextual adaptability, or the kind of tacit compliance knowledge a 10-year veteran loan officer carries. A model can score well on a structured benchmark and still fail unpredictably on novel edge cases in production. The appropriate caveat is always: these results hold under the conditions we tested, for this task, at this point in time. Model capabilities change with each version update, and evaluation must be treated as an ongoing process rather than a one-time certification.

---

## Question 3: What is the one thing you could not evaluate without a human?

The one dimension I could not evaluate without a human is whether a rejection letter genuinely respects the dignity of the applicant — what might be called the lived experience of receiving it. Our judge prompt can assess empathy markers at the lexical level ("we understand your situation", "we encourage you to reapply"), and it can verify regulatory completeness. What it cannot assess is whether a real person — perhaps someone who has been struggling financially, or who applied for a loan to cover a medical emergency — would feel treated with respect after reading the letter. This requires a reader who can hold both the emotional register of the letter and the psychological context of the recipient simultaneously, something no current LLM judge reliably does.

In practice, I would incorporate human evaluation by recruiting a small panel of 5–10 participants representing diverse financial backgrounds and literacy levels, having them read a sample of generated letters and rate them on perceived fairness, clarity, and emotional impact using a structured survey. This would run in parallel with the automated judge, not replace it — the automated judge handles scale and consistency, while human raters calibrate the dimensions that matter most to the people the system actually affects. Periodic human re-evaluation (e.g. quarterly) would also serve as a check against model drift, catching cases where an updated model version produces subtly different tone that automated metrics miss.
