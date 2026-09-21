# Review-first contact enrichment with Skip Trace

This playbook uses the hosted [Skip Trace Actor](https://apify.com/apivault_labs/skip-trace-people-finder) to turn an authorized lookup into a compact record for manual review.

Use it only when you have a lawful purpose and the right to process the submitted information. The Actor is not a consumer-reporting service. Do not use it for credit, employment, housing, insurance, tenant screening or other FCRA-regulated decisions.

## 1. Start with one independent lookup

Choose the field that matches the information you already have. The example below uses fictional data:

```python
from skip_trace import SkipTraceClient

client = SkipTraceClient()
rows = client.search_by_name(
    "Jane Example; Springfield, IL",
    max_results=3,
    output_preset="contacts",
)
```

Name, address, phone and email values are independent lookups. Do not put unrelated values into different fields and assume the Actor will treat them as one identity.

## 2. Review the match

Useful review fields include:

- the original input and search type;
- `mostLikely` and `matchConfidence`;
- name and current address;
- available phones and emails;
- the compliance notice.

A confidence score is a ranking signal, not proof of identity. Public-record information can be incomplete, stale or incorrect, so verify important details independently.

## 3. Keep the first run small

Each delivered matched-person row is billed at **$6.50 per 1,000 matches**. Unmatched queries have no result charge, while the small Actor Start charge and Apify platform usage may still apply.

Begin with `max_results=1` to `3`. Increase it only after confirming that the lookup and output are useful.

## 4. Prepare a manual-review CRM row

```python
approved = []
for row in rows:
    if row.get("success") and row.get("matchConfidence", 0) >= 60:
        approved.append({
            "name": row.get("name", ""),
            "phone": row.get("bestPhone", ""),
            "email": row.get("bestEmail", ""),
            "address": row.get("currentAddress", ""),
            "reviewStatus": "manual_review_required",
        })
```

The score threshold only prioritizes review. It must not make an eligibility or identity decision automatically.

## 5. Automate without removing review

The maintained [n8n workflow](https://github.com/apivault-labs/n8n-nodes-apivault-skip-trace/blob/main/examples/quickstart-workflow.json) prepares compact results for a review queue. Select your own Apify credential, replace the fictional sample with an authorized lookup and keep the manual approval step before any downstream action.

## Expected outcome

You finish with a small set of compact, ranked contact records ready for independent verification. Empty and invalid lookups remain visible through structured summaries and diagnostics instead of being mistaken for successful matches.

The public SDK and n8n node are thin clients to the hosted Actor. They contain no data-collection implementation, private sources, credentials or infrastructure configuration.
