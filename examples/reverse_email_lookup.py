"""Authorized reverse-email lookup with a fictional sample address."""

from skip_trace import SkipTraceClient


client = SkipTraceClient()
rows = client.search_by_email(
    "jane@example.com",
    max_results=3,
    output_preset="contacts",
)

print("matched rows:", len(client.filter_matches(rows)))
