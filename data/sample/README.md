# Sample data

A small, committed slice of the pipeline's cleaned output (the 2024 season
only — 24 races, 479 driver-race results, 479 qualifying rows) so the
repository is inspectable and partially reproducible without hitting the
live Jolpica-F1 API.

These are the same normalized tables `scripts/build_processed_data.py`
produces in `data/processed/` (which is gitignored, since it's the full
2015-2026 history and easily regenerated). To regenerate the full dataset:

```bash
cd backend
./scripts/run_pipeline.sh        # ingest -> process -> features -> train -> seed
```

| File | Contents |
|---|---|
| `races_2024.csv` | 2024 season schedule |
| `race_results_2024.csv` | Race classification for every driver, every 2024 race |
| `qualifying_results_2024.csv` | Qualifying classification and session times |
| `drivers_2024.csv` | Driver reference data for everyone who raced in 2024 |
| `constructors_2024.csv` | Constructor reference data for 2024 |
| `circuits_2024.csv` | Circuit reference data for every 2024 venue |
