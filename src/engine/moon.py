from dataclasses import dataclass, field

from pyglm import glm


@dataclass
class Moon:
    """Visible world-space moon and directional moonlight source."""
    direction: glm.vec3 = glm.vec3(-0.65, -0.85, -0.35)
    color: glm.vec3 = glm.vec3(0.55, 0.68, 0.98)
    intensity: float = 0.22
    ambient_strength: float = 0.18
    phase: float = 0.15
    visible: bool = True
    apparent_size: float = 1.0
    radius: float = 18.0
    world_position: glm.vec3 = field(default_factory=lambda: glm.vec3(0.0, 110.0, -180.0))

    def __post_init__(self):
        self.direction = glm.normalize(self.direction)
        self.world_position = self._position_from_direction(self.direction)
        self.phase = self.compute_phase(self.direction)

    @property
    def night_factor(self):
        return 1.0 - max(0.0, min(1.0, (self.direction.y + 0.2) / 0.9))

    def _position_from_direction(self, direction):
        dir_vec = glm.normalize(direction)
        orbital_radius = 180.0
        return dir_vec * orbital_radius + glm.vec3(0.0, 60.0, 0.0)

    def compute_phase(self, sun_direction=None):
        if sun_direction is None:
            return self.phase
        sun_dir = glm.normalize(sun_direction)
        angle = max(-1.0, min(1.0, float(glm.dot(self.direction, sun_dir))))
        # 0.0 = full moon, 1.0 = new moon.
        value = 1.0 - (angle * 0.5 + 0.5)
        return max(0.0, min(1.0, value))

    def set_direction(self, direction):
        self.direction = glm.normalize(direction)
        self.world_position = self._position_from_direction(self.direction)

    def set_color(self, color):
        self.color = color

    def set_intensity(self, intensity):
        self.intensity = max(0.0, float(intensity))

    def set_ambient_strength(self, strength):
        self.ambient_strength = max(0.0, float(strength))

    def set_phase(self, phase):
        self.phase = max(0.0, min(1.0, float(phase)))

    def update_from_state(self, moon_direction, sun_direction=None):
        self.set_direction(moon_direction)
        if sun_direction is not None:
            self.phase = self.compute_phase(sun_direction)

    def opposite_of(self, sun_direction):
        self.set_direction(-glm.normalize(sun_direction))

    def model_matrix(self):
        scale = glm.mat4(1.0)
        for i in range(3):
            scale[i][i] = self.radius * self.apparent_size
        return glm.translate(glm.mat4(1.0), self.world_position) * scale
