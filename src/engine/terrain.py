import math
import numpy as np
from .mesh import Mesh


def _hash(x, z):
    return (math.sin(x * 127.1 + z * 311.7) * 43758.5453123) % 1.0


def _value_noise(x, z):
    ix, iz = math.floor(x), math.floor(z)
    fx, fz = x - ix, z - iz
    fx, fz = fx * fx * (3.0 - 2.0 * fx), fz * fz * (3.0 - 2.0 * fz)
    a, b, c, d = _hash(ix, iz), _hash(ix + 1, iz), _hash(ix, iz + 1), _hash(ix + 1, iz + 1)
    return ((a + (b - a) * fx) + ((c + (d - c) * fx) - (a + (b - a) * fx)) * fz) * 2.0 - 1.0


def _noise(x, z):
    """A coherent island heightfield: beach, rolling hills, and a rough highland."""
    f, amplitude, frequency, detail = 0.0, 1.0, .035, 0.0
    for _ in range(5):
        detail += _value_noise(x * frequency, z * frequency) * amplitude
        amplitude *= .5; frequency *= 2.05
    radius = math.sqrt(x * x + z * z)
    island = max(0.0, 1.0 - (radius / 57.0) ** 1.65)
    ridge = max(0.0, _value_noise(x * .018 + 13.0, z * .018 - 7.0)) * 5.0
    # Keep the interior land reliably above sea level.  Detail shapes hills; it
    # never punches accidental lakes through the playable island.
    return island * (8.0 + detail * 2.5 + ridge) - 2.5


class Terrain:
    def __init__(self, resolution=161, spacing=.75):
        self.resolution, self.spacing = resolution, spacing
        half = (resolution - 1) * spacing * .5
        vertices, indices = [], []
        for z in range(resolution):
            for x in range(resolution):
                wx, wz = x * spacing - half, z * spacing - half
                h = _noise(wx, wz)
                # Central difference normal and analytic grid tangent.
                dhx = (_noise(wx + spacing, wz) - _noise(wx - spacing, wz)) / (2 * spacing)
                dhz = (_noise(wx, wz + spacing) - _noise(wx, wz - spacing)) / (2 * spacing)
                n = np.array([-dhx, 1.0, -dhz]); n /= np.linalg.norm(n)
                t = np.array([1.0, dhx, 0.0]); t /= np.linalg.norm(t)
                vertices.append([wx, h, wz, *n, *t, x / (resolution - 1), z / (resolution - 1)])
        for z in range(resolution - 1):
            for x in range(resolution - 1):
                i = z * resolution + x
                indices += [i, i + 1, i + resolution + 1, i + resolution + 1, i + resolution, i]
        self.mesh = Mesh(vertices, indices)

    @staticmethod
    def height_at(x, z):
        """The authoritative terrain height query used by player and prop placement."""
        return _noise(x, z)

    def normal_at(self, x, z):
        step = self.spacing
        dx = (self.height_at(x + step, z) - self.height_at(x - step, z)) / (2.0 * step)
        dz = (self.height_at(x, z + step) - self.height_at(x, z - step)) / (2.0 * step)
        n = np.array([-dx, 1.0, -dz], dtype=np.float32)
        return n / np.linalg.norm(n)
