"""HTTP client for the Jolpica-F1 API (an Ergast-compatible historical F1 data
source: https://api.jolpi.ca/ergast/f1).

Every response is cached to disk as JSON. On a network failure, the client
falls back to the cached copy if one exists, so the rest of the pipeline and
the running application keep working without the external API.
"""

from __future__ import annotations

import json
import logging
import re
import time
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

DEFAULT_PAGE_LIMIT = 100
REQUEST_TIMEOUT_SECONDS = 20.0
RETRY_ATTEMPTS = 5
RETRY_BACKOFF_SECONDS = 2.0
INTER_REQUEST_DELAY_SECONDS = 0.4
_UNSAFE_CHARS = re.compile(r"[^a-zA-Z0-9._-]+")


class JolpicaClientError(RuntimeError):
    """Raised when a request fails and no cached fallback is available."""


class JolpicaClient:
    def __init__(self, base_url: str, cache_dir: str | Path) -> None:
        self.base_url = base_url.rstrip("/")
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_path(self, endpoint: str) -> Path:
        safe_name = _UNSAFE_CHARS.sub("_", endpoint.strip("/")) + ".json"
        return self.cache_dir / safe_name

    def _get_json(self, endpoint: str, *, use_cache_on_failure: bool = True, force_refresh: bool = False) -> dict:
        cache_path = self._cache_path(endpoint)
        if not force_refresh and cache_path.exists():
            return json.loads(cache_path.read_text())

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        last_error: Exception | None = None
        for attempt in range(1, RETRY_ATTEMPTS + 1):
            try:
                response = httpx.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
                if response.status_code == 429:
                    retry_after = float(response.headers.get("retry-after", RETRY_BACKOFF_SECONDS * attempt))
                    logger.warning("Rate limited (attempt %d/%d), waiting %.1fs", attempt, RETRY_ATTEMPTS, retry_after)
                    time.sleep(retry_after)
                    continue
                response.raise_for_status()
                data = response.json()
                cache_path.write_text(json.dumps(data))
                time.sleep(INTER_REQUEST_DELAY_SECONDS)
                return data
            except (httpx.HTTPError, json.JSONDecodeError) as exc:
                last_error = exc
                logger.warning("Jolpica request failed (attempt %d/%d): %s", attempt, RETRY_ATTEMPTS, exc)
                if attempt < RETRY_ATTEMPTS:
                    time.sleep(RETRY_BACKOFF_SECONDS * attempt)

        if use_cache_on_failure and cache_path.exists():
            logger.warning("Falling back to cached response for %s", endpoint)
            return json.loads(cache_path.read_text())

        raise JolpicaClientError(f"Failed to fetch {url} and no cache available") from last_error

    def _get_all_pages(self, endpoint_template: str, *, force_refresh: bool = False) -> list[dict]:
        """Follow the Ergast `limit`/`offset` pagination scheme.

        Important: the `limit`/`offset`/`total` in these endpoints paginate over
        *result rows* (e.g. one row per driver-race), not over races. A race
        with ~20 results can therefore be split across two pages, with each
        page holding a disjoint subset of that race's `Results` (or
        `QualifyingResults`). Pages are merged here by `round` so a race's
        results are never silently truncated to whichever page happened to
        hold its first few classified drivers.
        """
        offset = 0
        races_by_round: dict[str, dict] = {}
        round_order: list[str] = []
        while True:
            sep = "&" if "?" in endpoint_template else "?"
            endpoint = f"{endpoint_template}{sep}limit={DEFAULT_PAGE_LIMIT}&offset={offset}"
            data = self._get_json(endpoint, force_refresh=force_refresh)
            table = data["MRData"].get("RaceTable") or data["MRData"].get("StandingsTable")
            races = table.get("Races") or table.get("StandingsLists") or []

            for race in races:
                round_ = race["round"]
                list_key = "Results" if "Results" in race else "QualifyingResults" if "QualifyingResults" in race else None
                if round_ not in races_by_round:
                    races_by_round[round_] = race
                    round_order.append(round_)
                elif list_key is not None:
                    races_by_round[round_][list_key].extend(race[list_key])

            total = int(data["MRData"]["total"])
            offset += DEFAULT_PAGE_LIMIT
            if offset >= total or not races:
                break
        return [races_by_round[r] for r in round_order]

    def get_season_results(self, season: int, *, force_refresh: bool = False) -> list[dict]:
        """All race results for a season, one entry per race with nested Results."""
        return self._get_all_pages(f"{season}/results.json", force_refresh=force_refresh)

    def get_season_qualifying(self, season: int, *, force_refresh: bool = False) -> list[dict]:
        """All qualifying results for a season, one entry per race with nested QualifyingResults."""
        return self._get_all_pages(f"{season}/qualifying.json", force_refresh=force_refresh)

    def get_season_races(self, season: int, *, force_refresh: bool = False) -> list[dict]:
        """Race schedule (name, circuit, date) for a season, no results."""
        return self._get_all_pages(f"{season}.json", force_refresh=force_refresh)
