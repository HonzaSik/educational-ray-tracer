from dataclasses import dataclass, field
from typing import Tuple, List

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from src import Camera
from src.geometry.geometry_hit import GeometryHit
from src.geometry.ray import Ray
from src.scene.light import LightType, Light
from src.scene.object import Object
from src.math import Vertex, Vector
from src.geometry.ray import Ray
from src.scene.surface_interaction import SurfaceInteraction
from src.shading.helpers import light_dir_dist, shadow_trace


def to_matplotlib_coords(x: float, y: float, z: float) -> Tuple[float, float, float]:
    """
    Converts coordinates from our 3D space (X right, Y up, Z forward) to matplotlib's 3D coordinate system (X right, Y forward, Z up)
    """
    return x, -z, y


def vector_to_matplotlib(vec):
    """Convert a Vector object to matplotlib coordinates"""
    return to_matplotlib_coords(vec.x, vec.y, vec.z)


def vertex_to_matplotlib(vert):
    """Convert a Vertex object to matplotlib coordinates"""
    return to_matplotlib_coords(vert.x, vert.y, vert.z)


def calculate_base_corners(camera: Camera):
    bl_w = camera.origin + (camera.right * (-camera.half_width) + camera.up * (-camera.half_height) + camera.forward)
    br_w = camera.origin + (camera.right * ( camera.half_width) + camera.up * (-camera.half_height) + camera.forward)
    tr_w = camera.origin + (camera.right * ( camera.half_width) + camera.up * ( camera.half_height) + camera.forward)
    tl_w = camera.origin + (camera.right * (-camera.half_width) + camera.up * ( camera.half_height) + camera.forward)

    bl = vertex_to_matplotlib(bl_w)
    br = vertex_to_matplotlib(br_w)
    tr = vertex_to_matplotlib(tr_w)
    tl = vertex_to_matplotlib(tl_w)

    return [bl, br, tr, tl]


@dataclass
class Visualizer:
    """
    Data visualizer for iupyter notebooks. Provides methods to visualize various data types such as axes, rays, geometry hits, etc. in a 3D plot.
    """
    ax : Axes = field(default_factory=lambda: None)
    plot : plt = field(default_factory=lambda: plt)
    fig : Figure = field(default_factory=lambda: None)

    view_elev: float = 20
    view_azim: float = -60
    view_roll: float = 0


    def create_empty_scene(self,
                           size=10.0,
                           figsize=(10, 10),
                           show_axes_labels=False,
                           show_arrows=True,
                           background_color='whitesmoke',
                           show_grid=True,
                           show_axes=True,
                           show_xyz_labels=True,
                           view_elev=20, view_azim=-60, view_roll=0
                           ):
        """
        Creates an empty 3D scene with optional axes, arrows, grid and labels for visualization purposes.
        You can use this function to create empty scenes before plotting different camera positions, rays, objects etc.
        It helps to visualize the coordinate system and how different elements are positioned in 3D space.
        Returns Fig and Axes objects that you can use for further plotting but also stores them in the Visualizer instance for later use

        Parameters:
            size: float - the half-length of the axes (the axes will go from -size to +size)
            figsize: tuple - size of the matplotlib figure
            show_axes_labels: bool - whether to show +X, -X, +Y, -Y, +Z, -Z labels at the ends of the axes
            show_arrows: bool - whether to show arrows at the ends of the axes
            background_color: str - color of the background
            show_grid: bool - whether to show grid lines
            show_axes: bool - whether to show the axes lines
            show_xyz_labels: bool - whether to label the axes with "X axis", "Y axis", "Z axis" (note: Y and Z are swapped in matplotlib)
            view_elev: float - elevation angle for 3D view
            view_azim: float - azimuth angle for 3D view
            view_roll: float - roll angle for 3D view
        Returns:
            fig: the created matplotlib figure
            ax: the created matplotlib 3D axes
        """

        fig = self.plot.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection="3d")
        ax.set_facecolor(background_color)
        try:
            ax.view_init(elev=view_elev, azim=view_azim, roll=view_roll)
        except TypeError:
            ax.view_init(elev=view_elev, azim=view_azim)

        self.view_elev = view_elev
        self.view_azim = view_azim
        self.view_roll = view_roll

        axis_colors = {
            'x': 'red',
            'y': 'green',
            'z': 'blue'
        }

        points = int(size) * 2
        oppacity = 0.4

        if show_axes:
            # plot points along each axis to create a measurable scale
            for i in range(points):
                x_start = -size + (2 * size * i / points)
                x_end = -size + (2 * size * (i + 1) / points)
                ax.plot([x_start, x_end], [0, 0], [0, 0],
                        color=axis_colors['x'], linewidth=3, alpha=oppacity,
                        marker='s', markersize=2, markevery=[0, 1])

                z_start = -size + (2 * size * i / points)
                z_end = -size + (2 * size * (i + 1) / points)
                ax.plot([0, 0], [0, 0], [z_start, z_end],
                        color=axis_colors['y'], linewidth=3, alpha=oppacity,
                        marker='s', markersize=2, markevery=[0, 1])

                y_start = -size + (2 * size * i / points)
                y_end = -size + (2 * size * (i + 1) / points)
                ax.plot([0, 0], [y_start, y_end], [0, 0],
                        color=axis_colors['z'], linewidth=3, alpha=oppacity,
                        marker='s', markersize=2, markevery=[0, 1])

        if show_arrows and show_axes:
            # add arrows at the ends of the axes to indicate positive direction
            arrow_scale = 0.3
            ax.quiver(size * (1 - arrow_scale), 0, 0, size * arrow_scale, 0, 0,
                      color=axis_colors['x'], arrow_length_ratio=0.4, linewidth=3, alpha=0.7)
            ax.quiver(0, 0, size * (1 - arrow_scale), 0, 0, size * arrow_scale,
                      color=axis_colors['y'], arrow_length_ratio=0.4, linewidth=3, alpha=0.7)
            ax.quiver(0, -size * (1 - arrow_scale), 0, 0, -size * arrow_scale, 0,
                      color=axis_colors['z'], arrow_length_ratio=0.4, linewidth=3, alpha=0.7)

        if show_axes_labels and show_axes:
            # add labels at the ends of the axes
            label_offset = 1.2
            label_bg = dict(fontsize=16, weight='bold',
                            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                                      alpha=0.7, edgecolor='gray'))

            ax.text(size * label_offset, 0, 0, "+X", color=axis_colors['x'],
                    ha="left", va="center", **label_bg)
            ax.text(-size * label_offset, 0, 0, "-X", color=axis_colors['x'],
                    ha="right", va="center", **label_bg)
            ax.text(0, 0, size * label_offset, "+Y", color=axis_colors['y'],
                    ha="center", va="bottom", **label_bg)
            ax.text(0, 0, -size * label_offset, "-Y", color=axis_colors['y'],
                    ha="center", va="top", **label_bg)
            ax.text(0, size * label_offset, 0, "-Z", color=axis_colors['z'],
                    ha="left", va="bottom", **label_bg)
            ax.text(0, -size * label_offset, 0, "+Z", color=axis_colors['z'],
                    ha="right", va="top", **label_bg)

        if show_grid:
            ax.grid(True, linestyle="--", alpha=0.4)
            ax.set_axisbelow(True)
        else:
            ax.grid(False)

        limit = size * 1.3
        # set limits and aspect ratio to make sure the scene is centered and not distorted
        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)
        ax.set_zlim(-limit, limit)
        # centered axes at the origin and make sure they have equal scaling
        ax.set_box_aspect([1, 1, 1])

        if show_xyz_labels:
            ax.set_xlabel("X axis", fontsize=12)
            ax.set_ylabel("Z axis", fontsize=12)
            ax.set_zlabel("Y axis", fontsize=12)

        # adjusted layout to prevent clipping of labels and title
        self.plot.tight_layout()

        self.fig = fig
        self.ax = ax

        return fig, ax

    def savefig(self, filename: str = "tmp.png", dpi: int = 300) -> None:
        """Save the current figure to a file.
            :param filename: Name of the output file (e.g., "output.png").
            :param dpi: Dots per inch (resolution) of the saved image.
        """
        if self.fig is not None:
            self.fig.savefig(filename, dpi=dpi)
        else:
            raise RuntimeError("No figure to save. Please create a scene first.")


    def show(self) -> None:
        """Display the current figure."""
        if self.fig is not None:
            self.plot.show()
        else:
            raise RuntimeError("No figure to show. Please create a scene first.")

    def plot_camera_position_and_orientation(self,
                                             camera: 'Camera',
                                             arrow_length=1,
                                             show_frustum=True,
                                             frustum_depth=2.0,
                                             show_camera_orientation=True,
                                             show_plane=False,
                                             show_plane_corners=False
                                             ):
        """
        plots camera position and orientation vectors (forward, up, right)
        Parameters:
            - ax: matplotlib 3D axis to plot on
            - camera: Camera object containing position and orientation information
            - arrow_length: how long the arrows representing the camera's direction vectors should be
            - show_frustum: whether to plot the camera frustum (view volume)
            - frustum_depth: depth to which the frustum should be plotted (if show_frustum is True)
        """

        cam_x, cam_y, cam_z = vertex_to_matplotlib(camera.origin)

        # Camera position marker
        self.ax.scatter(cam_x, cam_y, cam_z, color='red', s=150, alpha=0.9,
                   edgecolors='black', linewidths=2, zorder=30, label='Camera')

        # camera orientation vectors (forward, up, right)
        if show_camera_orientation:
            vectors = [
                (camera.direction.normalize(), 'blue', 1.0, 2, 'Forward'),
                (camera.up.normalize(), 'green', 1.0, 2, 'Up'),
                (camera.right.normalize(), 'orange', 1.0, 2, 'Right')
            ]

            for vec, color, scale, line_width, label in vectors:
                vx, vy, vz = vector_to_matplotlib(vec)
                self.ax.quiver(
                    cam_x, cam_y, cam_z,
                    vx * arrow_length,
                    vy * arrow_length,
                    vz * arrow_length,
                    color=color,
                    arrow_length_ratio=0.3,
                    linewidth=2,
                    alpha=0.95,
                    label=label
                )

        if show_plane:
            self.plot_image_plane(camera, show_plane_corners=show_plane_corners)

        if show_frustum:
            self.plot_frustum(camera, extended_depth=frustum_depth - 1.0)

        self.ax.legend(loc='upper right', fontsize=10)

    def plot_frustum(self, camera: Camera, extended_depth=5.0):
        """
        Plot camera frustum showing the view volume edges.

        Args:
            camera: Camera object
            extended_depth: depth to extend frustum to
        """
        cam_pos = vertex_to_matplotlib(camera.origin)

        bl, br, tr, tl = calculate_base_corners(camera)
        corners = [bl, br, tr, tl]
        edges = [(bl, br), (br, tr), (tr, tl), (tl, bl)]

        # Draw lines from camera to each corner of the image plane
        for corner in [bl, br, tr, tl]:
            self.ax.plot([cam_pos[0], corner[0]],
                    [cam_pos[1], corner[1]],
                    [cam_pos[2], corner[2]],
                    color='orange', linewidth=1.5, linestyle='--', alpha=0.6)

        for i, (start, end) in enumerate(edges):
            self.ax.plot([start[0], end[0]],
                         [start[1], end[1]],
                         [start[2], end[2]],
                         color='orange', linewidth=1.5, alpha=0.9, linestyle='--',
                         label='Projection Plane' if i == 0 else None)

        # Extend frustum to the specified depth
        extended_corners = []
        for corner in corners:
            dir_vec = np.array(corner) - np.array(cam_pos)
            dir_vec = dir_vec / np.linalg.norm(dir_vec)  # Normalize

            # Extend the corner along the direction vector
            ext_corner = np.array(corner) + dir_vec * extended_depth
            extended_corners.append(ext_corner)

        # Draw extended edges
        for corner, ext_corner in zip(corners, extended_corners):
            self.ax.plot([corner[0], ext_corner[0]],
                    [corner[1], ext_corner[1]],
                    [corner[2], ext_corner[2]],
                    color='orange', linewidth=1, linestyle=':', alpha=0.4)

        # Draw extended frame
        ext_bl, ext_br, ext_tr, ext_tl = extended_corners
        ext_edges = [
            (ext_bl, ext_br),
            (ext_br, ext_tr),
            (ext_tr, ext_tl),
            (ext_tl, ext_bl),
        ]

        for i, (start, end) in enumerate(ext_edges):
            self.ax.plot([start[0], end[0]],
                    [start[1], end[1]],
                    [start[2], end[2]],
                    color='orange',
                    linewidth=1.5,
                    alpha=0.4,
                    linestyle=':',
                    label='Extended Frustum' if i == 0 else None)

    def plot_image_plane(self, camera: Camera, show_plane_corners=False):
        """
        Plot the image plane rectangle with corner labels.

        Args:
            camera: Camera object
            show_plane_corners: whether to label the corners of the image plane with their (u,v) coordinates
        """


        corners = calculate_base_corners(camera)

        if show_plane_corners:
            labels = [
                "-1, -1",  # bottom-left
                "1, -1",  # bottom-right
                "1,  1",  # top-right
                "-1,  1",  # top-left
            ]
        else:
            labels = [""] * 4

        for i, (corner, label) in enumerate(zip(corners, labels)):
            self.ax.scatter(corner[0],
                       corner[1],
                       corner[2],
                       color='purple',
                       s=20,
                       zorder=5,
                       alpha=0.9,
                       label='Image Plane Corners' if i == 0 else None)

            self.ax.text(corner[0],
                    corner[1],
                    corner[2],
                    label,
                    color='purple',
                    fontsize=9,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                              alpha=0.7, edgecolor='gray'),
                    zorder=4,
                    horizontalalignment='center',
                    verticalalignment='center')

        # Draw filled plane
        verts = [corners]

        poly = Poly3DCollection(verts, alpha=0.2, facecolor='cyan',
                                edgecolor='orange', linewidth=2)
        self.ax.add_collection3d(poly)

    def set_title(self, title: str, fontsize: int = 12) -> None:
        """Set the title of the plot."""
        if self.fig is not None:
            self.ax.set_title(title, fontsize=fontsize, pad=20)
        else:
            raise RuntimeError("No figure to set title on. Please create a scene first.")


    def visualize_ray(self, ray: Ray, length=5.0, color='magenta', opacity=0.6, ended_by_hit_point : SurfaceInteraction | GeometryHit | None = None):
        """
        Visualizes a ray in the 3D scene by plotting a line from the ray's origin in the direction of the ray.
        Parameters:
            ax: matplotlib 3D axis to plot on
            ray: Ray object containing origin and direction
            length: how long the ray should be visualized (default is 5.0 units)
            color: color of the ray line (default is 'magenta')
        """

        if ended_by_hit_point is not None:
            length = min(length, ended_by_hit_point.dist)

        start = vertex_to_matplotlib(ray.origin)
        end_point = ray.origin + ray.direction * length
        end = vertex_to_matplotlib(end_point)

        self.ax.plot([start[0], end[0]],
                 [start[1], end[1]],
                 [start[2], end[2]],
                 color=color, linewidth=2, alpha=opacity)

    def visualize_intersections(self, ray: Ray, objects: List[Object], intersection_opacity=0.5, max_dist=100.0, intersection_size=20):
        """
        Plot simple representations of objects in the scene (e.g. spheres as points)

        Parameters:
        -----------
        ax : matplotlib 3D axes
        objects : list of Object
            The objects to plot (we will just plot their centers for simplicity)
        """
        for obj in objects:
            intersection_point = obj.geometry.intersect(ray)
            if intersection_point is not None and intersection_point.dist < max_dist:
                self.ax.scatter(*vertex_to_matplotlib(intersection_point.point),
                           color=obj.material.get_color(), s=intersection_size, alpha=0.5)

    def visualize_lights_positions(self, lights: List[Light]):
        for light in lights:
            if light.type == LightType.POINT:
                self.ax.scatter(*vertex_to_matplotlib(light.position), color='yellow', s=100, alpha=0.9, edgecolors='Orange',
                           linewidths=2, zorder=30, label='Point Light')


    def visualize_normal_at_hit_point(self, hit_point: 'SurfaceInteraction',
                                      length=0.3, color='cyan', alpha=0.9):
        if hit_point is None:
            return

        point = hit_point.geom.point
        normal = hit_point.normal

        p = np.array(vertex_to_matplotlib(point))
        n = np.array(vector_to_matplotlib(normal))  # normal is a vector, not a vertex

        self.ax.quiver(p[0], p[1], p[2],
                       n[0] * length, n[1] * length, n[2] * length,
                       color=color, arrow_length_ratio=0.3, linewidth=1.3,
                       alpha=alpha)

    def show_image_plane_point(self, camera: Camera, u: float, v: float,
                               color='purple', size=20, label='Image Plane Point'):
        """
        Shows a (u,v) coordinate on the actual camera image plane in 3D space.
        u, v should be in [-1, 1] range.
        """

        point_w = camera.origin + (
                camera.right * (u * camera.half_width) +
                camera.up * (v * camera.half_height) +
                camera.forward
        )

        p = vertex_to_matplotlib(point_w)
        self.ax.scatter(*p, color=color, s=size, alpha=0.9,
                        edgecolors='black', linewidths=2, zorder=20, label=label)

        self.ax.legend(loc='upper right', fontsize=10)

    def show_shadow_rays(self, hit: SurfaceInteraction, lights: List[Light], objects: List[Object], ray_length=5.0, color='gray', opacity=0.5):
        """
        Visualizes shadow rays from the hit point to each light source.
        Parameters:
            hit: SurfaceInteraction containing the hit point and normal
            lights: list of Light objects in the scene
            ray_length: how long the shadow rays should be visualized (default is 5.0 units)
            color: color of the shadow rays (default is 'gray')
            opacity: opacity of the shadow rays (default is 0.5)
        """
        if hit is None:
            return

        hit_point = hit.geom.point

        for light in lights:
            if light.type == LightType.AMBIENT:
                continue  # ambient light doesn't cast shadows

            light_dir, light_dist = light_dir_dist(hit, light)

            for obj in objects:
                shadow_hit = obj.geometry.intersect(Ray(origin=hit_point, direction=light_dir))
                if shadow_hit is not None and shadow_hit.dist < light_dist:
                    self.visualize_ray(Ray(origin=hit_point, direction=light_dir), length=shadow_hit.dist, color='black', opacity=opacity, ended_by_hit_point=shadow_hit)
                else:
                    self.visualize_ray(Ray(origin=hit_point, direction=light_dir), length=light_dist, color=color, opacity=opacity)
