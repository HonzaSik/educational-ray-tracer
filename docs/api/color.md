<p align="center">
  <img src="../examples/header.png" alt="Educational Ray Tracer" width="2560" />
</p>

<h1 align="center">Color</h1>

---

<p align="center">
  <b> Detailed Description </b>
</p>

---

``` python3
Color
```
- A class representing RGB colors used in materials and lighting. Inherits from `Vec3`.

``` python3
Color.custom_albedo(r: float, g: float, b: float)
```
- Create a custom color with specified red, green, and blue components.
- Returns a Color instance clamped between 0.0 and 1.0. 
- #todo missing 4th param - maybe implement vec4 as np array

``` python3
Color.custom_rgb(r: int, g: int, b: int)
```
- Create a custom color using RGB values in the range 0-255.
- Returns a Color instance with normalized RGB values. 

``` python3
Color.to_rgb8()
```
- Convert the color to RGB values in the range 0-255.

...

---
[example of usage](../../notebooks/complex_scene_creation/01_material.ipynb)

