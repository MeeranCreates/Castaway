from dataclasses import dataclass
import glm
from .mesh import make_box, make_cone


@dataclass
class SceneObject:
    mesh: object
    position: glm.vec3
    scale: glm.vec3
    color: glm.vec3
    collision_radius: float = 0.0
    rotation: float = 0.0

    @property
    def model(self):
        m = glm.translate(glm.mat4(1), self.position)
        m = glm.rotate(m, glm.radians(self.rotation), glm.vec3(0, 1, 0))
        return glm.scale(m, self.scale)


class IslandProps:
    """Visible, collidable island landmarks positioned against Terrain.height_at()."""
    def __init__(self, terrain):
        box, cone = make_box(), make_cone()
        self.objects = []
        tree_variants = [
            (glm.vec3(.23, .12, .045), glm.vec3(.03, .18, .05), 1.0, 1.0),
            (glm.vec3(.18, .10, .04), glm.vec3(.05, .22, .08), 1.15, 1.1),
            (glm.vec3(.27, .17, .08), glm.vec3(.08, .14, .06), 0.9, 1.4),
            (glm.vec3(.20, .14, .08), glm.vec3(.12, .20, .08), 0.8, 1.8),
            (glm.vec3(.18, .13, .06), glm.vec3(.07, .28, .12), 0.7, 1.25),
        ]
        for x, z, size, variant in [
            (-18,-9,2.6,0), (-14,-14,2.1,1), (15,-12,3.2,2), (22,8,2.4,3), (-26,12,2.8,0), (8,22,2.3,1),
            (30,-18,2.9,2), (-32,20,2.5,3), (33,12,2.2,4), (-10,30,2.7,2), (18,30,2.4,0), (-30,-28,3.0,3),
            (40,-8,2.7,4), (-24,34,2.5,1), (12,-35,2.9,0), (-42,-2,2.3,2), (36,26,2.6,4), (-8,-38,2.4,3)
        ]:
            y = terrain.height_at(x, z)
            trunk_color, canopy_color, scale_mod, canopy_scale = tree_variants[variant]
            trunk_scale = glm.vec3(.35 * scale_mod, size * 1.45 * scale_mod, .35 * scale_mod)
            canopy_scale = glm.vec3(size * 1.1 * canopy_scale, size * 2.2 * canopy_scale, size * 1.1 * canopy_scale)
            canopy_center = glm.vec3(x, y + size * 1.65 * scale_mod, z)
            self.objects += [
                SceneObject(box, glm.vec3(x, y + size * .75 * scale_mod, z), trunk_scale, trunk_color, .75),
                SceneObject(box, glm.vec3(x, y + size * 1.05 * scale_mod, z), glm.vec3(.30 * scale_mod, .36 * scale_mod, .30 * scale_mod), trunk_color),
                SceneObject(cone, canopy_center, canopy_scale, canopy_color)
            ]
        for x, z, scale in [(-5,10,1.4), (11,4,1.1), (-23,-3,1.8), (25,-17,1.35), (4,-22,1.5), (35,-2,1.9), (-32,-14,1.7), (-12,36,1.8), (28,27,1.6), (-38,14,1.5), (16,39,1.7), (42,7,1.8)]:
            self.objects.append(SceneObject(box, glm.vec3(x, terrain.height_at(x, z) + scale * .38, z), glm.vec3(scale, scale * .76, scale), glm.vec3(.28, .27, .24), scale * .48, x * 7.3))
        x, z, y = -5, -27, terrain.height_at(-5, -27)
        self.objects += [SceneObject(box, glm.vec3(x, y + 1.0, z), glm.vec3(2.2, .55, 7.0), glm.vec3(.20, .09, .025), 2.2, -12),
                         SceneObject(box, glm.vec3(x, y + 3.4, z), glm.vec3(.18, 5.0, .18), glm.vec3(.13, .06, .02), .3)]

    @property
    def colliders(self):
        return [(obj.position, obj.collision_radius) for obj in self.objects if obj.collision_radius > 0]
