"""
Quickstart: look up a person by name and print the matches.

    pip install -r requirements.txt
    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/quickstart.py
"""

from skip_trace import SkipTraceClient


def main() -> None:
    client = SkipTraceClient()  # picks up APIFY_API_TOKEN from env

    people = client.search_by_name(
        "James E Whitsitt",
        tier="basic",
        max_results=5,
    )

    print(f"\nFound {len(people)} matches\n")
    for p in people:
        print(f"{p.get('name', '?')}  (age {p.get('age', '?')})")
        print(f"  address: {p.get('currentAddress') or p.get('address', 'n/a')}")
        print(f"  phone:   {client.best_phone(p) or 'n/a'}")
        print(f"  profile: {p.get('profileUrl', 'n/a')}")
        print()


if __name__ == "__main__":
    main()
