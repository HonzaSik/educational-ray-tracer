from __future__ import annotations
from pathlib import Path
from typing import Sequence
import imageio as imageio


def frames_to_mp4(
        frames: Sequence[Path | str],
        output_path: Path | str,
        fps: int = 24,
) -> Path:
    """
    Takes a sequence of image frames and compiles them into an MP4 animatons file.
    :param frames: Sequence of file paths to image frames.
    :param output_path: Path to save the output MP4 file.
    :param fps: Frames per second for the output animatons.
    :return: Path to the created MP4 file.
    """
    if not frames:
        raise ValueError("frames_to_mp4: no frames provided")

    # Normalize and sort the frame paths (e.g. frame_0000.png ... frame_0123.png)
    frame_paths = [Path(f) for f in frames]
    frame_paths.sort(key=lambda p: p.name)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # It uses ffmpeg inside #todo how to do it without installing imageio
    with imageio.get_writer(
            output_path.as_posix(),
            fps=fps,
            codec="libx264",
    ) as writer:
        for frame in frame_paths:
            img = imageio.imread(frame.as_posix())
            writer.append_data(img)

    return output_path
