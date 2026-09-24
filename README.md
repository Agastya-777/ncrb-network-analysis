# NCRB Network Analysis

AI-powered criminal network analysis system using synthetic, NCRB-distribution-seeded data. No real case data is used, by design, for privacy and legal reasons.

## Setup

```bash
pip install -r requirements.txt
```

## Project Structure

```
backend/
  data/            (owner: Track A — synthetic data generation)
  extraction/      (owner: Track A — LLM entity extraction)
  resolution/      (owner: Track A — entity resolution)
  graph/           (owner: Track B — NetworkX graph construction)
  analytics/       (owner: Track B — centrality, community, pattern detection)
  audit/           (owner: Track B — hash-chain audit log)
  schema.py        (SHARED — do not edit after this commit without both
                    developers agreeing)
  fixtures/
    resolved_entities_sample.json
    resolved_edges_sample.json
app.py             (owner: Track B — Streamlit entrypoint)
requirements.txt
README.md
```
