from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PreferredWPM:
    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError("Preferred WPM must be greater than zero.")
        if self.value > 2_000:
            raise ValueError("Preferred WPM must be 2000 or less.")


@dataclass(frozen=True, slots=True)
class PreferredWordsPerFlash:
    value: int

    def __post_init__(self) -> None:
        if self.value not in {1, 2, 3}:
            raise ValueError("Preferred words per flash must be 1, 2, or 3.")
