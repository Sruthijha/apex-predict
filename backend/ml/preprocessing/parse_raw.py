"""Parse cached raw Jolpica-F1 JSON responses into clean, normalized pandas
tables: circuits, drivers, constructors, races, race_results, qualifying_results.

This is the "RAW DATA -> CLEANED DATA" stage of the pipeline. No feature
engineering happens here — just parsing, type coercion, and de-duplication.
"""

from __future__ import annotations

import re

import pandas as pd

from ml.ingestion.jolpica_client import JolpicaClient

_LAP_TIME_RE = re.compile(r"^(?:(\d+):)?(\d+(?:\.\d+)?)$")

# "Lapped" is Jolpica's newer (2023+) label for what older seasons report as
# "+N Lap(s)" — both mean classified/finished, just multiple laps down.
FINISHED_STATUSES = {"Finished", "Lapped"}


def parse_lap_time_to_seconds(value: str | None) -> float | None:
    """Convert an Ergast-style lap/qualifying time ('1:31.856' or '31.856') to seconds."""
    if not value:
        return None
    match = _LAP_TIME_RE.match(value.strip())
    if not match:
        return None
    minutes_str, seconds_str = match.groups()
    seconds = float(seconds_str)
    if minutes_str:
        seconds += int(minutes_str) * 60
    return seconds


def is_finished(status: str) -> bool:
    """A driver is 'finished' if classified as Finished or lapped-but-classified (+N Lap(s))."""
    return status in FINISHED_STATUSES or status.startswith("+")


def parse_season_schedule(races: list[dict]) -> pd.DataFrame:
    rows = []
    for race in races:
        circuit = race["Circuit"]
        location = circuit["Location"]
        rows.append(
            {
                "season": int(race["season"]),
                "round": int(race["round"]),
                "name": race["raceName"],
                "date": race["date"],
                "time": race.get("time"),
                "url": race.get("url"),
                "circuit_id": circuit["circuitId"],
                "circuit_name": circuit["circuitName"],
                "circuit_country": location.get("country"),
                "circuit_locality": location.get("locality"),
                "circuit_lat": float(location["lat"]) if location.get("lat") else None,
                "circuit_long": float(location["long"]) if location.get("long") else None,
                "circuit_url": circuit.get("url"),
            }
        )
    return pd.DataFrame(rows)


def parse_season_results(races: list[dict]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Returns (race_results_df, drivers_df, constructors_df) for one season's results payload."""
    result_rows = []
    driver_rows = {}
    constructor_rows = {}

    for race in races:
        season, round_ = int(race["season"]), int(race["round"])
        for result in race["Results"]:
            driver, constructor = result["Driver"], result["Constructor"]
            driver_rows[driver["driverId"]] = {
                "driver_id": driver["driverId"],
                "code": driver.get("code"),
                "permanent_number": int(driver["permanentNumber"]) if driver.get("permanentNumber") else None,
                "given_name": driver["givenName"],
                "family_name": driver["familyName"],
                "nationality": driver.get("nationality"),
                "date_of_birth": driver.get("dateOfBirth"),
                "url": driver.get("url"),
            }
            constructor_rows[constructor["constructorId"]] = {
                "constructor_id": constructor["constructorId"],
                "name": constructor["name"],
                "nationality": constructor.get("nationality"),
                "url": constructor.get("url"),
            }
            status = result["status"]
            result_rows.append(
                {
                    "season": season,
                    "round": round_,
                    "driver_id": driver["driverId"],
                    "constructor_id": constructor["constructorId"],
                    "grid": int(result["grid"]),
                    "position": int(result["position"]) if result.get("position") else None,
                    "position_text": result.get("positionText"),
                    "points": float(result["points"]),
                    "laps": int(result["laps"]),
                    "status": status,
                    "finished": is_finished(status),
                    "dnf": not is_finished(status),
                }
            )

    results_df = pd.DataFrame(result_rows)
    drivers_df = pd.DataFrame(list(driver_rows.values()))
    constructors_df = pd.DataFrame(list(constructor_rows.values()))
    return results_df, drivers_df, constructors_df


def parse_season_qualifying(races: list[dict]) -> pd.DataFrame:
    rows = []
    for race in races:
        season, round_ = int(race["season"]), int(race["round"])
        for result in race["QualifyingResults"]:
            rows.append(
                {
                    "season": season,
                    "round": round_,
                    "driver_id": result["Driver"]["driverId"],
                    "constructor_id": result["Constructor"]["constructorId"],
                    "position": int(result["position"]),
                    "q1_seconds": parse_lap_time_to_seconds(result.get("Q1")),
                    "q2_seconds": parse_lap_time_to_seconds(result.get("Q2")),
                    "q3_seconds": parse_lap_time_to_seconds(result.get("Q3")),
                }
            )
    return pd.DataFrame(rows)


def build_processed_tables(
    seasons: list[int], client: JolpicaClient
) -> dict[str, pd.DataFrame]:
    """Fetch (from cache) and parse every season, returning deduplicated normalized tables."""
    schedules, all_results, all_qualifying = [], [], []
    all_drivers, all_constructors = [], []

    for season in seasons:
        schedules.append(parse_season_schedule(client.get_season_races(season)))

        results = client.get_season_results(season)
        if results:
            results_df, drivers_df, constructors_df = parse_season_results(results)
            all_results.append(results_df)
            all_drivers.append(drivers_df)
            all_constructors.append(constructors_df)

        qualifying = client.get_season_qualifying(season)
        if qualifying:
            all_qualifying.append(parse_season_qualifying(qualifying))

    races_df = pd.concat(schedules, ignore_index=True) if schedules else pd.DataFrame()
    race_results_df = pd.concat(all_results, ignore_index=True) if all_results else pd.DataFrame()
    qualifying_df = pd.concat(all_qualifying, ignore_index=True) if all_qualifying else pd.DataFrame()

    drivers_df = (
        pd.concat(all_drivers, ignore_index=True).drop_duplicates("driver_id", keep="last")
        if all_drivers
        else pd.DataFrame()
    )
    constructors_df = (
        pd.concat(all_constructors, ignore_index=True).drop_duplicates("constructor_id", keep="last")
        if all_constructors
        else pd.DataFrame()
    )
    circuits_df = races_df.drop_duplicates("circuit_id", keep="last")[
        ["circuit_id", "circuit_name", "circuit_country", "circuit_locality", "circuit_lat", "circuit_long", "circuit_url"]
    ].reset_index(drop=True) if not races_df.empty else pd.DataFrame()

    races_df = races_df.drop(
        columns=["circuit_name", "circuit_country", "circuit_locality", "circuit_lat", "circuit_long", "circuit_url"]
    ) if not races_df.empty else races_df

    return {
        "races": races_df,
        "circuits": circuits_df,
        "drivers": drivers_df,
        "constructors": constructors_df,
        "race_results": race_results_df,
        "qualifying_results": qualifying_df,
    }
