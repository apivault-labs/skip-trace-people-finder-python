"""Reverse lookup using a reserved fictional US phone number."""

from skip_trace import SkipTraceClient


client = SkipTraceClient()
rows = client.search_by_phone(
    "(202) 555-0182",
    max_results=3,
    output_preset="contacts",
)

print("matched rows:", len(client.filter_matches(rows)))
print("diagnostics:", len(client.last_errors()))
