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


def make_cone(radius=.5, height=1.0, segments=24):
    base_y = -0.35 * height
    vertices = [[0, height, 0, 0, 1, 0, 1, 0, 0, .5, 1], [0, base_y, 0, 0, -1, 0, 1, 0, 0, .5, .5]]
    indices = []
    for i in range(segments):
        a = i * 6.283185 / segments; x, z = radius * np.cos(a), radius * np.sin(a)
        n = np.array([x, 1.0, z], dtype=np.float32)
        n /= np.linalg.norm(n)
        vertices.append([x, 0, z, *n, 1, 0, 0, i / segments, 0])
    for i in range(segments):
        current, nxt = 2 + i, 2 + (i + 1) % segments
        indices += [0, nxt, current, 1, current, nxt]
    return Mesh(vertices, indices)


def make_capsule(radius=0.5, height=2.0, segments=16, rings=8):
    """Capsule: cylinder with hemispheres at top and bottom."""
    vertices, indices = [], []
    half_height = height * 0.5
    
    # Top hemisphere
    for ring in range(rings):
        theta = ring * np.pi / (2 * rings)
        sin_theta, cos_theta = np.sin(theta), np.cos(theta)
        for seg in range(segments):
            phi = seg * 2.0 * np.pi / segments
            sin_phi, cos_phi = np.sin(phi), np.cos(phi)
            x, y, z = radius * sin_theta * cos_phi, half_height + radius * cos_theta, radius * sin_theta * sin_phi
            nx, ny, nz = sin_theta * cos_phi, cos_theta, sin_theta * sin_phi
            u, v = seg / segments, ring / rings
            vertices.append([x, y, z, nx, ny, nz, 1, 0, 0, u, v])
    
    # Cylinder
    cyl_start = len(vertices)
    for seg in range(segments):
        phi = seg * 2.0 * np.pi / segments
        sin_phi, cos_phi = np.sin(phi), np.cos(phi)
        x, z = radius * cos_phi, radius * sin_phi
        vertices.append([x, half_height, z, cos_phi, 0, sin_phi, 1, 0, 0, seg / segments, 0.5])
        vertices.append([x, -half_height, z, cos_phi, 0, sin_phi, 1, 0, 0, seg / segments, 0.5])
    
    # Bottom hemisphere
    bot_start = len(vertices)
    for ring in range(rings):
        theta = np.pi / 2 + ring * np.pi / (2 * rings)
        sin_theta, cos_theta = np.sin(theta), np.cos(theta)
        for seg in range(segments):
            phi = seg * 2.0 * np.pi / segments
            sin_phi, cos_phi = np.sin(phi), np.cos(phi)
            x, y, z = radius * sin_theta * cos_phi, -half_height + radius * cos_theta, radius * sin_theta * sin_phi
            nx, ny, nz = sin_theta * cos_phi, cos_theta, sin_theta * sin_phi
            u, v = seg / segments, 0.5 + ring / rings
            vertices.append([x, y, z, nx, ny, nz, 1, 0, 0, u, v])
    
    # Top hemisphere indices
    for ring in range(rings - 1):
        for seg in range(segments):
            a = ring * segments + seg
            b = a + segments
            c = (a + 1) % (segments if ring < rings - 1 else segments)
            d = (b + 1) % segments + b - a
            indices += [a, b, c, c, b, d]
    
    # Cylinder indices
    for seg in range(segments):
        a = cyl_start + seg * 2
        b = a + 1
        c = cyl_start + ((seg + 1) % segments) * 2
        d = c + 1
        indices += [a, b, c, c, b, d]
    
    # Bottom hemisphere indices
    for ring in range(rings - 1):
        for seg in range(segments):
            a = bot_start + ring * segments + seg
            b = a + segments
            c = (a + 1) % segments if ring < rings - 1 else (a + 1) % segments
            indices += [a, c, b, b, c, b + 1 if ring < rings - 1 else c + 1]
    
    return Mesh(vertices, indices)


def make_sphere(radius=1.0, segments=16, rings=12):
    """UV-mapped sphere for sun, moon, and stars backdrop."""
    vertices, indices = [], []
    for ring in range(rings + 1):
        theta = ring * np.pi / rings
        sin_theta, cos_theta = np.sin(theta), np.cos(theta)
        for seg in range(segments + 1):
            phi = seg * 2.0 * np.pi / segments
            sin_phi, cos_phi = np.sin(phi), np.cos(phi)
            x, y, z = radius * sin_theta * cos_phi, radius * cos_theta, radius * sin_theta * sin_phi
            nx, ny, nz = sin_theta * cos_phi, cos_theta, sin_theta * sin_phi
            u, v = seg / segments, ring / rings
            vertices.append([x, y, z, nx, ny, nz, 1, 0, 0, u, v])
    for ring in range(rings):
        for seg in range(segments):
            a = ring * (segments + 1) + seg
            b = a + segments + 1
            indices += [a, b, a + 1, a + 1, b, b + 1]
    return Mesh(vertices, indices)
