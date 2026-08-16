import math
import glfw
from pyglm import glm

from .mesh import make_capsule
from .world import SceneObject


class PlayerVisual:
    def __init__(self, player):
        self.player = player
        self.mesh = make_capsule(radius=0.4, height=1.8)
        self.position = glm.vec3(0.0, 0.0, 0.0)
        self.color = glm.vec3(0.5, 0.7, 0.9)
    
    @property
    def model(self):
        m = glm.translate(glm.mat4(1), self.position)
        m = glm.rotate(m, glm.radians(self.player.facing), glm.vec3(0, 1, 0))
        return m

    def update_from_player(self, player):
        self.position = player.position + glm.vec3(0.0, 0.9, 0.0)


class Player:
    """Kinematic third-person player constrained to the procedural terrain surface."""
    def __init__(self, terrain, position=glm.vec3(0, 0, 0), trees=None):
        self.terrain, self.position = terrain, glm.vec3(position.x, position.y, position.z)
        self.speed, self.radius, self.facing = 7.0, .55, 0.0
        self.sprint_speed = 12.0
        self.jump_speed, self.gravity = 7.8, 19.5
        self.vertical_velocity, self.grounded = 0.0, True
        self.coyote_time, self.jump_cooldown = 0.12, 0.0
        self.coyote_timer = 0.0
        self.position.y = terrain.height_at(position.x, position.z)
        self.state = "IDLE"
        self.ground_speed = 0.0
        self.animation_time = 0.0
        self.bob_amount = 0.0
        self.chop_target = None
        self.chop_timer = 0.0
        self.chop_cooldown = 0.0
        self.chop_duration = 0.65
        self.chop_impact_done = False
        self.visual = PlayerVisual(self)
        self.trees = trees or []
        self.interact_tree = None

    def _current_movement_state(self):
        if self.chop_target is not None:
            return "CHOPPING"
        if not self.grounded:
            return "JUMPING" if self.vertical_velocity > 0.0 else "FALLING"
        if self.ground_speed > 8.0:
            return "RUNNING"
        if self.ground_speed > 0.5:
            return "WALKING"
        return "IDLE"

    def _find_interactable_tree(self, trees):
        if trees is None:
            return None
        best_tree = None
        best_distance = 999.0
        for tree in trees:
            if not getattr(tree, "alive", True):
                continue
            dx = tree.position.x - self.position.x
            dz = tree.position.z - self.position.z
            dist = math.hypot(dx, dz)
            if dist > 3.2 or dist >= best_distance:
                continue
            toward = glm.vec3(dx, 0.0, dz)
            facing = glm.vec3(math.sin(glm.radians(self.facing)), 0.0, math.cos(glm.radians(self.facing)))
            if glm.length(toward) > 0.0:
                toward = glm.normalize(toward)
                if glm.dot(toward, facing) < 0.25:
                    continue
            best_tree = tree
            best_distance = dist
        return best_tree

    def begin_chop(self, tree):
        if tree is None or not getattr(tree, "alive", True):
            return
        self.state = "CHOPPING"
        self.chop_target = tree
        self.chop_timer = 0.0
        self.chop_impact_done = False
        self.ground_speed = 0.0
        self.chop_cooldown = 0.35

    def update(self, window, camera, dt, colliders, trees=None):
        if trees is not None:
            self.trees = trees

        forward = glm.normalize(glm.vec3(camera.target.x - camera.position.x, 0, camera.target.z - camera.position.z))
        right = glm.normalize(glm.cross(forward, glm.vec3(0, 1, 0)))
        direction = glm.vec3(0)
        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS: direction += forward
        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS: direction -= forward
        if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS: direction += right
        if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS: direction -= right

        self.interact_tree = self._find_interactable_tree(self.trees)

        if self.chop_target is not None and self.state == "CHOPPING":
            self.chop_timer += dt
            if self.chop_timer >= self.chop_duration:
                self.state = self._current_movement_state()
                self.chop_target = None
                self.chop_timer = 0.0
                self.chop_cooldown = 0.5
                self.chop_impact_done = False
            elif not self.chop_impact_done and self.chop_timer >= self.chop_duration * 0.52:
                if self.chop_target is not None and getattr(self.chop_target, "alive", False):
                    self.chop_target.damage(20)
                self.chop_impact_done = True
        else:
            self.chop_impact_done = False

        if self.chop_cooldown > 0.0:
            self.chop_cooldown = max(0.0, self.chop_cooldown - dt)

        if self.state != "CHOPPING":
            if glfw.get_key(window, glfw.KEY_E) == glfw.PRESS and self.chop_cooldown <= 0.05:
                tree = self.interact_tree
                if tree is not None:
                    self.begin_chop(tree)

            move_speed = self.sprint_speed if glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS else self.speed
            if glm.length(direction) > 0.0:
                direction = glm.normalize(direction)
                self.ground_speed = move_speed
                self.state = "RUNNING" if glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS and glm.length(direction) > 0.0 else "WALKING"
                candidate = self.position + direction * move_speed * dt
                for center, radius in colliders:
                    delta = glm.vec2(candidate.x - center.x, candidate.z - center.z)
                    distance = glm.length(delta)
                    minimum = self.radius + radius
                    if distance < minimum:
                        if distance < .001:
                            delta, distance = glm.vec2(1, 0), 1.0
                        delta = glm.normalize(delta) * minimum
                        candidate.x, candidate.z = center.x + delta.x, center.z + delta.y
                self.position = candidate
                self.facing = math.degrees(math.atan2(direction.x, direction.z))
            else:
                self.ground_speed = 0.0
                self.state = "IDLE"

        if self.jump_cooldown > 0.0:
            self.jump_cooldown = max(0.0, self.jump_cooldown - dt)

        if self.grounded:
            self.coyote_timer = self.coyote_time
        else:
            self.coyote_timer = max(0.0, self.coyote_timer - dt)

        if glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS and self.jump_cooldown == 0.0 and self.coyote_timer > 0.0 and self.state != "CHOPPING":
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

        if self.state != "CHOPPING":
            self.state = self._current_movement_state()

        self.animation_time += dt
        self.bob_amount = math.sin(self.animation_time * (4.0 if self.state == "RUNNING" else 2.4)) * (0.10 if self.state in {"WALKING", "RUNNING"} else 0.02)

    @property
    def camera_target(self):
        return self.position + glm.vec3(0, 1.25, 0)
