"""
ADS (Aim Down Sights) zoom level data.

IMPORTANT: The "zoom" field here is a PLACEHOLDER.
It is NOT the official Ubisoft sensitivity multiplier.
The exact multiplier values must be extracted from the official article
before they are used in the mathematical model.

Ref: https://www.ubisoft.com/zh-tw/game/rainbow-six/siege/news-updates/3IMlDGlaRFgdvQNq3BOSFv/5-3
"""

from typing import List, Dict, Any


# ---------------------------------------------------------------------------
# Placeholder ADS table
# ---------------------------------------------------------------------------
# Each entry represents one selectable ADS zoom level in the UI.
# The "zoom" key conceptually identifies the zoom category (1.0x, 1.5x, ...)
# but does NOT claim to be the actual in-game multiplier.
# ---------------------------------------------------------------------------
ADS_TABLE: List[Dict[str, Any]] = [
    {"name": "0.0x",  "multiplier": 1.0},
    {"name": "1.0x",  "multiplier": 0.6},
    {"name": "2.0x",  "multiplier": 0.49},
    {"name": "3.0x",  "multiplier": 0.35},
    {"name": "8.0x",  "multiplier": 0.14},
]


def get_ads_names() -> List[str]:
    """
    Return a list of display names for all ADS zoom levels.

    Example:
        >>> get_ads_names()
        ['1.0x', '1.5x', '2.0x', ...]
    """
    return [ads["name"] for ads in ADS_TABLE]


def get_ads_data(index: int) -> Dict[str, Any]:
    """
    Retrieve the ADS entry at the given index.

    Parameters:
        index: Zero-based index into ADS_TABLE.

    Returns:
        A dict containing the ADS metadata (e.g. {"name": "1.5x", "zoom": 1.5}).

    Raises:
        IndexError: If the index is out of range.
    """
    if not (0 <= index < len(ADS_TABLE)):
        raise IndexError("ADS index out of range")
    return ADS_TABLE[index]

def get_ads_multiplier(index: int) -> float:
    """
    Return the official ADS multiplier for the given zoom level.
    This is the constant used in the Y5S3 conversion formula.
    """
    return get_ads_data(index)["multiplier"]