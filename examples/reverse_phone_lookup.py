"""
Reverse phone lookup: identify the owner(s) of US phone numbers.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/reverse_phone_lookup.py
"""

from skip_trace import SkipTraceClient


def main() -> None:
    client = SkipTraceClient()

    phones = [
        "(214) 321-5304",
        "(212) 555-0148",
    ]

    print(f"Estimated cost: ${client.estimate_cost(len(phones) * 5, 'basic')}")

    owners = client.search_by_phone(*phones, tier="basic", max_results=5)

    print(f"\n{len(owners)} records\n")
    for p in owners:
        print(f"{p.get('name', '?')} — {p.get('currentAddress', 'n/a')}")
        print(f"  phone: {client.best_phone(p)}")


if __name__ == "__main__":
    main()
