# Changelog

## 0.2.0

- Synchronized the client with the current name, address, phone and email workflows.
- Added Contacts, Flat and Full output presets plus SUMMARY/ERRORS helpers.
- Replaced the retired two-tier pricing copy with the current `$6.50/1K` matched-record model.
- Added a review-first contact-enrichment guide and removed outdated result claims.

## 0.1.0

- Initial release.
- `SkipTraceClient` with `search`, `search_by_name`, `search_by_address`,
  `search_by_phone`.
- Basic ($7/1K) and Premium ($15/1K) tiers.
- Filters: `filter_with_phone`, `filter_with_email`, `filter_by_min_age`,
  `filter_by_state`.
- Helpers: `best_phone`, `estimate_cost`.
- 5 examples: quickstart, reverse_phone_lookup, address_residents,
  premium_deep_profile, bulk_crm_export.
