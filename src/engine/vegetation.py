import ctypes
import numpy as np
from OpenGL.GL import *
from .mesh import Mesh


class InstancedVegetation:
    """One low-poly grass blade mesh, batched into a single instanced draw call."""
    def __init__(self, terrain, count=12000, field_size=260.0):
        # Two crossed cards form visible blades from every camera direction.
        vertices = [[-.055, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0], [.055, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0],
                    [.028, .55, 0, 0, 1, 0, 1, 0, 0, 1, 1], [-.028, .55, 0, 0, 1, 0, 1, 0, 0, 0, 1],
                    [0, 0, -.055, 0, 1, 0, 1, 0, 0, 0, 0], [0, 0, .055, 0, 1, 0, 1, 0, 0, 1, 0],
                    [0, .55, .028, 0, 1, 0, 1, 0, 0, 1, 1], [0, .55, -.028, 0, 1, 0, 1, 0, 0, 0, 1]]
        indices = [0, 1, 2, 2, 3, 0, 4, 5, 6, 6, 7, 4]
        self.mesh, self.count = Mesh(vertices, indices), count
        rng, transforms = np.random.default_rng(9), np.zeros((count, 4, 4), np.float32)
        i = attempts = 0
        while i < count and attempts < count * 18:
            attempts += 1
            x, z = rng.uniform(-field_size / 2, field_size / 2, 2)
            scale = rng.uniform(.62, 1.65)
            y = terrain.height_at(x, z)
            if y < .35:
                continue
            transforms[i] = [[scale, 0, 0, 0], [0, scale, 0, 0], [0, 0, scale, 0], [x, y, z, 1]]
            i += 1
        self.count = i
        self.instance_vbo = glGenBuffers(1)
        glBindVertexArray(self.mesh.vao); glBindBuffer(GL_ARRAY_BUFFER, self.instance_vbo)
        glBufferData(GL_ARRAY_BUFFER, transforms.nbytes, transforms, GL_STATIC_DRAW)
        for col in range(4):
            glEnableVertexAttribArray(4 + col)
            glVertexAttribPointer(4 + col, 4, GL_FLOAT, GL_FALSE, 64, ctypes.c_void_p(col * 16))
            glVertexAttribDivisor(4 + col, 1)
        glBindVertexArray(0)

    def draw(self): self.mesh.draw(self.count)
