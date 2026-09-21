"""Thin synchronous client for the hosted Skip Trace Apify Actor."""

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
PRICE_PER_MATCH_USD = 0.0065
TERMINAL_FAIL = {"FAILED", "TIMED-OUT", "ABORTED"}


class SkipTraceClient:
    """Run authorized name, address, phone and email lookups on Apify."""

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
                "An Apify API token is required. Pass api_token= or set "
                "APIFY_API_TOKEN."
            )
        self._timeout = int(timeout)
        self._poll_interval = float(poll_interval)
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "skip-trace-python/0.2.0",
        })
        self._last_run: dict[str, Any] | None = None

    def search(
        self,
        *,
        names: Sequence[str] = (),
        addresses: Sequence[str] = (),
        phones: Sequence[str] = (),
        emails: Sequence[str] = (),
        max_results: int = 3,
        output_preset: str = "contacts",
        verify_emails: bool = True,
        coverage: str = "auto",
        actor_timeout_secs: int = 600,
    ) -> list[dict[str, Any]]:
        """Run one or more independent OR lookups and return Dataset rows."""
        values = {
            "name": self._clean(names),
            "street_citystatezip": self._clean(addresses),
            "phone_number": self._clean(phones),
            "email": self._clean(emails),
        }
        if not any(values.values()):
            raise ValueError("Provide at least one name, address, phone or email")
        if output_preset not in {"contacts", "flat", "full"}:
            raise ValueError("output_preset must be contacts, flat or full")
        if coverage not in {"auto", "merge", "default"}:
            raise ValueError("coverage must be auto, merge or default")

        payload: dict[str, Any] = {
            "workflow": "combined" if sum(bool(v) for v in values.values()) > 1 else "auto",
            "max_results": max(1, min(1000, int(max_results))),
            "outputPreset": output_preset,
            "verifyEmails": bool(verify_emails),
            "source": coverage,
            "useDemoOnEmpty": False,
        }
        payload.update({key: value for key, value in values.items() if value})
        return self._execute(payload, actor_timeout_secs)

    def search_by_name(self, *names: str, **kwargs: Any) -> list[dict[str, Any]]:
        return self.search(names=names, **kwargs)

    def search_by_address(self, *addresses: str, **kwargs: Any) -> list[dict[str, Any]]:
        return self.search(addresses=addresses, **kwargs)

    def search_by_phone(self, *phones: str, **kwargs: Any) -> list[dict[str, Any]]:
        return self.search(phones=phones, **kwargs)

    def search_by_email(self, *emails: str, **kwargs: Any) -> list[dict[str, Any]]:
        return self.search(emails=emails, **kwargs)

    def last_summary(self) -> dict[str, Any]:
        return self._record("SUMMARY", {})

    def last_errors(self) -> list[dict[str, Any]]:
        return self._record("ERRORS", [])

    @staticmethod
    def filter_matches(rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
        return [row for row in rows if row.get("success") is True]

    @staticmethod
    def filter_with_phone(rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
        return [row for row in rows if row.get("phones") or row.get("bestPhone")]

    @staticmethod
    def filter_with_email(rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
        return [row for row in rows if row.get("emails") or row.get("bestEmail")]

    @staticmethod
    def best_phone(person: dict[str, Any]) -> str | None:
        if person.get("bestPhone"):
            return str(person["bestPhone"])
        phones = person.get("phones") or []
        return str(phones[0]) if isinstance(phones, list) and phones else None

    @staticmethod
    def best_email(person: dict[str, Any]) -> str | None:
        if person.get("bestEmail"):
            return str(person["bestEmail"])
        emails = person.get("emails") or []
        return str(emails[0]) if isinstance(emails, list) and emails else None

    @staticmethod
    def estimate_cost(expected_matches: int) -> float:
        return round(max(0, int(expected_matches)) * PRICE_PER_MATCH_USD, 4)

    @staticmethod
    def _clean(values: Sequence[str]) -> list[str]:
        return [value.strip() for value in values if value and value.strip()]

    def _execute(self, payload: dict[str, Any], actor_timeout_secs: int) -> list[dict[str, Any]]:
        run = self._start_run(payload, actor_timeout_secs)
        run = self._wait_for_run(run["id"])
        self._last_run = run
        return self._fetch_dataset(run["defaultDatasetId"])

    def _start_run(self, payload: dict[str, Any], actor_timeout_secs: int) -> dict[str, Any]:
        try:
            response = self._session.post(
                f"{self._base_url}/acts/{ACTOR_ID}/runs",
                params={"timeout": int(actor_timeout_secs)},
                json=payload,
                timeout=30,
            )
        except requests.RequestException as exc:
            raise SkipTraceError("Could not start the Apify run") from exc
        if response.status_code == 401:
            raise AuthenticationError("Apify rejected the API token")
        if response.status_code >= 400:
            raise ActorRunError(f"Apify returned HTTP {response.status_code} when starting the run")
        run = response.json().get("data") or {}
        if not run.get("id"):
            raise ActorRunError("Apify did not return a run ID")
        return run

    def _wait_for_run(self, run_id: str) -> dict[str, Any]:
        deadline = time.time() + self._timeout
        while True:
            try:
                response = self._session.get(f"{self._base_url}/actor-runs/{run_id}", timeout=30)
            except requests.RequestException as exc:
                raise SkipTraceError("Could not read the Apify run status") from exc
            if response.status_code >= 400:
                raise ActorRunError(f"Apify returned HTTP {response.status_code} while polling")
            run = response.json().get("data") or {}
            status = run.get("status")
            if status == "SUCCEEDED":
                return run
            if status in TERMINAL_FAIL:
                raise ActorRunError(f"Actor run ended with status {status}")
            if time.time() >= deadline:
                raise ActorTimeoutError(f"Actor run did not finish within {self._timeout} seconds")
            time.sleep(self._poll_interval)

    def _fetch_dataset(self, dataset_id: str) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        offset = 0
        while True:
            response = self._session.get(
                f"{self._base_url}/datasets/{dataset_id}/items",
                params={"clean": "true", "limit": 1000, "offset": offset},
                timeout=120,
            )
            if response.status_code >= 400:
                raise ActorRunError(f"Apify returned HTTP {response.status_code} while reading results")
            page = response.json()
            if not isinstance(page, list):
                raise ActorRunError("Apify returned an unexpected Dataset response")
            rows.extend(page)
            if len(page) < 1000:
                return rows
            offset += len(page)

    def _record(self, key: str, default: Any) -> Any:
        if not self._last_run:
            return default
        store_id = self._last_run.get("defaultKeyValueStoreId")
        if not store_id:
            return default
        response = self._session.get(
            f"{self._base_url}/key-value-stores/{store_id}/records/{key}",
            timeout=30,
        )
        if response.status_code == 404:
            return default
        if response.status_code >= 400:
            raise ActorRunError(f"Apify returned HTTP {response.status_code} while reading {key}")
        return response.json()
