"""
Address lookup: find people associated with a street address.

Useful for real-estate / investor outreach — turn a property address
into owner contacts.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/address_residents.py
"""

from skip_trace import SkipTraceClient


def main() -> None:
    client = SkipTraceClient()

    residents = client.search_by_address(
        "2551 Pinebluff Dr; Dallas, TX 75228",
        tier="basic",
        max_results=10,
    )

    print(f"\n{len(residents)} people associated with the address\n")
    for p in residents:
        print(f"{p.get('name', '?')}  (age {p.get('age', '?')})")
        print(f"  phone: {client.best_phone(p) or 'n/a'}")

    # Keep only those with a reachable phone number
    reachable = client.filter_with_phone(residents)
    print(f"\n{len(reachable)} of them have a phone number on file")


if __name__ == "__main__":
    main()
