# Skip Trace — Python SDK

A thin Python client for the hosted [Skip Trace Actor](https://apify.com/apivault_labs/skip-trace-people-finder). Search authorized US public-record data by name, address, phone or email and receive structured contact records.

> **Lawful use only.** This is not a consumer-reporting service. Do not use the data for credit, employment, housing, insurance, tenant screening or other FCRA-regulated decisions. Verify important information independently.

## Install

```bash
pip install git+https://github.com/apivault-labs/skip-trace-people-finder-python.git
```

Set your Apify token in `APIFY_API_TOKEN`, then start with one small lookup:

```python
from skip_trace import SkipTraceClient

client = SkipTraceClient()
rows = client.search_by_name(
    "Jane Example; Springfield, IL",
    max_results=3,
    output_preset="contacts",
)

for row in rows:
    if row.get("success"):
        print(row.get("name"), row.get("bestPhone"), row.get("matchConfidence"))
```

The sample is fictional. Replace it only with information you are authorized to process.

## Lookup methods

```python
client.search_by_name("Jane Example; Springfield, IL", max_results=3)
client.search_by_address("123 Example Ave; Springfield, IL 62704", max_results=3)
client.search_by_phone("(202) 555-0182", max_results=3)
client.search_by_email("jane@example.com", max_results=3)
```

For mixed independent lookups:

```python
rows = client.search(
    names=["Jane Example; Springfield, IL"],
    phones=["(202) 555-0182"],
    max_results=3,
    output_preset="contacts",
)
```

Inputs are independent OR lookups; fields are not paired row by row.

## Output presets

- `contacts` — compact fields for AI, CRM and review queues;
- `flat` — spreadsheet-friendly values;
- `full` — address history, relatives and the complete public result when available.

Full remains the default for compatibility. Start with Contacts when you need a smaller response.

Every run also exposes a structured `SUMMARY` and `ERRORS` record through Apify. Use `client.last_summary()` and `client.last_errors()` after a completed call.

## Pricing

- **$6.50 per 1,000 delivered matched-person records**;
- unmatched queries have no result charge;
- the small Actor Start charge and Apify platform usage may still apply;
- no subscription or per-seat fee.

Start with `max_results=1` to `3`, review match quality, and increase the limit only when needed.

## Review-first workflow

Read the [contact-enrichment playbook](guides/review-first-contact-enrichment.md) before connecting results to a CRM. The maintained [n8n node](https://www.npmjs.com/package/n8n-nodes-apivault-skip-trace) includes a ready-to-import manual-review workflow.

## Result helpers

- `filter_matches(rows)` — keep only successful matched-person rows;
- `filter_with_phone(rows)` and `filter_with_email(rows)`;
- `best_phone(row)` and `best_email(row)`;
- `estimate_cost(expected_matches)` — estimate result charges at the current flat rate.

## Resources

- [Run Skip Trace on Apify](https://apify.com/apivault_labs/skip-trace-people-finder)
- [Review-first use case](guides/review-first-contact-enrichment.md)
- [n8n community node](https://www.npmjs.com/package/n8n-nodes-apivault-skip-trace)

## License

[MIT](LICENSE)
