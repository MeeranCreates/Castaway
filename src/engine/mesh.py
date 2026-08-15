import ctypes
import numpy as np
from OpenGL.GL import *


class Mesh:
    """Interleaved indexed mesh: position(3), normal(3), tangent(3), uv(2)."""
    stride = 11 * 4
    def __init__(self, vertices, indices):
        self.count = len(indices)
        self.vao, self.vbo, self.ebo = glGenVertexArrays(1), glGenBuffers(1), glGenBuffers(1)
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, np.asarray(vertices, np.float32), GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, np.asarray(indices, np.uint32), GL_STATIC_DRAW)
        for index, count, offset in ((0, 3, 0), (1, 3, 12), (2, 3, 24), (3, 2, 36)):
            glEnableVertexAttribArray(index)
            glVertexAttribPointer(index, count, GL_FLOAT, GL_FALSE, self.stride, ctypes.c_void_p(offset))
        glBindVertexArray(0)

    def draw(self, instances=1):
        glBindVertexArray(self.vao)
        if instances == 1: glDrawElements(GL_TRIANGLES, self.count, GL_UNSIGNED_INT, None)
        else: glDrawElementsInstanced(GL_TRIANGLES, self.count, GL_UNSIGNED_INT, None, instances)
        glBindVertexArray(0)


def make_plane(size=1.0):
    s = size * .5
    # normal and tangent allow the water shader to derive a stable surface basis.
    v = [[-s, 0, -s, 0, 1, 0, 1, 0, 0, 0, 0], [s, 0, -s, 0, 1, 0, 1, 0, 0, 1, 0],
         [s, 0, s, 0, 1, 0, 1, 0, 0, 1, 1], [-s, 0, s, 0, 1, 0, 1, 0, 0, 0, 1]]
    return Mesh(v, [0, 1, 2, 2, 3, 0])


def make_box(size=1.0):
    """A UV-mapped box suitable for crates, rocks (after scaling), and buildings."""
    s = size * .5
    faces = [((0, 0, 1), [(-s,-s,s),(s,-s,s),(s,s,s),(-s,s,s)]), ((0,0,-1), [(s,-s,-s),(-s,-s,-s),(-s,s,-s),(s,s,-s)]),
             ((1,0,0), [(s,-s,s),(s,-s,-s),(s,s,-s),(s,s,s)]), ((-1,0,0), [(-s,-s,-s),(-s,-s,s),(-s,s,s),(-s,s,-s)]),
             ((0,1,0), [(-s,s,s),(s,s,s),(s,s,-s),(-s,s,-s)]), ((0,-1,0), [(-s,-s,-s),(s,-s,-s),(s,-s,s),(-s,-s,s)])]
    vertices, indices = [], []
    for face, (normal, points) in enumerate(faces):
        tangent = (1, 0, 0) if abs(normal[1]) else (0, 1, 0)
        for (x, y, z), uv in zip(points, ((0,0),(1,0),(1,1),(0,1))): vertices.append([x,y,z,*normal,*tangent,*uv])
        base = face * 4; indices += [base,base+1,base+2,base+2,base+3,base]
    return Mesh(vertices, indices)


def make_cone(radius=.5, height=1.0, segments=10):
    vertices = [[0, height, 0, 0, 1, 0, 1, 0, 0, .5, 1], [0, 0, 0, 0, -1, 0, 1, 0, 0, .5, .5]]
    indices = []
    for i in range(segments):
        a = i * 6.283185 / segments; x, z = radius * np.cos(a), radius * np.sin(a)
        n = np.array([x, radius / height, z]); n /= np.linalg.norm(n)
        vertices.append([x, 0, z, *n, 1, 0, 0, i / segments, 0])
    for i in range(segments):
        current, nxt = 2 + i, 2 + (i + 1) % segments
        indices += [0, current, nxt, 1, nxt, current]
    return Mesh(vertices, indices)
