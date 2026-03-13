"""Canonical character identifier helpers and binding validation utilities."""

from __future__ import annotations

import csv
from functools import lru_cache
from typing import Dict, List, Optional, Sequence, Set, Tuple

DEFAULT_VARIANT = "Standard"

# Canonical strategy:
# - Canonical Name is the exact CSV "Name" value after alias normalization.
# - Canonical character id is "<Canonical Name>::<Variant>".
LEGACY_NAME_ALIASES: Dict[str, str] = {
    "Megumi Fushiguro": "Fushiguro Megumi",
    "Yuta Okkotsu": "Yuta Okkotsu",
    "Hakari Kinji": "Kinji Hakari",
    "Toge": "Toge Inumaki",
    "Inumaki Toge": "Toge Inumaki",
    "Kamo Noritoshi": "Noritoshi Kamo",
    "Todo Aoi": "Aoi Todo",
    "Yaga": "Masamichi Yaga",
    "Sukuna": "Ryomen Sukuna",
    "Ryu": "Ryu Ishigori",
}


def normalize_character_name(name: Optional[str]) -> str:
    """Normalize legacy/alias names to canonical CSV name keys."""
    normalized = (name or "").strip()
    if not normalized:
        return ""
    return LEGACY_NAME_ALIASES.get(normalized, normalized)


def normalize_variant(variant: Optional[str]) -> str:
    normalized = (variant or "").strip()
    return normalized or DEFAULT_VARIANT


def build_character_id(name: Optional[str], variant: Optional[str] = None) -> str:
    return f"{normalize_character_name(name)}::{normalize_variant(variant)}"


def _read_csv_names(csv_path: str) -> Set[str]:
    names: Set[str] = set()
    with open(csv_path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            names.add(normalize_character_name(row.get("Name")))
    return names


@lru_cache(maxsize=8)
def validate_character_bindings(
    csv_path: str,
    card_ability_names: Sequence[str],
    ultimate_names: Sequence[str],
) -> Tuple[str, ...]:
    """Return human-readable binding warnings for names in the source CSV."""
    canonical_csv_names = _read_csv_names(csv_path)
    card_set = {normalize_character_name(name) for name in card_ability_names}
    ultimate_set = {normalize_character_name(name) for name in ultimate_names}

    messages: List[str] = []

    missing_card = sorted(canonical_csv_names - card_set)
    if missing_card:
        messages.append(
            "Missing card ability bindings for: " + ", ".join(missing_card)
        )

    missing_ultimate = sorted(canonical_csv_names - ultimate_set)
    if missing_ultimate:
        messages.append(
            "Missing ultimate ability bindings for: " + ", ".join(missing_ultimate)
        )

    extra_card = sorted(card_set - canonical_csv_names)
    if extra_card:
        messages.append(
            "Card ability bindings with no CSV match: " + ", ".join(extra_card)
        )

    extra_ultimate = sorted(ultimate_set - canonical_csv_names)
    if extra_ultimate:
        messages.append(
            "Ultimate ability bindings with no CSV match: " + ", ".join(extra_ultimate)
        )

    return tuple(messages)


def report_binding_validation(
    csv_path: str,
    card_ability_names: Sequence[str],
    ultimate_names: Sequence[str],
) -> None:
    """Print load-time validation issues exactly once per process+path."""
    issues = validate_character_bindings(csv_path, tuple(card_ability_names), tuple(ultimate_names))
    for issue in issues:
        print(f"[binding-validation] {issue}")
