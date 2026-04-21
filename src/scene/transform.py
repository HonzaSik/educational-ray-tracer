from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from src.math import Vector

@dataclass
class Transform:
    """
    Represents an affine transformation with its matrix and cached inverse.
    """
    matrix: np.ndarray        # 4x4 matrix representing the transformation
    inverse: np.ndarray       # inverse of the matrix for transforming rays and points back to local space
    inverse_T: np.ndarray     # inverse transpose for transforming normals

    @staticmethod
    def identity():
        """
        Create an identity transformation.
        :return: Transform instance representing the identity transformation
        """
        identity_matrix = np.eye(4)
        return Transform(
            matrix=identity_matrix,
            inverse=identity_matrix,
            inverse_T=identity_matrix
        )

    @staticmethod
    def translate(x: float, y: float, z: float) -> Transform:
        """
        Create a translation transformation.
        :param x: translation along x-axis
        :param y: translation along y-axis
        :param z: translation along z-axis
        :return: Transform instance representing the translation
        """
        matrix = np.eye(4)
        matrix[:3, 3] = [x, y, z]

        matrix_inv = np.eye(4)
        matrix_inv[:3, 3] = [-x, -y, -z]

        return Transform(matrix, matrix_inv, matrix_inv.T)

    @staticmethod
    def scale(scale_x: float, scale_y: float, scale_z: float) -> Transform:
        """
        Create a scaling transformation.
        :param scale_x: scaling factor along x-axis
        :param scale_y: scaling factor along y-axis
        :param scale_z: scaling factor along z-axis
        :return: Transform instance representing the scaling
        """
        if scale_x == 0 or scale_y == 0 or scale_z == 0:
            raise ValueError("Scaling factors must be non-zero to avoid singular transformation.")

        matrix = np.diag([scale_x, scale_y, scale_z, 1])
        matrix_inv = np.diag([1 / scale_x, 1 / scale_y, 1 / scale_z, 1])

        return Transform(matrix, matrix_inv, matrix_inv.T)

    @staticmethod
    def rotate_y(angle_degrees: float) -> Transform:
        """
        Create a rotation transformation around the Y-axis.
        :param angle_degrees: rotation angle in degrees
        :return: Transform instance representing the rotation
        """
        radians = np.radians(angle_degrees)
        cos, sin = np.cos(radians), np.sin(radians)

        matrix = np.array([
            [cos, 0, sin, 0],
            [0, 1, 0, 0],
            [-sin, 0, cos, 0],
            [0, 0, 0, 1],
        ])

        matrix_inv = matrix.T

        return Transform(matrix, matrix_inv, matrix_inv.T)

    @staticmethod
    def rotate_x(angle_degrees: float) -> Transform:
        """
        Create a rotation transformation around the X-axis.
        :param angle_degrees: rotation angle in degrees
        :return: Transform instance representing the rotation
        """
        radians = np.radians(angle_degrees)
        cos, sin = np.cos(radians), np.sin(radians)

        matrix = np.array([
            [1, 0, 0, 0],
            [0, cos, -sin, 0],
            [0, sin, cos, 0],
            [0, 0, 0, 1],
        ])

        matrix_inv = matrix.T

        return Transform(matrix, matrix_inv, matrix_inv.T)

    @staticmethod
    def rotate_z(angle_degrees: float) -> Transform:
        """
        Create a rotation transformation around the Z-axis.
        :param angle_degrees: rotation angle in degrees
        :return: Transform instance representing the rotation
        """
        radians = np.radians(angle_degrees)
        cos, sin = np.cos(radians), np.sin(radians)

        matrix = np.array([
            [cos, -sin, 0, 0],
            [sin, cos, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ])

        matrix_inv = matrix.T

        return Transform(matrix, matrix_inv, matrix_inv.T)

    def combine(self, other: Transform) -> Transform:
        """
        Apply another transformation on top of this one by matrix multiplication.
        The resulting transformation is equivalent to first applying 'other' and then 'self'.
        """
        matrix = other.matrix @ self.matrix
        matrix_inv = self.inverse @ other.inverse
        return Transform(matrix, matrix_inv, matrix_inv.T)


def transform_normal(matrix_inv_T: np.ndarray, n: Vector) -> Vector:
    """
    Transform a normal vector using the inverse transpose of the transformation matrix.
    This is necessary to ensure that the normal remains perpendicular to the surface after transformations that include non-uniform scaling.
    """

    v = np.array([n.x, n.y, n.z, 0.0], dtype=float)  # w=0 for direction
    r = matrix_inv_T @ v
    return Vector(float(r[0]), float(r[1]), float(r[2])).normalize()