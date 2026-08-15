import math
import glfw
import glm


class Player:
    """Kinematic third-person player constrained to the procedural terrain surface."""
    def __init__(self, terrain, position=glm.vec3(0, 0, 0)):
        self.terrain, self.position = terrain, position
        self.speed, self.radius, self.facing = 9.0, .55, 0.0
        self.position.y = terrain.height_at(position.x, position.z)

    def update(self, window, camera, dt, colliders):
        forward = glm.normalize(glm.vec3(camera.target.x - camera.position.x, 0, camera.target.z - camera.position.z))
        right = glm.normalize(glm.cross(forward, glm.vec3(0, 1, 0)))
        direction = glm.vec3(0)
        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS: direction += forward
        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS: direction -= forward
        if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS: direction += right
        if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS: direction -= right
        if glm.length(direction) > 0.0:
            direction = glm.normalize(direction)
            candidate = self.position + direction * self.speed * dt
            for center, radius in colliders:
                delta = glm.vec2(candidate.x - center.x, candidate.z - center.z)
                distance = glm.length(delta)
                minimum = self.radius + radius
                if distance < minimum:
                    if distance < .001: delta, distance = glm.vec2(1, 0), 1.0
                    delta = glm.normalize(delta) * minimum
                    candidate.x, candidate.z = center.x + delta.x, center.z + delta.y
            self.position = candidate
            self.facing = math.degrees(math.atan2(direction.x, direction.z))
        self.position.y = self.terrain.height_at(self.position.x, self.position.z)

    @property
    def camera_target(self):
        # Aim at the torso, not the ground at the character's feet.
        return self.position + glm.vec3(0, 1.25, 0)
