class Tolerence:
    """
    Centralized epsilon values for numeric tolerances.

    Call apply_overrides at startup to override values from a config dict.
    """

    GENERAL = 1e-9
    COLLISION = 0.1

    @classmethod
    def apply_overrides(cls, overrides: dict[str, float] | None) -> None:
        if not overrides:
            return
        if "general" in overrides:
            cls.GENERAL = float(overrides["general"])
        if "collision" in overrides:
            cls.COLLISION = float(overrides["collision"])
