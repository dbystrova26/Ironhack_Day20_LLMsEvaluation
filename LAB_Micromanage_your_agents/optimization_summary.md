# Optimization Summary

Under these evaluation conditions and for this specific EU banking compliance task, **gpt-4o-mini at temperature=0 is the optimal configuration** — it achieved perfect correctness (1.00) and identical CCD II compliance (0.93) compared to temperature=0.7 (correctness 0.87, ccd_compliance 0.93), at virtually the same cost (~$0.003 per 15-letter batch) and only marginally higher latency (7.15s vs 6.41s P50). The full gpt-4o model was not available under the current API tier, which would be the natural next candidate for maximum performance if budget allows (~17x cost increase). For production deployment, temperature=0 is the clear choice: determinism is non-negotiable for regulatory compliance letters where reproducibility and auditability are legal requirements under the EU AI Act.

---

## Cost-Performance Comparison

| Configuration | Correctness | CCD Compliance | Cost / 15 letters | Latency P50 | Recommendation |
|---|---|---|---|---|---|
| gpt-4o-mini (temp=0) | **1.00** | 0.93 | ~$0.003 | 7.15s | ✅ **Best overall** |
| gpt-4o-mini (temp=0.7) | 0.87 | 0.93 | ~$0.003 | 6.41s | ⚠️ Lower correctness |
| gpt-4o (not available) | — | — | ~$0.05 | — | 🔒 API tier required |

## When to Pick Each

- **Maximum performance** → gpt-4o-mini (temp=0): perfect correctness, same cost as temp=0.7, deterministic output for audit trails
- **Cost efficiency** → gpt-4o-mini (temp=0): both configs cost the same; temp=0 wins on quality at no extra cost
- **Best balanced** → gpt-4o-mini (temp=0): dominates on every metric that matters for compliance
- **If gpt-4o access available** → run A/B against gpt-4o-mini to justify the 17x cost premium with real correctness data before committing to production
