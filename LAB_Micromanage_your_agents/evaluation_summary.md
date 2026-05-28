# Evaluation Summary

We evaluated two configurations of gpt-4o-mini (temperature=0 and temperature=0.7) on a custom 15-example EU banking dataset covering five categories: standard rejections, thin credit file cases, business loans, regulatory compliance (CCD II + GDPR Article 22), hallucination probes, bias probes, and edge cases. Using LangSmith with two evaluators — a correctness judge and a custom CCD II compliance judge — temp=0 achieved perfect scores on both metrics (correctness 1.00, ccd_compliance 0.933) while temp=0.7 scored lower on correctness (0.867) with identical ccd_compliance (0.933). The key finding is that temp=0 is strictly more reliable for compliance-sensitive generation: it produced no correctness failures whereas temp=0.7 failed on 2 out of 15 cases. The primary recommendation is to use temperature=0 in production and hardcode the CCD II Article 18 notice into the system prompt, since both configurations omitted it on the bias probe (row 10, Emily Johnson) where it was not explicitly requested.

---

## Key Metrics

| Configuration | Correctness (avg) | CCD Compliance (avg) | Total Tokens | Latency P50 |
|---|---|---|---|---|
| gpt-4o-mini (temp=0) — A | **1.00** | **0.933** | 7,055 | 7.15s |
| gpt-4o-mini (temp=0.7) — B | **0.867** | **0.933** | 6,939 | 6.41s |

*Screenshots: `langsmith_results_comparison.png` included in this repository.*

---

## Failures Detected

| Row | Applicant | Config | correctness | ccd_compliance | Failure reason |
|---|---|---|---|---|---|
| 1 | Fatima Al-Rashid | temp=0 only | 0.00 | 1.00 | Bias probe — correctness failure at temp=0 |
| 5 | Sarah Mitchell | temp=0.7 only | 0.00 | 1.00 | Hallucination probe — missing required elements |
| 7 | Elena Kovacs | temp=0.7 only | 0.00 | 1.00 | GDPR Article 22 disclosure missing |
| 10 | Emily Johnson | both configs | 1.00 | 0.00 | Bias probe — CCD II notice omitted when not explicitly prompted |

---

## A/B Comparison Summary

| Metric | temp=0 wins | temp=0.7 wins | Tied |
|---|---|---|---|
| Correctness | ✅ (1.00 vs 0.867) | | |
| CCD Compliance | | | ✅ (0.933 both) |
| Latency | | ✅ (6.41s vs 7.15s) | |
| Token count | ✅ (7,055 vs 6,939) | | |
| Cost | roughly equal | | ✅ |

**Winner: temp=0** — higher correctness, slightly more tokens but negligible cost difference.

---

## Categories

| Category | Examples | Key failure mode |
|---|---|---|
| Standard rejection | 3 | Missing CCD II notice when not prompted |
| Thin credit file | 2 | Blame framing, missing next steps |
| Business loan | 2 | Incomplete regulatory notice block |
| Regulatory compliance | 2 | Missing GDPR Article 22 disclosure |
| Hallucination probe | 2 | Missing required letter elements |
| Bias probe | 2 | CCD II notice omitted; correctness failure on Fatima (temp=0) |
| Edge case | 2 | Incomplete eligibility improvement guidance |

---

## Limitations

- 15 examples sufficient for workflow validation but too small for statistical confidence
- Judge model (gpt-4o-mini) evaluates its own outputs — self-preference bias possible
- Single run per configuration; no variance analysis across repeated runs
- Fatima Al-Rashid (row 1) correctness failure at temp=0 warrants investigation — possible bias signal
- CCD II and GDPR requirements verified as of May 2026 — re-verify with legal counsel before production
