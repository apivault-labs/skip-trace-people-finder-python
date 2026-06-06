"""
Skip Trace — Python SDK

Official Python client for the apivault_labs/skip-trace-people-finder
Apify actor. Locate hard-to-find people in the US by name, address, or
phone and get back contact and profile data.

Tiers:
- basic  ($7 / 1000 results)  — name, age, current address, phones,
  public profile link
- premium ($15 / 1000 results) — everything in basic plus phone line
  types, full address history, emails, relatives, aliases, work/education
  hints, net-worth estimate, and the record's last-updated date

Features handled server-side on Apify:
- Search by name, address, or phone (bulk arrays supported)
- Automatic residential-proxy fallback when datacenter IPs are blocked
- Parallel lookups with retry on transient anti-bot responses
- No API key for the underlying source required

> Lawful B2B use only. Do not use this data for decisions covered by the
> FCRA (credit, employment, insurance, housing, or tenant screening).

Quick start:

    from skip_trace import SkipTraceClient

    client = SkipTraceClient(api_token="apify_api_xxxxxx")

    # By name (optionally narrow with "; City, ST ZIP")
    people = client.search_by_name("James E Whitsitt", tier="basic")
    for p in people:
        print(p.get("name"), p.get("age"), p.get("currentAddress"))

    # Reverse phone lookup
    owners = client.search_by_phone("(214) 321-5304")

    # Who lives at an address
    residents = client.search_by_address("2551 Pinebluff Dr; Dallas, TX 75228")

See https://github.com/apivault-labs/skip-trace-people-finder-python
for full docs.
"""

from .client import SkipTraceClient
from .exceptions import (
    ActorRunError,
    ActorTimeoutError,
    AuthenticationError,
    SkipTraceError,
)

__version__ = "0.1.0"
__all__ = [
    "SkipTraceClient",
    "SkipTraceError",
    "AuthenticationError",
    "ActorRunError",
    "ActorTimeoutError",
]
