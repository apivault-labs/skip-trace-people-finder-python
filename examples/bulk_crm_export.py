"""Prepare matched rows for manual CRM review without printing contact data."""

import csv

from skip_trace import SkipTraceClient


client = SkipTraceClient()
rows = client.search(
    names=["Jane Example; Springfield, IL", "John Example; Madison, WI"],
    max_results=1,
    output_preset="contacts",
)

with open("skip_trace_review.csv", "w", newline="", encoding="utf-8") as stream:
    writer = csv.DictWriter(
        stream,
        fieldnames=["name", "bestPhone", "bestEmail", "currentAddress", "matchConfidence", "reviewStatus"],
    )
    writer.writeheader()
    for row in client.filter_matches(rows):
        writer.writerow({
            "name": row.get("name", ""),
            "bestPhone": row.get("bestPhone", ""),
            "bestEmail": row.get("bestEmail", ""),
            "currentAddress": row.get("currentAddress", ""),
            "matchConfidence": row.get("matchConfidence", ""),
            "reviewStatus": "manual_review_required",
        })

print("review rows written:", len(client.filter_matches(rows)))
