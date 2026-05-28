# Reflection

---

## Question 1: What would change if the client's data was in French?

Since our client is already a European bank, French is a realistic operating language rather than a hypothetical edge case — many EU banks operate across multiple member states with multilingual customer bases. The most immediate challenge would be benchmark availability: virtually all the benchmarks we considered (FinanceBench, BBQ, InstructEval) are English-language resources with no validated French equivalents. We would need to either find French-language financial NLP benchmarks — which are sparse and less peer-reviewed — or translate our custom prompts, which introduces risk. Machine-translated evaluation prompts can carry subtle meaning shifts that alter what is actually being tested, particularly for legally precise language like CCD II Article 18 explanation notices, which require specific phrasing to be legally valid in French jurisdiction.

Quality verification would also become significantly harder. Our LLM-as-judge approach relies on the judge model being equally capable in French as in English — which is not guaranteed for domain-specific compliance language. We would need to validate the judge's French-language performance separately before trusting its scores, ideally by running it against a set of manually labelled French letters reviewed by a native-speaking compliance officer. This connects directly to the EBA Guidelines requirement that institutions be able to explain automated credit decisions to applicants in their own language — the evaluation framework must match the language of deployment, not just the language of development.

---

## Question 2: How do you respond if the client asks "is this model AGI-level?"

The honest answer is that "AGI-level" is not a well-defined evaluation target, and no current benchmark can answer that question — including ours. I would respond to the client by first clarifying what they likely mean in practical terms: are they asking whether the model can replace a human compliance officer entirely, or whether it performs well enough on this specific task to be trusted in a supervised production workflow? These are very different questions, and only the second one is answerable with the evaluation we ran. For that narrower question, our results give a directional yes for supervised use with human review, and a qualified no for full automation — particularly given the systemic regulatory disclosure gap we identified across all model configurations.

If pressed on the AGI framing specifically, I would explain that even benchmarks designed to probe general reasoning — such as Humanity's Last Exam or ARC-AGI — do not measure real-world regulatory judgment, contextual adaptability under novel EU legislation, or the tacit compliance knowledge a senior loan officer carries after years of practice. A model can score well on a structured benchmark and still fail unpredictably on novel edge cases in production. Under EU AI Act requirements (which classify credit scoring as a high-risk AI use case), the bank also has a legal obligation to conduct ongoing human oversight regardless of model performance — so the AGI question is not just technically premature, it is also legally irrelevant for this deployment context.

---

## Question 3: What is the one thing you could not evaluate without a human?

The one dimension I could not evaluate without a human is whether a rejection letter genuinely respects the dignity of the applicant — what might be called the lived experience of receiving it. Our judge prompt can assess empathy markers at the lexical level ("we understand your situation", "we encourage you to reapply"), and it can verify regulatory completeness. What it cannot assess is whether a real person — perhaps someone who has been struggling financially, or who applied for a loan to cover a medical emergency — would feel treated with respect after reading the letter. This requires a reader who can hold both the emotional register of the letter and the psychological context of the recipient simultaneously, something no current LLM judge reliably does.

In practice, I would incorporate human evaluation by recruiting a small panel of 5–10 participants representing diverse financial backgrounds and literacy levels across the EU markets the bank serves, having them read a sample of generated letters and rate them on perceived fairness, clarity, and emotional impact using a structured survey. This would run in parallel with the automated judge — not replace it. This approach also aligns with GDPR Article 22 requirements: where automated decisions significantly affect individuals, the bank must provide meaningful human review on request, which means human evaluators need to be involved in validating that the letters produced by the system meet the standard required for that human review to be genuine rather than performative.
