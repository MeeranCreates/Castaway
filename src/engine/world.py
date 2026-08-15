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
        # Trees are deliberately separate trunk/canopy objects so they can evolve into real model assets.
        for x, z, size in [(-18,-9,2.6), (-14,-14,2.1), (15,-12,3.2), (22,8,2.4), (-26,12,2.8), (8,22,2.3)]:
            y = terrain.height_at(x, z)
            self.objects += [SceneObject(box, glm.vec3(x,y+size*.8,z), glm.vec3(.36,size*1.6,.36), glm.vec3(.23,.12,.045), .75),
                             SceneObject(cone, glm.vec3(x,y+size*1.45,z), glm.vec3(size,size*1.7,size), glm.vec3(.035,.19,.055))]
        for x, z, scale in [(-5,10,1.4), (11,4,1.1), (-23,-3,1.8), (25,-17,1.35), (4,-22,1.5)]:
            self.objects.append(SceneObject(box, glm.vec3(x,terrain.height_at(x,z)+scale*.38,z), glm.vec3(scale,scale*.76,scale), glm.vec3(.28,.27,.24), scale*.48, x*7.3))
        # A shipwreck-like survival landmark: meaningful geometry, not a background decal.
        x, z, y = -5, -27, terrain.height_at(-5,-27)
        self.objects += [SceneObject(box, glm.vec3(x,y+1.0,z), glm.vec3(2.2,.55,7.0), glm.vec3(.20,.09,.025), 2.2, -12),
                         SceneObject(box, glm.vec3(x,y+3.4,z), glm.vec3(.18,5.0,.18), glm.vec3(.13,.06,.02), .3)]

    @property
    def colliders(self):
        return [(obj.position, obj.collision_radius) for obj in self.objects if obj.collision_radius > 0]
