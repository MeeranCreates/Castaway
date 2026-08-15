from dataclasses import dataclass
from pyglm import glm


@dataclass
class CloudSystem:
    """Procedural sky cloud layer for a custom OpenGL renderer.

    This is intentionally lightweight and separate from the main scene rendering so it
    can later be replaced with true volumetric clouds without reworking the entire sky.
    """
    density: float = 0.62
    height: float = 90.0
    speed: float = 0.12
    wind: glm.vec2 = glm.vec2(0.36, 0.12)
    offset: glm.vec2 = glm.vec2(0.0, 0.0)
    coverage: float = 0.55
    color_top: glm.vec3 = glm.vec3(0.88, 0.9, 0.94)
    color_bottom: glm.vec3 = glm.vec3(0.62, 0.68, 0.76)

    def __post_init__(self):
        self.wind = glm.vec2(self.wind.x, self.wind.y)
        self.offset = glm.vec2(self.offset.x, self.offset.y)

    def update(self, dt):
        self.offset += self.wind * self.speed * dt

    def set_wind(self, wind):
        self.wind = glm.vec2(wind.x, wind.y)

    def set_speed(self, speed):
        self.speed = max(0.0, float(speed))

    def set_density(self, density):
        self.density = max(0.0, min(1.0, float(density)))

    def set_height(self, height):
        self.height = max(0.0, float(height))
