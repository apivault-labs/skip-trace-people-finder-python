"""
Bulk skip-trace a list of names and export reachable contacts to CSV
ready for CRM import (HubSpot / Pipedrive / Salesforce).

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/bulk_crm_export.py
"""

import csv

from skip_trace import SkipTraceClient


NAMES = [
    "James E Whitsitt; Dallas, TX",
    "Amalia Castillo; Dallas, TX 75228",
    "Robert Johnson; Austin, TX",
]


def main() -> None:
    client = SkipTraceClient()

    print(f"Estimated cost: ${client.estimate_cost(len(NAMES) * 5, 'basic')}")

    people = client.search(names=NAMES, tier="basic", max_results=5)

    # Only keep records we can actually reach
    reachable = client.filter_with_phone(people)

    with open("skip_trace_contacts.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "age", "address", "phone", "profile_url"])
        for p in reachable:
            writer.writerow([
                p.get("name", ""),
                p.get("age", ""),
                p.get("currentAddress") or p.get("address", ""),
                client.best_phone(p) or "",
                p.get("profileUrl", ""),
            ])

    print(f"Wrote {len(reachable)} contacts to skip_trace_contacts.csv")


if __name__ == "__main__":
    main()
