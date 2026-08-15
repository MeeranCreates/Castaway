import math
import glfw
from pyglm import glm


class OrbitCamera:
    """Third-person camera with yaw/pitch orbit controls around a target point."""
    def __init__(self, target=glm.vec3(0, 3, 0), distance=16.0):
        self.target, self.distance = target, distance
        # Positive pitch places the camera above the player, looking down at them.
        self.yaw, self.pitch = -125.0, 17.0
        self.fov, self._last_mouse = 62.0, None
        self.target_lerp = 1.0

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

    def update_from_locked_cursor(self, window):
        width, height = glfw.get_window_size(window)
        center_x, center_y = width * 0.5, height * 0.5
        x, y = glfw.get_cursor_pos(window)
        if self._last_mouse is None:
            self._last_mouse = (center_x, center_y)
            glfw.set_cursor_pos(window, center_x, center_y)
            return
        dx, dy = x - self._last_mouse[0], y - self._last_mouse[1]
        self.yaw += dx * 0.18
        self.pitch = max(7.0, min(58.0, self.pitch - dy * 0.18))
        self._last_mouse = (center_x, center_y)
        glfw.set_cursor_pos(window, center_x, center_y)

    def follow_target(self, target, dt, airborne=False):
        if airborne:
            self.target_lerp = max(0.04, self.target_lerp * 0.92)
        else:
            self.target_lerp = min(1.0, self.target_lerp + dt * 3.0)
        self.target = self.target * (1.0 - self.target_lerp) + target * self.target_lerp

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
