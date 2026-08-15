from dataclasses import dataclass
from pyglm import glm


@dataclass
class Sun:
    """Directional light representation for the Castaway renderer."""
    direction: glm.vec3 = glm.vec3(0.65, 0.85, 0.35)
    color: glm.vec3 = glm.vec3(1.0, 0.85, 0.68)
    intensity: float = 1.35
    ambient_strength: float = 0.35

    def __post_init__(self):
        self.direction = glm.normalize(self.direction)

    @property
    def daylight_factor(self):
        return max(0.0, min(1.0, (self.direction.y + 0.2) / 0.9))

    def set_direction(self, direction):
        self.direction = glm.normalize(direction)

    def set_color(self, color):
        self.color = color

    def set_intensity(self, intensity):
        self.intensity = max(0.0, float(intensity))

    def set_ambient_strength(self, strength):
        self.ambient_strength = max(0.0, float(strength))
