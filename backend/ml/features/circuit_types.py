"""Static circuit-type lookup used as a categorical feature.

Ergast/Jolpica doesn't classify circuits by type, so this is a small
hand-maintained mapping of well-known street circuits. Anything not listed
defaults to "permanent". This is a coarse but defensible proxy for track
character (overtaking difficulty, downforce demands) without depending on
unavailable/unreliable metadata.
"""

STREET_CIRCUITS = {
    "monaco",
    "baku",
    "marina_bay",
    "jeddah",
    "las_vegas",
    "miami",
    "albert_park",  # semi-street; treated as street for downforce/overtaking profile
    "valencia",
    "detroit",
    "phoenix",
    "adelaide",
}


# Checked only for circuits not already classified as "street" above.
HIGH_SPEED_CIRCUITS = {
    "monza",
    "spa",
    "silverstone",
    "red_bull_ring",
}


def get_circuit_type(circuit_id: str) -> str:
    if circuit_id in STREET_CIRCUITS:
        return "street"
    if circuit_id in HIGH_SPEED_CIRCUITS:
        return "high_speed"
    return "permanent"
