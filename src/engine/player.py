import math
import glfw
import glm


class Player:
    """Kinematic third-person player constrained to the procedural terrain surface."""
    def __init__(self, terrain, position=glm.vec3(0, 0, 0)):
        self.terrain, self.position = terrain, position
        self.speed, self.radius, self.facing = 9.0, .55, 0.0
        self.sprint_speed = 14.0
        self.jump_speed, self.gravity = 7.8, 19.5
        self.vertical_velocity, self.grounded = 0.0, True
        self.coyote_time, self.jump_cooldown = 0.12, 0.0
        self.coyote_timer = 0.0
        self.position.y = terrain.height_at(position.x, position.z)

    def update(self, window, camera, dt, colliders):
        forward = glm.normalize(glm.vec3(camera.target.x - camera.position.x, 0, camera.target.z - camera.position.z))
        right = glm.normalize(glm.cross(forward, glm.vec3(0, 1, 0)))
        direction = glm.vec3(0)
        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS: direction += forward
        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS: direction -= forward
        if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS: direction += right
        if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS: direction -= right

        move_speed = self.sprint_speed if glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS else self.speed
        if glm.length(direction) > 0.0:
            direction = glm.normalize(direction)
            candidate = self.position + direction * move_speed * dt
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

        if self.jump_cooldown > 0.0:
            self.jump_cooldown = max(0.0, self.jump_cooldown - dt)

        if self.grounded:
            self.coyote_timer = self.coyote_time
        else:
            self.coyote_timer = max(0.0, self.coyote_timer - dt)

        if glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS and self.jump_cooldown == 0.0 and self.coyote_timer > 0.0:
            self.vertical_velocity = self.jump_speed
            self.grounded = False
            self.coyote_timer = 0.0
            self.jump_cooldown = 0.18

        if glfw.get_key(window, glfw.KEY_SPACE) == glfw.RELEASE and self.vertical_velocity > 0.0:
            self.vertical_velocity *= 0.55

        self.position.y += self.vertical_velocity * dt
        self.vertical_velocity -= self.gravity * dt
        ground_height = self.terrain.height_at(self.position.x, self.position.z)
        if self.position.y <= ground_height:
            self.position.y = ground_height
            self.vertical_velocity = 0.0
            self.grounded = True
        else:
            self.grounded = False

    @property
    def camera_target(self):
        # Aim at the torso, not the ground at the character's feet.
        return self.position + glm.vec3(0, 1.25, 0)
