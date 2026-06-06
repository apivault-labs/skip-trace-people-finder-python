# Skip Trace — People & Contact Finder (Python SDK)

Locate hard-to-find people in the **US** by **name, address, or phone**. Get back full names, age, current and previous addresses, phone numbers, emails, relatives, aliases, and a public profile link.

Pay-as-you-go, no monthly subscription. The people-search logic runs server-side on [Apify](https://apify.com); this SDK is a thin client you drive with your own Apify API token.

> **Lawful B2B use only.** Do not use this data for decisions covered by the FCRA (credit, employment, insurance, housing, or tenant screening).

Built by **[apivault_labs](https://apify.com/apivault_labs)** — see [all our actors](https://apify.com/apivault_labs).

## Install

```bash
pip install git+https://github.com/apivault-labs/skip-trace-people-finder-python.git
```

## Quick start

```python
from skip_trace import SkipTraceClient

client = SkipTraceClient(api_token="apify_api_xxxxxx")  # or set APIFY_API_TOKEN

# By name (optionally narrow with "; City, ST ZIP")
people = client.search_by_name("James E Whitsitt", tier="basic")
for p in people:
    print(p.get("name"), p.get("age"), p.get("currentAddress"))

# Reverse phone lookup
owners = client.search_by_phone("(214) 321-5304")

# Who lives at an address
residents = client.search_by_address("2551 Pinebluff Dr; Dallas, TX 75228")
```

## Getting an Apify token

1. Create a free account at [apify.com](https://apify.com)
2. Go to **Apify Console → Settings → Integrations** and copy your **API token**
3. Pass it as `api_token=` or set the `APIFY_API_TOKEN` environment variable

A free Apify account includes monthly usage credits, so you can try it without a card.

## Pricing

| Tier | Price | Returns |
|------|-------|---------|
| `basic` | **$7 / 1,000** | name, age, current address, phones, profile link |
| `premium` | **$15 / 1,000** | everything in Basic + phone line types, full address history, emails, relatives, aliases, work/education hints, net-worth estimate |

You only pay for the people actually returned. Estimate before you run:

```python
client.estimate_cost(500, tier="basic")    # -> 3.5
client.estimate_cost(500, tier="premium")  # -> 7.5
```

## API

### `search(*, names=(), addresses=(), phones=(), tier="basic", max_results=5, ...)`
Run a lookup with any combination of inputs. Returns a list of people records.

Convenience wrappers:
- `search_by_name(*names, tier=..., max_results=...)`
- `search_by_address(*addresses, ...)`
- `search_by_phone(*phones, ...)`

Extra options (passed through to all of the above):
- `use_residential` (default `True`) — fall back to residential IPs when the source blocks datacenter IPs
- `max_concurrency` (default `4`) — parallel lookups
- `max_retries` (default `2`) — retries on transient anti-bot responses
- `timeout_per_request` (default `25`) — seconds per page fetch

### Filters (client-side, free)
- `filter_with_phone(people)`
- `filter_with_email(people)` — premium tier
- `filter_by_min_age(people, min_age)`
- `filter_by_state(people, "TX", "OK")`

### Helpers
- `best_phone(person)` — first available phone number
- `estimate_cost(expected_results, tier)`

## Example output (basic)

```json
{
  "name": "James E Whitsitt",
  "age": 58,
  "currentAddress": "2551 Pinebluff Dr, Dallas, TX 75228",
  "phones": ["(214) 321-5304"],
  "profileUrl": "https://radaris.com/p/James/Whitsitt/..."
}
```

## Examples

See the [`examples/`](examples) folder:

- `quickstart.py` — search by name
- `reverse_phone_lookup.py` — identify phone owners
- `address_residents.py` — people at an address (real-estate outreach)
- `premium_deep_profile.py` — relatives, history, emails, net worth
- `bulk_crm_export.py` — bulk lookup → CSV for HubSpot/Pipedrive/Salesforce

## Use cases

- **Real-estate / investor outreach** — turn a property address into owner contacts
- **Debt collection & skip tracing** — relocate people who moved
- **B2B lead enrichment** — append phone/email to a name in your CRM
- **Process serving / investigations** — confirm a current address

## Resources

- [Skip Trace actor on Apify](https://apify.com/apivault_labs/skip-trace-people-finder)
- [All actors by apivault_labs](https://apify.com/apivault_labs)
- Prefer no-code? Use the [n8n community node](https://www.npmjs.com/package/n8n-nodes-apivault-skip-trace)

## License

[MIT](LICENSE)

## Keywords

`skip-trace` `skip-tracing` `people-search` `people-finder` `reverse-phone-lookup` `address-lookup` `contact-finder` `lead-generation` `real-estate-leads` `debt-collection` `whitepages-alternative` `spokeo-alternative` `beenverified-alternative` `truepeoplesearch-alternative` `apify` `python-sdk`
