from __future__ import annotations
import math
import numpy as np

from src import Color
from src.math.vec3 import Vec3

def hdr_to_ndarray(path: str) -> np.ndarray:
    """
    Reads and transforms an HDR image file to a numpy ndarray of shape (H, W, 3) with float32 RGB values. Handles RLE decoding
    and transforms from RGBE to linear RGB. Supports vertical and horizontal flipping based on HDR header info.
    param path: Path to HDR image file
    return: numpy ndarray of shape (H, W, 3) with float32 RGB values
    """
    with open(path, "rb") as f:
        # header buffer
        header = []

        # read header lines until empty line
        i = 0
        while True:
            line = f.readline()
            if not line:
                raise Exception("End of file before HDR header")
            # gets rid of non-ascii characters and trailing whitespace
            line = line.decode("ascii", errors="ignore").strip()
            #check first line for valid signature
            if i == 0 and line != "#?RADIANCE":
                raise Exception("Not a valid HDR file.")
            # empty line indicates end of header
            if line == "":
                break
            # store header lines
            header.append(line)
            i += 1

        # after header, expect resolution line: -Y height +X width (or +Y -X) in format 4 tokens
        res = f.readline().decode("ascii", errors="ignore").strip().split()

        # sanity checks
        if len(res) != 4:
            raise Exception("Unexpected data after HDR header.")


        if res[0] not in ("-Y", "+Y") or res[2] not in ("-X", "+X"):
            raise Exception("Doesnt contain valid HDR resolution info.")

        #gets hdr width and height can be in value from 1 to 65535
        hdr_height = int(res[1])
        hdr_width = int(res[3])

        # flip flags for vertical and horizontal flip based on + or - in resolution line
        flip_y = (res[0] == "+Y")
        flip_x = (res[2] == "-X")

        # allocate data array
        data = np.zeros((hdr_height, hdr_width, 3), dtype=np.float32)

        # scan each line of height
        for y in range(hdr_height):
            # read scanline header every time (4 bytes) starting with 2, 2
            scan_head = f.read(4)

            # sanity checks
            if len(scan_head) != 4:
                raise Exception("Header too short for scanline.")

            # must be RLE encoded
            if scan_head[0] != 2 or scan_head[1] != 2:
                raise Exception("HDR scanline not RLE encoded.")

            # second two bytes are width high byte, low byte (should match hdr_width)
            w_hi, w_lo = scan_head[2], scan_head[3]

            # sanity check width match
            if (w_hi << 8 | w_lo) != hdr_width:
                raise Exception("HDR scanline width mismatch.")

            # check all four channels (R, G, B, E) and decode each one
            chan = [np.zeros(hdr_width, dtype=np.uint8) for _ in range(4)] # for r, g, b, e

            #hdr stores pixel = (R/256, G/256, B/256) * 2^(E-128) in 4 channels
            # read each channel
            for c in range(4):
                x = 0
                # decode until full width
                while x < hdr_width:

                    # read count byte
                    count = f.read(1)
                    if not count:
                        raise Exception("Could not read count byte.")

                    # get count value (0-255) and check for num_to_read or literal
                    count = count[0]
                    if count > 128:
                        # 128-255 is a num_to_read so we read one value and repeat it count-128 times
                        num_to_read = count - 128
                        val_b = f.read(1) # read the value what we repeat
                        if not val_b:
                            raise Exception("Unexpected EOF in num_to_read.")
                        chan[c][x:x+num_to_read] = val_b[0] # from x to x+num_to_read we set the values
                        x += num_to_read
                    else:
                        # 0-128 is a literal, so we read count values directly into the channel
                        num_to_read = count # number of literal values to read
                        vals = f.read(num_to_read)
                        if len(vals) != num_to_read:
                            raise Exception("Unexpected EOF in literal.")
                        chan[c][x:x+num_to_read] = np.frombuffer(vals, dtype=np.uint8)
                        x += num_to_read

            # save one scanline of pixels to data array as float32
            R = chan[0].astype(np.float32)
            G = chan[1].astype(np.float32)
            B = chan[2].astype(np.float32)
            E = chan[3].astype(np.float32)

            # convert from RGBE to float32 linear RGB
            mask = (E > 0) # avoid invalid ldexp for zero exponent
            scale = np.zeros_like(E, dtype=np.float32) # default scale is 0

            scale[mask] = np.ldexp(1.0, (E[mask] - 136).astype(np.int32)) # counts how many times to multiply by 2^(E-128)/256 = 2^(E-136) to get final scale for R,G,B
            rgb_row = np.stack([R*scale, G*scale, B*scale], axis=-1) # transform to RGB float32 row (H x 3, float32)

            # handle flipping if needed
            correct_y = hdr_height - 1 - y if flip_y else y

            # handle horizontal flip if needed
            if flip_x:
                rgb_row = rgb_row[::-1, :]
            data[correct_y, :, :] = rgb_row

        return data


class SkyboxHDR:
    """
    Create a skybox from an HDR image file and can sample colors based on 3D direction vectors.
    """
    def __init__(self, path: str,  yaw_deg: float = 90): #todo handle rotation after moove to scene

        arr = hdr_to_ndarray(path)
        self.data = arr
        # image dimensions height, width
        self.h, self.w = arr.shape[:2]
        # yaw rotation in radians
        self.yaw = math.radians(yaw_deg)

    def _dir_to_uv(self, direction: Vec3) -> tuple[float, float]:
        """
        Convert a 3D direction vector to UV coordinates on the skybox.
        :param direction: Direction vector
        :return: (u, v) coordinates in [0, 1] range
        """
        direction = direction.normalize_ip()
        x,y,z = direction.x, direction.y, direction.z

        # apply yaw rotation around Y axis to direction vector sy = sin(yaw), cy = cos(yaw)
        cos_yaw = math.sin(self.yaw)
        sin_yaw = math.cos(self.yaw)

        # rotate direction vector
        x_rotated =  cos_yaw * x + sin_yaw * z
        z_rotated = -sin_yaw * x + cos_yaw * z
        y_rotated = max(-1.0, min(1.0, y))

        # convert to spherical coordinates
        u = 0.5 + math.atan2(z_rotated, x_rotated) / (2.0 * math.pi)
        v = 0.5 - math.asin(y_rotated) / math.pi

        # wrap u to [0, 1]
        u = u % 1.0 # can be negative or >1 then wraps around
        v = max(0.0, min(1.0, v)) # clamp v to [0, 1]
        return u, v

    def color_from_dir(self, d: Vec3) -> Color:
        # get (u, v) coordinates from direction
        u, v = self._dir_to_uv(d.normalize_ip())

        # float pixel coordinates
        float_x = u * (self.w - 1)
        float_y = v * (self.h - 1)

        # bilinear interpolation of the four nearest pixels for smooth sampling
        x0 = int(float_x)
        x1 = min(x0 + 1, self.w - 1)
        y0 = int(float_y)
        y1 = min(y0 + 1, self.h - 1)

        # fractional part for interpolation weights in x and y directions [0, 1]
        tx = float_x - x0
        ty = float_y - y0

        # get the four pixel colors
        c00 = self.data[y0, x0]
        c10 = self.data[y0, x1]
        c01 = self.data[y1, x0]
        c11 = self.data[y1, x1]

        # interpolate color from four pixels and return as Color
        c0 = (1 - tx) * c00 + tx * c10
        c1 = (1 - tx) * c01 + tx * c11
        c  = (1 - ty) * c0  + ty * c1

        return Color(float(c[0]), float(c[1]), float(c[2]))

    def rotate_skybox(self, yaw_deg: float) -> None:
        """
        Rotate the skybox by a given yaw angle in degrees.
        :param yaw_deg: Yaw angle in degrees
        :return: None
        """
        self.yaw = math.radians(yaw_deg)