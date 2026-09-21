"""Fictional name lookup with compact, review-ready output."""

from skip_trace import SkipTraceClient


client = SkipTraceClient()
rows = client.search_by_name(
    "Jane Example; Springfield, IL",
    max_results=3,
    output_preset="contacts",
)

print("matched rows:", len(client.filter_matches(rows)))
print("summary status:", client.last_summary().get("status"))
