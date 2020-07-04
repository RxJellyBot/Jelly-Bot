__all__ = ["UnhandledSkillDirectionError"]


class UnhandledSkillDirectionError(ValueError):
    def __init__(self, skill_direction):
        super().__init__(f"Unhandled skill direction ({skill_direction})")
