# Custom Evaluator & A/B Comparison

---

## Step 13: Custom Evaluator Documentation

### What it measures

The `ccd_compliance_evaluator` measures a single, binary, legally-critical dimension:
**does the generated letter include a reference to the applicant's right to request
a full explanation under EU Consumer Credit Directive (CCD II) Article 18?**

This is separate from the general `correctness` evaluator — a letter can be
well-written, accurate, and empathetic (correctness=1) but still legally
non-compliant if it omits the CCD II notice (ccd_compliance=0).

---

### Evaluation criteria and prompt design

The evaluator checks for all three required elements:

1. A clear statement that the loan has been denied
2. The specific reason(s) for rejection
3. A reference to the applicant's right to request a full explanation (CCD II Article 18)

**Scoring:**
- `1` (pass) — all three elements present
- `0` (fail) — any element missing

**Implementation:** plain OpenAI API call with `response_format={"type": "json_object"}`
rather than openevals `create_llm_as_judge`, because openevals does not support
dictionary-access syntax (`{outputs[answer]}`) in custom prompt strings.

```python
def ccd_compliance_evaluator(inputs, outputs, reference_outputs):
    letter = outputs.get("answer", "")
    # builds prompt with letter injected directly
    # calls gpt-4o-mini at temperature=0
    # returns {"key": "ccd_compliance", "score": 0 or 1, "comment": "..."}
```

---

### Results from custom evaluator

| Config | ccd_compliance AVG | Failures | Failure cases |
|---|---|---|---|
| gpt4o-mini-t0  | **0.933** | 1/15 | Row 10 (Emily Johnson — bias probe) |
| gpt4o-mini-t07 | **0.933** | 1/15 | Row 10 (Emily Johnson — bias probe) |

Both configurations failed on exactly the same case — Emily Johnson (bias probe,
TC04), where the prompt did not explicitly request the CCD II notice. This confirms
the failure is **systemic** (model behaviour) rather than configuration-specific
(not caused by temperature).

---

### What the custom evaluator adds beyond correctness

| Scenario | correctness | ccd_compliance | Insight |
|---|---|---|---|
| Good letter, CCD II included | 1 | 1 | Fully compliant |
| Good letter, CCD II missing | 0 | 0 | Both catch it |
| Correct reasons, CCD II missing | 1 | 0 | **Only ccd_compliance catches this** |
| Wrong reasons, CCD II present | 0 | 1 | **Only correctness catches this** |

The custom evaluator is most valuable for catching letters that score well on
general correctness but fail the specific regulatory compliance check — a failure
mode that matters most for production EU banking deployments under CCD II and
the EU AI Act high-risk AI requirements.

---

### Reflection on custom evaluation dimensions

Running both evaluators confirmed that **general correctness is not sufficient**
for compliance-sensitive domains. A model can follow instructions well and still
omit a legally mandatory disclosure. In production, the CCD II notice evaluator
would serve as a hard gate — any letter scoring 0 on ccd_compliance would be
blocked from sending regardless of its correctness score. This pattern (general
quality judge + domain-specific compliance gate) is the recommended architecture
for regulated industry LLM deployments.

---

## Step 14: A/B Comparison Results

### Configurations compared

| Config | Model | Temperature | Experiment ID |
|---|---|---|---|
| A | gpt-4o-mini | 0.0 | gpt4o-mini-t0-e88ff3d0 |
| B | gpt-4o-mini | 0.7 | gpt4o-mini-t07-ea0d0011 |

*Note: gpt-4o was not available under the current OpenAI API tier
(PermissionDeniedError 403). Temperature variation was used as the A/B
comparison dimension instead.*

---

### Performance metrics

| Config | Correctness | CCD Compliance | P50 Latency | P99 Latency | Total Tokens |
|---|---|---|---|---|---|
| gpt4o-mini-t0  | **1.00** | 0.93 | 7.15s | 15.22s | 7,055 |
| gpt4o-mini-t07 | 0.87 | 0.93 | **6.41s** | 13.16s | 6,939 |

---

### Cost information

| Config | Input Tokens | Output Tokens | Total Cost (15 letters) | Cost per letter |
|---|---|---|---|---|
| gpt4o-mini-t0  | 1,791 | 5,294 | $0.0034 | $0.000227 |
| gpt4o-mini-t07 | 1,791 | 5,148 | $0.0034 | $0.000220 |

Both configurations cost **effectively the same** — the output token difference
(146 tokens across 15 letters) produces a cost delta of less than $0.0001.

---

### Fair comparison assurance

- Same dataset: `eu-loan-rejection-letters` (15 examples)
- Same evaluators: `correctness_evaluator` + `ccd_compliance_evaluator`
- Same judge model: `gpt-4o-mini` for both evaluators
- Same system prompt: identical compliance officer instructions
- Only variable: temperature (0 vs 0.7)
- Both runs: 0% error rate, all 15 examples processed

---

### Key finding

At identical cost, **temperature=0 delivers higher correctness (1.00 vs 0.87)**
with no trade-off on CCD compliance (tied at 0.93). The only advantage of
temperature=0.7 is a 0.74s faster median latency, which is operationally
irrelevant for batch letter generation. Temperature=0 is the recommended
production configuration.
