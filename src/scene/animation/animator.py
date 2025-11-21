from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.render.resolution import Resolution
from src.math.vector import Vector
from src.shading.shader_model import ShadingModel
from src.scene import Scene
from src.scene.camera import Camera
from .ease import linear, ease_in_out, EaseType
from src.math.vertex import Vertex


@dataclass
class AnimationSetup:
    """
    Defines camera animation parameters.

    move_from: Starting position for camera movement.
    move_to: Ending position for camera movement.
    move_start_delay: Delay before movement starts (seconds).
    move_duration: Duration of camera movement (seconds).

    rotate_axis: Axis of rotation for camera.
    rotate_angle_deg: Total rotation angle in degrees.
    rotate_start_delay: Delay before rotation starts (seconds).
    rotate_duration: Duration of camera rotation (seconds).

    zoom_from: Starting field of view (degrees).
    zoom_to: Ending field of view (degrees).
    zoom_start_delay: Delay before zoom starts (seconds).
    zoom_duration: Duration of camera zoom (seconds).
    """
    move_from: Vertex | None = None
    move_to: Vertex | None = None
    move_start_delay: float = 0.0
    move_duration: float | None = None

    rotate_axis: Vector | None = None
    rotate_angle_deg: float | None = None
    rotate_start_delay: float = 0.0
    rotate_duration: float | None = None

    zoom_from: float | None = None
    zoom_to: float | None = None
    zoom_start_delay: float = 0.0
    zoom_duration: float | None = None


@dataclass
class Animator:
    """
    Handles animation setup and frame generation.
    """
    animation_setup: AnimationSetup = None
    animation_fps: int = 24 #todo move to QualityPreset
    animation_length_seconds: float = 2.0 #todo move to QualityPreset
    animation_resolution: Resolution = Resolution.R144p #todo move to QualityPreset

    _total_frames: int = 0
    _frame_duration: float = 0.0

    def __post_init__(self):
        if self.animation_setup is None:
            self.animation_setup = AnimationSetup()
        self._total_frames = self.get_total_frames()

    def get_total_frames(self) -> int:
        if self._total_frames == 0:
            self._total_frames = int(self.animation_length_seconds * self.animation_fps)
        return self._total_frames

    def get_frame_duration(self) -> float:
        self._frame_duration = 1.0 / self.animation_fps
        return self._frame_duration

    def _ease_apply(self, t: float, ease: EaseType) -> float:
        if ease == EaseType.LINEAR:
            return linear(t)
        elif ease == EaseType.EASE_IN_OUT:
            return ease_in_out(t)
        return t
    #todo add more easing functions if needed in ease.py and here _apply_ease mb move to ease.py

    def create_png_sequence(
        self,
        shader: ShadingModel | None = None,
        scene: Scene | None = None,
        folder: Path | str | None = None,
        ease: EaseType = EaseType.LINEAR,
    ) -> list[Path]:
        """
        Renders the animation frames to PNG files.
        :param ease: Easing type to use for transitions.
        :param shader: Optional shader model to use for rendering.
        :param scene: Scene to render.
        :param folder: Folder to save the frames. If None, defaults to "./animation_frames"
        :return: List of paths to the rendered frame PNG files.
        """

        #validation of inputs
        if scene is None:
            raise ValueError("Scene must be provided for animation rendering.")
        if self.animation_setup is None:
            raise ValueError("animation_setup must be set before calling animate_to_png().")

        # calate other params and sets animation settings
        total_frames = self.get_total_frames()
        frame_duration = self.get_frame_duration()
        scene.set_camera_resolution(self.animation_resolution)
        cam: Camera = scene.camera
        last_angle_deg: float = 0.0
        frames: list[Path] = []

        # folder management
        if folder is None:
            folder = Path("./animation_frames")
        elif not isinstance(folder, Path):
            folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)

        for frame_i in range(total_frames):
            current_time = frame_i * frame_duration

            print(f"Rendering frame {frame_i + 1}/{total_frames}")
            print(
                f"At time {current_time:.2f}s of {self.animation_length_seconds:.2f}s "
                f"- frame duration {frame_duration:.4f}s - Percent: {((frame_i + 1) / total_frames) * 100:.2f}%"
            )

            # move camera
            if (
                self.animation_setup.move_from is not None
                and self.animation_setup.move_to is not None
                and self.animation_setup.move_duration is not None
                and self.animation_setup.move_duration > 0.0
            ):
                start = self.animation_setup.move_start_delay
                duration = self.animation_setup.move_duration
                if start <= current_time <= start + duration:
                    t = (current_time - start) / duration  # 0-1 time normalized
                    t_eased = self._ease_apply(t, ease) # apply easing function to t
                    new_position = self.animation_setup.move_from.lerp(
                        self.animation_setup.move_to, t_eased # linear interpolation between from and to
                    )
                    cam.origin = new_position #todo update vec3/vertex/vector mismatch


            rotate_duration = self.animation_setup.rotate_duration
            # rotate camera
            if (
                self.animation_setup.rotate_axis is not None
                and self.animation_setup.rotate_angle_deg is not None
                and rotate_duration is not None
                and rotate_duration > 0.0
            ):
                start = self.animation_setup.rotate_start_delay
                duration = rotate_duration

                if start <= current_time <= start + duration:
                    t = (current_time - start) / duration # 0-1 time normalized
                    t_eased = self._ease_apply(t, ease)

                    total_angle = self.animation_setup.rotate_angle_deg # total rotation angle in degrees
                    target_angle_deg = total_angle * t_eased # target angle at current time

                    delta_angle_deg = target_angle_deg - last_angle_deg # change in angle since last frame
                    if abs(delta_angle_deg) > 1e-6: # if there is almost no change, skip rotation
                        cam.rotate_around_axis(self.animation_setup.rotate_axis, delta_angle_deg)
                    last_angle_deg = target_angle_deg # for next frame

            # zoom camera
            if (
                self.animation_setup.zoom_from is not None
                and self.animation_setup.zoom_to is not None
                and self.animation_setup.zoom_duration is not None
                and self.animation_setup.zoom_duration > 0.0
            ):
                start = self.animation_setup.zoom_start_delay
                duration = self.animation_setup.zoom_duration
                if start <= current_time <= start + duration:
                    t = (current_time - start) / duration # 0-1 time normalized
                    t_eased = self._ease_apply(t, ease) # apply easing function to t
                    new_fov = self.animation_setup.zoom_from + (
                        self.animation_setup.zoom_to - self.animation_setup.zoom_from # linear interpolation of fov
                    ) * t_eased
                    cam.fov = new_fov
                    cam.__post_init__() # recalculate camera parameters after fov change

            # reset camera in scene
            scene.set_camera(cam)

            # render individual frame as PNG by sequence - frame_0000.png, frame_0001.png, ...
            path = folder / f"frame_{frame_i:04d}.png"
            spp, max_depth = (1, 5) #todo remove hardcode later add to QualityPreset or params

            scene.render_multithreaded(
                samples_per_pixel=spp,
                max_depth=max_depth,
                shading_model=shader,
                image_png_path=str(path.resolve()),
            )

            frames.append(path)
        return frames

    def animate_to_mp4(
        self,
        shader: ShadingModel | None = None,
        scene: Scene | None = None,
        output_path: Path | str | None = None,
        ease: EaseType = EaseType.LINEAR,
    ) -> Path:
        """
        Renders the animation to an MP4 file.
        :param ease: Easing type to use for transitions.
        :param shader: Optional shader model to use for rendering.
        :param scene: Scene to render.
        :param output_path: Path to save the MP4 file. If None, defaults to "./animatons/animation.mp4"
        :return: Path to the rendered MP4 file.
        """
        from src.io.video import frames_to_mp4

        if output_path is None:
            output_path = Path("./animatons/animation.mp4")
        elif not isinstance(output_path, Path):
            output_path = Path(output_path)

        frames_folder = Path("./animation_frames")
        frames = self.create_png_sequence(
            shader=shader,
            scene=scene,
            folder=frames_folder,
            ease=ease,
        )

        mp4_path = frames_to_mp4(
            frames,
            output_path,
            fps=self.animation_fps
        )

        print(
            f"----------------------- Animation MP4 saved to: {mp4_path.resolve()} -------------------------------"
        )

        return mp4_path
