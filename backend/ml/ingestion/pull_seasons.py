"""Pull raw historical F1 data (race schedule, race results, qualifying
results) for a range of seasons from Jolpica-F1, caching every response to
disk. Safe to re-run: cached responses are reused instantly on subsequent
calls, and a rerun only hits the network for genuinely new data (e.g. a
season's most recent race).

Usage:
    python -m ml.ingestion.pull_seasons --start 2015 --end 2026
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from app.core.config import get_settings
from ml.ingestion.jolpica_client import JolpicaClient

logger = logging.getLogger(__name__)


def pull_season(client: JolpicaClient, season: int) -> dict:
    logger.info("Pulling season %d ...", season)
    schedule = client.get_season_races(season)
    results = client.get_season_results(season)
    qualifying = client.get_season_qualifying(season)
    return {
        "season": season,
        "races_scheduled": len(schedule),
        "races_with_results": len(results),
        "races_with_qualifying": len(qualifying),
    }


def pull_seasons(start: int, end: int, cache_dir: str | Path) -> list[dict]:
    settings = get_settings()
    client = JolpicaClient(base_url=settings.jolpica_base_url, cache_dir=cache_dir)
    summary = [pull_season(client, season) for season in range(start, end + 1)]

    manifest_path = Path(cache_dir) / "manifest.json"
    manifest_path.write_text(json.dumps({"start": start, "end": end, "seasons": summary}, indent=2))
    return summary


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Pull raw F1 season data from Jolpica-F1.")
    parser.add_argument("--start", type=int, default=2015)
    parser.add_argument("--end", type=int, default=2026)
    parser.add_argument("--cache-dir", type=str, default=None)
    args = parser.parse_args()

    settings = get_settings()
    cache_dir = args.cache_dir or settings.data_cache_dir
    summary = pull_seasons(args.start, args.end, cache_dir)
    for row in summary:
        logger.info(
            "Season %(season)d: %(races_with_results)d/%(races_scheduled)d races with results, "
            "%(races_with_qualifying)d with qualifying",
            row,
        )


if __name__ == "__main__":
    main()
