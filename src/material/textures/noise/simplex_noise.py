import math
from dataclasses import dataclass

from src.material.textures.noise.normal_base import Noise


@dataclass
class SimplexNoise(Noise):
    def value(self, p):
        x = (p + self.offset) * self.scale

        # Skewing factors for 3D simplex grid
        F3 = 1.0 / 3.0
        G3 = 1.0 / 6.0

        s = (x.x + x.y + x.z) * F3
        i = math.floor(x.x + s)
        j = math.floor(x.y + s)
        k = math.floor(x.z + s)

        t = (i + j + k) * G3
        X0 = i - t
        Y0 = j - t
        Z0 = k - t

        x0 = x.x - X0
        y0 = x.y - Y0
        z0 = x.z - Z0

        # Determine simplex corner ordering
        if x0 >= y0:
            if y0 >= z0:
                i1,j1,k1 = 1,0,0
                i2,j2,k2 = 1,1,0
            elif x0 >= z0:
                i1,j1,k1 = 1,0,0
                i2,j2,k2 = 1,0,1
            else:
                i1,j1,k1 = 0,0,1
                i2,j2,k2 = 1,0,1
        else:
            if y0 < z0:
                i1,j1,k1 = 0,0,1
                i2,j2,k2 = 0,1,1
            elif x0 < z0:
                i1,j1,k1 = 0,1,0
                i2,j2,k2 = 0,1,1
            else:
                i1,j1,k1 = 0,1,0
                i2,j2,k2 = 1,1,0

        # Offsets for corners
        x1 = x0 - i1 + G3
        y1 = y0 - j1 + G3
        z1 = z0 - k1 + G3
        x2 = x0 - i2 + 2.0 * G3
        y2 = y0 - j2 + 2.0 * G3
        z2 = z0 - k2 + 2.0 * G3
        x3 = x0 - 1.0 + 3.0 * G3
        y3 = y0 - 1.0 + 3.0 * G3
        z3 = z0 - 1.0 + 3.0 * G3

        # Gradient contributions (simple hash)
        def grad(ix, iy, iz, x, y, z):
            h = hash((ix, iy, iz)) & 15
            u = x if h < 8 else y
            v = y if h < 4 else (x if h in (12, 14) else z)
            return ((u if (h & 1) == 0 else -u) +
                    (v if (h & 2) == 0 else -v))

        n0 = n1 = n2 = n3 = 0.0

        for (dx,dy,dz,xx,yy,zz) in [
            (0,0,0,x0,y0,z0),
            (i1,j1,k1,x1,y1,z1),
            (i2,j2,k2,x2,y2,z2),
            (1,1,1,x3,y3,z3)
        ]:
            t = 0.6 - xx*xx - yy*yy - zz*zz
            if t > 0:
                t *= t
                n = grad(i+dx, j+dy, k+dz, xx, yy, zz)
                if (dx,dy,dz) == (0,0,0): n0 = t*t*n
                elif (dx,dy,dz) == (i1,j1,k1): n1 = t*t*n
                elif (dx,dy,dz) == (i2,j2,k2): n2 = t*t*n
                else: n3 = t*t*n

        return (32.0 * (n0 + n1 + n2 + n3)) * self.strength
