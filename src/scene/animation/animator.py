from pathlib import Path

from src.io.resolution import Resolution
from src.math.vector import Vector
from dataclasses import dataclass
from src.shading.shader_model import ShadingModel
from src.scene import Scene, QualityPreset, Resolution, ShadingModel, RenderMethod
from .ease import linear, ease_in_out, EaseType
from ... import Camera


@dataclass
class AnimationSetup:
    move_from: Vector | None = None
    move_to: Vector | None = None
    move_start_delay: float = 0.0  # in seconds
    move_duration: float | None = None  # in seconds

    rotate_axis: Vector | None = None
    rotate_angle_deg: float | None = None  # in degrees
    rotate_start_delay: float = 0.0  # in seconds
    rotate_duration: float | None = None  # in seconds

    zoom_from: float | None = None  # fov in degrees
    zoom_to: float | None = None  # fov in degrees
    zoom_start_delay: float = 0.0  # in seconds
    zoom_duration: float | None = None  # in seconds


@dataclass
class Animator:
    """
    Handles animation setup and frame generation.
    """
    animation_setup: AnimationSetup = None
    animation_fps: int = 24
    animation_length_seconds: float = 2.0
    animation_resolution: Resolution = Resolution.R144p

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

    def animate_to_png(
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
        :param folder: Folder to save the frames. If None, defaults to "./animation_frames
        :return: List of paths to the rendered frame PNG files.
        """
        frames: list[Path] = []
        total_frames = self.get_total_frames()
        frame_duration = self.get_frame_duration()

        scene.camera.resolution = self.animation_resolution

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
                f"- frame duration {frame_duration:.4f}s - Percent: {(frame_i / total_frames) * 100:.2f}%"
            )

            if scene is None:
                raise ValueError("Scene must be provided for animation rendering.")
            if shader is not None:
                scene.shader_model = shader

            # each frame, update camera based on animation setup
            cam: Camera = scene.camera

            if (
                self.animation_setup.move_from is not None
                and self.animation_setup.move_to is not None
                and self.animation_setup.move_duration is not None
            ):
                start = self.animation_setup.move_start_delay
                duration = self.animation_setup.move_duration
                if start <= current_time <= start + duration:
                    t = (current_time - start) / duration
                    if ease == EaseType.LINEAR:
                        t_eased = linear(t)
                    elif ease == EaseType.EASE_IN_OUT:
                        t_eased = ease_in_out(t)
                    else:
                        t_eased = t
                    new_position = self.animation_setup.move_from.lerp(
                        self.animation_setup.move_to, t_eased
                    )
                    cam.position = new_position

            if (
                self.animation_setup.rotate_axis is not None
                and self.animation_setup.rotate_angle_deg is not None
                and self.animation_setup.rotate_duration is not None
            ):
                start = self.animation_setup.rotate_start_delay
                duration = self.animation_setup.rotate_duration
                if start <= current_time <= start + duration:
                    t = (current_time - start) / duration
                    if ease == EaseType.LINEAR:
                        t_eased = linear(t)
                    elif ease == EaseType.EASE_IN_OUT:
                        t_eased = ease_in_out(t)
                    else:
                        t_eased = t
                    angle = self.animation_setup.rotate_angle_deg / duration * t_eased
                    cam.rotate_around_axis(self.animation_setup.rotate_axis, angle)

            if (
                self.animation_setup.zoom_from is not None
                and self.animation_setup.zoom_to is not None
                and self.animation_setup.zoom_duration is not None
            ):
                start = self.animation_setup.zoom_start_delay
                duration = self.animation_setup.zoom_duration
                if start <= current_time <= start + duration:
                    t = (current_time - start) / duration
                    if ease == EaseType.LINEAR:
                        t_eased = linear(t)
                    elif ease == EaseType.EASE_IN_OUT:
                        t_eased = ease_in_out(t)
                    else:
                        t_eased = t
                    new_fov = self.animation_setup.zoom_from + (
                        self.animation_setup.zoom_to - self.animation_setup.zoom_from
                    ) * t_eased
                    cam.fov = new_fov

            scene.set_camera(cam)

            path = folder / f"frame_{frame_i:04d}.png"
            frames.append(path)

            scene.render(
                quality=QualityPreset.ULTRA_LOW,
                render_method=RenderMethod.SHADOW_TRACE_MULTITHREADED,
                image_png_path=str(path.resolve()),
            )

        return frames
