# src/render/loops/progress.py
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple
import io
import numpy as np
from PIL import Image
import ipywidgets as widgets
from IPython.display import display
from tqdm import tqdm as tqdm_console
from tqdm.notebook import tqdm as tqdm_nb


class ProgressDisplay(Enum):
    NONE = 0
    TQDM_CONSOLE = 1
    TQDM_BAR = 2
    TQDM_IMAGE_PREVIEW = 3

@dataclass
class PreviewConfig:
    refresh_interval_rows: int = 10
    fill_missing_rows: bool = True
    show_status: bool = True
    border: str = "1px solid #ddd"


class ProgressUI:
    def __init__(self,
                 mode: ProgressDisplay,
                 width: int,
                 height: int,
                 preview: PreviewConfig | None = None) -> None:

        self.mode = mode
        self.width = width
        self.height = height
        self.preview = preview or PreviewConfig()
        self.progress_bar = None
        self.img_widget: widgets.Image | None = None
        self.status_widget: widgets.HTML | None = None


    def start(self, total_pixels: int) -> None:
        if self.mode == ProgressDisplay.TQDM_CONSOLE:
            self.progress_bar = tqdm_console(total=total_pixels, desc="Rendering", unit="px", leave=True)

        elif self.mode == ProgressDisplay.TQDM_BAR:
            self.progress_bar = tqdm_nb(total=total_pixels, desc="Rendering", unit="px", leave=True)

        if self.mode == ProgressDisplay.TQDM_IMAGE_PREVIEW:
            self.img_widget = widgets.Image(
                format="png",
                layout=widgets.Layout(
                    width=f"{self.width}px",
                    height=f"{self.height}px",
                    border=self.preview.border,
                ),
            )

            # Display the image and status
            image = [self.img_widget]

            # Status widget below the image as simple text
            if self.preview.show_status:
                self.status_widget = widgets.HTML(value="Starting…")
                image.append(self.status_widget)

            display(widgets.VBox(image))


    def update_pixel(self, n: int = 1) -> None:
        if self.progress_bar is not None:
            self.progress_bar.update(n)


    def update_row(self, pixels_u8: List[Tuple[int, int, int]], row: int) -> None:

        if self.img_widget is None:
            return

        width, height = self.width, self.height

        if self.preview.fill_missing_rows:
            flat = pixels_u8 + [(0, 0, 0)] * ((height - row) * width)
            arr = np.asarray(flat, dtype=np.uint8).reshape(height, width, 3)
        else:
            arr = np.asarray(pixels_u8, dtype=np.uint8).reshape(row, width, 3)

        img = Image.fromarray(arr)

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        self.img_widget.value = buffer.getvalue()

        if self.status_widget is not None:
            self.status_widget.value = f"Rendering - {row}/{height} rows"


    def update_end(self, pixels_flat_u8: List[Tuple[int, int, int]]) -> None:
        if self.progress_bar is not None:
            self.progress_bar.close()

        if self.img_widget is not None:
            width, height = self.width, self.height

            arr = np.asarray(pixels_flat_u8, dtype=np.uint8).reshape(height, width, 3)

            img = Image.fromarray(arr)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            self.img_widget.value = buf.getvalue()

            if self.status_widget is not None:
                self.status_widget.value = "Done."
