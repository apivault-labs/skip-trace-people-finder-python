"""
SkipTraceClient — synchronous wrapper around the Apify
``apivault_labs/skip-trace-people-finder`` actor.

The actor handles all heavy work on Apify infrastructure:
  - Search by name, address, or phone against a public people-search source
  - Automatic residential-proxy fallback when datacenter IPs are blocked
  - Two tiers: basic (core contact data) and premium (deep profile:
    phone line types, full address history, emails, relatives, aliases,
    work/education hints, net-worth estimate, record last-updated date)
  - Parallel lookups with retry on transient anti-bot responses

This client forwards inputs, polls until the run finishes, then
downloads the dataset and exposes small helpers for lead-gen and
skip-tracing workflows.

Pricing: basic $7 / 1000 results, premium $15 / 1000 results.

> Lawful B2B use only. Do not use this data for decisions covered by the
> FCRA (credit, employment, insurance, housing, or tenant screening).

Quick start:

    from skip_trace import SkipTraceClient

    client = SkipTraceClient(api_token="apify_api_xxxxxx")

    people = client.search_by_name(
        "James E Whitsitt",
        tier="basic",
    )
    for p in people:
        print(p.get("name"), p.get("age"), p.get("currentAddress"))
"""

from __future__ import annotations

import os
import time
from typing import Any, Sequence

import requests

from .exceptions import (
    ActorRunError,
    ActorTimeoutError,
    AuthenticationError,
    SkipTraceError,
)


ACTOR_ID = "apivault_labs~skip-trace-people-finder"
APIFY_API_BASE = "https://api.apify.com/v2"

TERMINAL_OK = {"SUCCEEDED"}
TERMINAL_FAIL = {"FAILED", "TIMED-OUT", "ABORTED"}

VALID_TIERS = ("basic", "premium")
PRICE_PER_RESULT_USD = {"basic": 0.007, "premium": 0.015}


class SkipTraceClient:
    """Synchronous client for the Skip Trace People & Contact Finder actor.

    Parameters
    ----------
    api_token : str, optional
        Apify Personal API token. Falls back to ``APIFY_API_TOKEN``.
    timeout : int, optional
        Maximum seconds to wait for an actor run. Default 900 (15 min).
    poll_interval : float, optional
        Seconds between status polls. Default 3.
    base_url : str, optional
        Override the Apify API base URL.
    """

    def __init__(
        self,
        api_token: str | None = None,
        timeout: int = 900,
        poll_interval: float = 3.0,
        base_url: str = APIFY_API_BASE,
    ):
        token = api_token or os.environ.get("APIFY_API_TOKEN")
        if not token:
            raise AuthenticationError(
                "Apify API token is required. Pass api_token='apify_api_...' "
                "or set the APIFY_API_TOKEN environment variable. "
                "Get a token at https://console.apify.com/account/integrations"
            )
        self._token = token
        self._timeout = int(timeout)
        self._poll_interval = float(poll_interval)
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
            "User-Agent": "skip-trace-python/0.1.0",
        })
        self._last_run_id: str | None = None
        self._last_dataset_id: str | None = None

    # ------------------------------------------------------------------ public

    def search(
        self,
        *,
        names: Sequence[str] = (),
        addresses: Sequence[str] = (),
        phones: Sequence[str] = (),
        tier: str = "basic",
        max_results: int = 5,
        use_residential: bool = True,
        max_concurrency: int = 4,
        max_retries: int = 2,
        timeout_per_request: int = 25,
        actor_timeout_secs: int = 600,
    ) -> list[dict[str, Any]]:
        """Run a skip-trace lookup and return matched people.

        Provide one or more of ``names``, ``addresses``, ``phones``.

        Parameters
        ----------
        names : Sequence[str], optional
            Full names. Optionally append a location after a semicolon to
            narrow results, e.g. ``"Amalia Castillo; Dallas, TX 75228"``.
        addresses : Sequence[str], optional
            Street addresses with city, state, ZIP. Finds people
            associated with the address.
        phones : Sequence[str], optional
            US phone numbers for reverse lookup.
        tier : str, optional
            ``"basic"`` ($7/1K — name, age, current address, phones,
            profile link) or ``"premium"`` ($15/1K — deep profile:
            line types, full address history, emails, relatives, aliases,
            work/education hints, net-worth estimate). Default ``"basic"``.
        max_results : int, optional
            How many matched people to return per input value (1-20).
        use_residential : bool, optional
            Fall back to residential IPs when the source blocks datacenter
            IPs (recommended; costs a fraction of a cent per run).
        max_concurrency : int, optional
            How many lookups to run in parallel (1-8).
        max_retries : int, optional
            Retry attempts on transient anti-bot responses (0-3).
        timeout_per_request : int, optional
            Max wait per page fetch in seconds (10-45).

        Returns
        -------
        list[dict]
            Matched people records.
        """
        clean_names = [n.strip() for n in names if n and n.strip()]
        clean_addresses = [a.strip() for a in addresses if a and a.strip()]
        clean_phones = [p.strip() for p in phones if p and p.strip()]

        if not (clean_names or clean_addresses or clean_phones):
            raise ValueError(
                "Provide at least one of names=, addresses=, or phones="
            )

        if tier not in VALID_TIERS:
            raise ValueError(
                f"tier must be one of {VALID_TIERS}, got {tier!r}"
            )

        payload: dict[str, Any] = {
            "tier": tier,
            "max_results": max(1, min(20, int(max_results))),
            "useResidential": bool(use_residential),
            "maxConcurrency": max(1, min(8, int(max_concurrency))),
            "maxRetries": max(0, min(3, int(max_retries))),
            "timeout": max(10, min(45, int(timeout_per_request))),
        }
        if clean_names:
            payload["name"] = clean_names
        if clean_addresses:
            payload["street_citystatezip"] = clean_addresses
        if clean_phones:
            payload["phone_number"] = clean_phones

        run_id = self._start_run(payload, actor_timeout_secs=actor_timeout_secs)
        run = self._wait_for_run(run_id)
        self._last_run_id = run_id
        self._last_dataset_id = run.get("defaultDatasetId")
        return self._fetch_dataset(self._last_dataset_id)

    # convenience single-field wrappers ------------------------------------

    def search_by_name(
        self,
        *names: str,
        tier: str = "basic",
        max_results: int = 5,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Look up one or more people by full name.

        Append a location after a semicolon to narrow results, e.g.
        ``search_by_name("Amalia Castillo; Dallas, TX 75228")``.
        """
        return self.search(
            names=names, tier=tier, max_results=max_results, **kwargs
        )

    def search_by_address(
        self,
        *addresses: str,
        tier: str = "basic",
        max_results: int = 5,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Find people associated with one or more street addresses."""
        return self.search(
            addresses=addresses, tier=tier, max_results=max_results, **kwargs
        )

    def search_by_phone(
        self,
        *phones: str,
        tier: str = "basic",
        max_results: int = 5,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Reverse-lookup one or more US phone numbers."""
        return self.search(
            phones=phones, tier=tier, max_results=max_results, **kwargs
        )

    # ------------------------------------------------------------------ filters

    def filter_with_phone(
        self,
        people: Sequence[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Keep only records that have at least one phone number."""
        return [p for p in people if p.get("phones") or p.get("phone")]

    def filter_with_email(
        self,
        people: Sequence[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Keep only records that have at least one email (premium tier)."""
        return [p for p in people if p.get("emails") or p.get("email")]

    def filter_by_min_age(
        self,
        people: Sequence[dict[str, Any]],
        min_age: int,
    ) -> list[dict[str, Any]]:
        """Keep only records whose ``age`` is at least ``min_age``."""
        out: list[dict[str, Any]] = []
        for p in people:
            try:
                if int(p.get("age") or 0) >= min_age:
                    out.append(p)
            except (TypeError, ValueError):
                continue
        return out

    def filter_by_state(
        self,
        people: Sequence[dict[str, Any]],
        *states: str,
    ) -> list[dict[str, Any]]:
        """Keep records whose current address contains one of the given
        US state codes (case-insensitive 2-letter match)."""
        wanted = {s.upper() for s in states if s}
        if not wanted:
            return list(people)
        out: list[dict[str, Any]] = []
        for p in people:
            addr = (p.get("currentAddress") or p.get("address") or "").upper()
            if any(f" {st} " in f" {addr} " or addr.endswith(f" {st}")
                   or f", {st}" in addr for st in wanted):
                out.append(p)
        return out

    # ------------------------------------------------------------------ helpers

    def best_phone(self, person: dict[str, Any]) -> str | None:
        """Return the first available phone number for a person, if any."""
        phones = person.get("phones")
        if isinstance(phones, list) and phones:
            first = phones[0]
            if isinstance(first, dict):
                return first.get("number") or first.get("phone")
            return str(first)
        return person.get("phone")

    def estimate_cost(self, expected_results: int, tier: str = "basic") -> float:
        """Estimate USD cost for ``expected_results`` results at the given
        tier ($7/1K basic, $15/1K premium).

        Use this *before* calling :meth:`search` to budget your run.
        """
        if tier not in VALID_TIERS:
            raise ValueError(f"tier must be one of {VALID_TIERS}")
        return round(expected_results * PRICE_PER_RESULT_USD[tier], 4)

    # ------------------------------------------------------------------ private

    def _start_run(
        self,
        payload: dict[str, Any],
        actor_timeout_secs: int,
    ) -> str:
        url = f"{self._base_url}/acts/{ACTOR_ID}/runs"
        params = {"timeout": int(actor_timeout_secs)}
        try:
            r = self._session.post(
                url, params=params, json=payload, timeout=30
            )
        except requests.RequestException as e:
            raise SkipTraceError(f"Failed to start actor run: {e}") from e
        if r.status_code == 401:
            raise AuthenticationError(
                "Apify rejected the API token. Generate a new one at "
                "https://console.apify.com/account/integrations"
            )
        if r.status_code >= 400:
            raise ActorRunError(
                f"Apify returned HTTP {r.status_code} when starting run: "
                f"{r.text[:300]}"
            )
        data = r.json().get("data") or {}
        run_id = data.get("id")
        if not run_id:
            raise ActorRunError(
                f"Apify response missing run id: {r.text[:300]}"
            )
        return run_id

    def _wait_for_run(self, run_id: str) -> dict[str, Any]:
        url = f"{self._base_url}/actor-runs/{run_id}"
        deadline = time.time() + self._timeout
        while True:
            try:
                r = self._session.get(url, timeout=30)
            except requests.RequestException as e:
                raise SkipTraceError(f"Failed to poll run status: {e}") from e
            if r.status_code >= 400:
                raise ActorRunError(
                    f"Apify returned HTTP {r.status_code} when polling: "
                    f"{r.text[:300]}"
                )
            run = r.json().get("data") or {}
            status = run.get("status")
            if status in TERMINAL_OK:
                return run
            if status in TERMINAL_FAIL:
                raise ActorRunError(
                    f"Actor run {run_id} ended with status={status}: "
                    f"{run.get('statusMessage') or '(no message)'}"
                )
            if time.time() > deadline:
                raise ActorTimeoutError(
                    f"Actor run {run_id} did not finish within "
                    f"{self._timeout}s (last status={status}). Increase "
                    "`timeout=` or fetch the dataset manually."
                )
            time.sleep(self._poll_interval)

    def _fetch_dataset(self, dataset_id: str) -> list[dict[str, Any]]:
        url = f"{self._base_url}/datasets/{dataset_id}/items"
        params = {"clean": "true", "format": "json"}
        try:
            r = self._session.get(url, params=params, timeout=120)
        except requests.RequestException as e:
            raise SkipTraceError(f"Failed to download dataset: {e}") from e
        if r.status_code >= 400:
            raise ActorRunError(
                f"Apify returned HTTP {r.status_code} when fetching "
                f"dataset: {r.text[:300]}"
            )
        try:
            data = r.json()
        except ValueError as e:
            raise ActorRunError(f"Apify dataset is not valid JSON: {e}") from e
        if not isinstance(data, list):
            raise ActorRunError(
                f"Unexpected dataset payload: {type(data).__name__}"
            )
        return data
