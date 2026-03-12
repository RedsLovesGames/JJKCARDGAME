from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List


@dataclass(frozen=True)
class AbilityEffect:
    duration: int = 0


@dataclass(frozen=True)
class BuffATK(AbilityEffect):
    amount: int = 0


@dataclass(frozen=True)
class BuffDEF(AbilityEffect):
    amount: int = 0


@dataclass(frozen=True)
class DamageReduction(AbilityEffect):
    reduction: float = 0.0


@dataclass(frozen=True)
class Stun(AbilityEffect):
    pass


@dataclass(frozen=True)
class SummonToken(AbilityEffect):
    name: str = "Token"
    atk: int = 0
    def_: int = 0


@dataclass(frozen=True)
class FlagEffect(AbilityEffect):
    flag: str = ""
    value: Any = True
    one_time: bool = False


class CardAbility:
    """Build structured effects from card metadata and csv text."""

    CSV_EFFECT_CONSTRUCTORS: List[tuple[str, Callable[[], List[AbilityEffect]]]] = [
        ("+50 atk", lambda: [BuffATK(amount=50, duration=1)]),
        ("+100 atk", lambda: [BuffATK(amount=100, duration=1)]),
        ("+50 atk and def", lambda: [BuffATK(amount=50, duration=1), BuffDEF(amount=50, duration=1)]),
        ("+100 atk and def", lambda: [BuffATK(amount=100, duration=1), BuffDEF(amount=100, duration=1)]),
        ("cannot attack during its next turn", lambda: [Stun(duration=1)]),
        ("reduce damage taken by 50", lambda: [DamageReduction(reduction=0.5, duration=1)]),
        (
            "token creature (atk 100/def 100)",
            lambda: [SummonToken(name="Token Creature", atk=100, def_=100, duration=1)],
        ),
        (
            "basic cursed corpse (atk 150/def 150)",
            lambda: [SummonToken(name="Basic Cursed Corpse", atk=150, def_=150, duration=2)],
        ),
        ("reduce the energy cost", lambda: [FlagEffect(flag="ultimate_cost_reduction", value=True, duration=1)]),
        ("draw 1 extra card", lambda: [FlagEffect(flag="extra_draw", value=True, duration=1)]),
    ]

    @staticmethod
    def apply_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> List[AbilityEffect]:
        """Compatibility layer: map legacy name/variant/effect text to structured effects."""
        effects: List[AbilityEffect] = []
        name = card.get("Name", "")
        variant = str(card.get("Variant", "")).lower()
        effect_text = str(card.get("Effect", "")).lower()

        # Existing bespoke logic (legacy compatibility)
        if name == "Gojo Satoru" and ("limitless" in effect_text or "honored one" in variant):
            effects.append(DamageReduction(reduction=0.5, duration=1))
        if name == "Fushiguro Megumi" and "detention center" in variant:
            effects.append(SummonToken(name="Ten Shadows Token", atk=100, def_=100, duration=1))
        if name == "Yuta Okkotsu" and "bound by rika" in effect_text and game_state.get("rika_on_field", False):
            effects.extend([BuffATK(amount=100, duration=1), BuffDEF(amount=100, duration=1)])
        if name == "Aoi Todo" and "boogie woogie" in effect_text:
            effects.append(FlagEffect(flag="can_swap_positions", value=True, duration=1))
        if name == "Kiyotaka Ijichi" and "desperate escape" in effect_text:
            effects.append(FlagEffect(flag="one_time_survival", value=True, one_time=True))

        # CSV text parser compatibility
        for trigger_text, constructor in CardAbility.CSV_EFFECT_CONSTRUCTORS:
            if trigger_text in effect_text:
                effects.extend(constructor())

        return effects
