import math
from pyglm import glm


class OrbitCamera:
    """Third-person camera with yaw/pitch orbit controls around a target point."""
    def __init__(self, target=glm.vec3(0, 3, 0), distance=16.0):
        self.target, self.distance = target, distance
        # Positive pitch places the camera above the player, looking down at them.
        self.yaw, self.pitch = -125.0, 17.0
        self.fov, self._last_mouse = 62.0, None

    def mouse_look(self, x, y, active=True):
        if self._last_mouse is None:
            self._last_mouse = (x, y)
            return
        dx, dy = x - self._last_mouse[0], y - self._last_mouse[1]
        self._last_mouse = (x, y)
        if active:
            self.yaw += dx * 0.18
            # A third-person follow camera must not orbit below the character.
            self.pitch = max(7.0, min(58.0, self.pitch - dy * 0.18))

    def zoom(self, amount):
        self.distance = max(8.0, min(42.0, self.distance - amount * 1.5))

    @property
    def position(self):
        yaw, pitch = math.radians(self.yaw), math.radians(self.pitch)
        offset = glm.vec3(math.cos(yaw) * math.cos(pitch), math.sin(pitch),
                          math.sin(yaw) * math.cos(pitch)) * self.distance
        return self.target + offset

    def view(self):
        return glm.lookAt(self.position, self.target, glm.vec3(0, 1, 0))

    def projection(self, aspect):
        return glm.perspective(glm.radians(self.fov), aspect, 0.1, 400.0)
