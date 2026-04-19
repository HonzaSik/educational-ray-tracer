# introduction to series of notebooks

---

In this series of notebooks, we will explore ray-tracing from scratch to building a simple Whited style ray-tracer. We will start with the basics of ray-tracing, including how camera works, how to generate rays, and how to intersect rays with objects. We will then move on to more advanced topics such as shading, lighting, and materials. Finally, we will build a simple ray-tracer that can render a scene with mathematicly defined objects and materials using the techniques we have learned and introducing some more advanced techniques like normal perturbation and procedural textures.
Some things are simplified and not physicly accurate, but the goal is to understand the basic principles pipeline of ray-tracing and how to implement it in code.

Whrough the series try to experiment with the code and try to implement your own features because that is the best way to learn and understand the concepts and yupiter notebooks are great for that.

Some thinks to keep in mind:
- We will be using Python for the implementation, but the concepts can be applied to any programming language.
- In the notebooks, we will be using pickle to save and load things we already created. Theese pickle files should not be added by me to the repository because the security of theese files cannot be guaranteed and you will need to generate them yourself by running the code in the notebooks. If you want to share your generated files with others, you can do so by sharing the code that generates them instead of sharing the pickle files directly.
- The code in the notebooks is not optimized for performance, but rather for clarity and understanding of the concepts. The goal is to understand how ray-tracing works and how to implement it, not to create a fast ray-tracer.

## Cheat sheet for the series how to use this library:

#### Importing from the library:
- `from src import *` to import all the necessary classes and functions.
- `from src.internals import *` to import the internals

---
# Configuration Classes

### `RenderConfig`

Controls the main rendering quality and recursion settings.

| Parameter | Type | Default | Description |
|---|---|---:|---|
| `resolution` | `Resolution` | `Resolution.R360p` | Output image resolution. Can use a predefined resolution or a custom one. |
| `samples_per_pixel` | `int` | `1` | Number of samples per pixel. Higher values improve anti-aliasing and noise reduction, but increase render time. |
| `max_depth` | `int` | `5` | Maximum recursion depth for secondary rays such as reflections and refractions. |

Example:

```
RenderConfig(
    resolution=Resolution.R360p,
    samples_per_pixel=1,
    max_depth=5,
)
```

### `PreviewConfig`

Controls how rendering progress is displayed.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `progress_display` | `ProgressDisplay` | `ProgressDisplay.NONE` | Chooses the progress display mode. |
| `refresh_interval_rows` | `int` | `10` | Number of rendered rows between preview updates. |
| `fill_missing_rows` | `bool` | `True` | Fills not-yet-rendered rows in the preview. |
| `show_status` | `bool` | `True` | Shows extra rendering status information. |
| `border` | `str` | `"1px solid #ddd"` | Border style for image preview output. |

Example:

```python
PreviewConfig(
    progress_display=ProgressDisplay.TQDM_IMAGE_PREVIEW,
    refresh_interval_rows=10,
    fill_missing_rows=True,
    show_status=True,
    border="1px solid #ddd",
)
```


### `PostProcessConfig`

Controls post-processing after rendering.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `enabled` | `bool` | `False` | Enables or disables post-processing. |
| `scale_factor` | `int` | `1` | Scales the final image by the given factor. |

Example:

```python
PostProcessConfig(
    enabled=False,
    scale_factor=1,
)
```

### `ProgressDisplay`

Available progress display modes.

| Mode | Value | Description |
|---|---|---|
| `NONE` | `0` | No progress output. |
| `TQDM_CONSOLE` | `1` | Progress output in the console. |
| `TQDM_BAR` | `2` | Standard tqdm progress bar. |
| `TQDM_IMAGE_PREVIEW` | `3` | Live image preview during rendering. |

Example:

```python
ProgressDisplay.TQDM_IMAGE_PREVIEW