"""RAW DATA -> CLEANED DATA. Parses cached Jolpica JSON into normalized
parquet tables under data/processed/.

Usage:
    python -m scripts.build_processed_data --start 2015 --end 2026
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from app.core.config import get_settings
from ml.ingestion.jolpica_client import JolpicaClient
from ml.preprocessing.parse_raw import build_processed_tables

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=2015)
    parser.add_argument("--end", type=int, default=2026)
    parser.add_argument("--out-dir", type=str, default="../data/processed")
    args = parser.parse_args()

    settings = get_settings()
    client = JolpicaClient(base_url=settings.jolpica_base_url, cache_dir=settings.data_cache_dir)

    seasons = list(range(args.start, args.end + 1))
    tables = build_processed_tables(seasons, client)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, df in tables.items():
        path = out_dir / f"{name}.parquet"
        df.to_parquet(path, index=False)
        logger.info("Wrote %s (%d rows)", path, len(df))


if __name__ == "__main__":
    main()
