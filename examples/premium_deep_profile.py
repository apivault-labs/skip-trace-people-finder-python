"""
Premium deep profile: get relatives, address history, emails, aliases,
phone line types, and a net-worth estimate.

Premium tier is $15/1K (vs $7/1K basic). Use it when you need a full
dossier per person, not just core contact data.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/premium_deep_profile.py
"""

from skip_trace import SkipTraceClient


def main() -> None:
    client = SkipTraceClient()

    people = client.search_by_name(
        "Amalia Castillo; Dallas, TX 75228",
        tier="premium",
        max_results=3,
    )

    for p in people:
        print("=" * 60)
        print(f"{p.get('name', '?')}  (age {p.get('age', '?')})")
        print(f"  current:    {p.get('currentAddress', 'n/a')}")
        print(f"  history:    {p.get('addressHistory') or []}")
        print(f"  emails:     {p.get('emails') or []}")
        print(f"  relatives:  {p.get('relatives') or []}")
        print(f"  aliases:    {p.get('aliases') or []}")
        print(f"  net worth:  {p.get('netWorthEstimate', 'n/a')}")
        print(f"  updated:    {p.get('lastUpdated', 'n/a')}")


if __name__ == "__main__":
    main()
