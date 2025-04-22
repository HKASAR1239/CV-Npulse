# ArUco Object‑Selection Demo

<p align="center">
  <!-- Replace preview.gif with an actual GIF or screenshot of your app -->
  <img src="doc/preview.gif" width="600" alt="Screen capture of the selection demo" />
</p>

> **Goal** – Point your finger -here we use a ruler- (with an **ArUco ID 10** marker) at one among many objects (with **ArUco IDs**) and the application instantly tells you which object is selected.

---

## 📽 Demo video

![demo](../docs/demo_obj_select.mp4?raw=true)



---

## Hardware & materials

| Item | Details |
|------|---------|
| **Camera** | Any 720 p+ webcam works. |
| **Ruler / Pointer** | Any stick ‑‑ glue **ArUco ID 10** on the pointing end. |
| **Objects** | n objects with markers **IDs 1 → n** . |
| **Printer** | To print the markers (4×4 dictionary). |
| Good lighting | Minimises false detections. |

---

## Quick start

```bash
# 1  Clone & prepare virtual‑env
source aruco_env/bin/activate  # Windows : aruco_env\Scripts\activate
pip install --upgrade pip
pip install opencv-python opencv-contrib-python numpy

# 2  Run the live demo
python main.py                # opens a window with live video
```
---

## File structure

```
.
├── aruco_env        # venv with necessary dependencies
├── main.py          # real‑time selection logic (no camera calibration)
└── README.md        # you are here
```

---

## How it works (TL;DR)

1. **Detect all markers** every frame with OpenCV’s `cv2.aruco.detectMarkers()`.
2. Compute the **centre** `O` and **X‑axis direction** `u` of the ruler marker 10.
3. For every object marker `i` (ID 1‑n):
   * project its centre vector on `u` → distance **along** the ray.
   * compute the perpendicular distance → **angle** (tanθ).
4. Keep objects with angle `< ±12 °`, pick the **closest** along the ray ⇒ selected.
5. **Hysteresis (2 frames)** keeps the label stable if the ruler jiggles.

See comments inside `main.py` for full maths.

---

## Parameters you can tweak

| Variable | Default | Effect |
|----------|---------|--------|
| `CONE_DEG` | `12` | Width of the selection cone (degrees). |
| `HOLD_FRAMES` | `2` | Frames that a new object must be seen before switch. Lower = more reactive. |
| `DIR_THR_DEG` | `4` | If the ruler rotates > this angle, we skip `HOLD_FRAMES` and switch instantly. |

---

## Troubleshooting

* **Markers detected but nothing selected** : check that marker 10 is *not* listed in `OBJ_IDS`, adjust `CONE_DEG` (wider) or move the camera closer.
* **Selection flickers** : raise `HOLD_FRAMES` or lower `DIR_THR_DEG`.

---

## License

MIT

---

### Authors

Gabriel Taïeb and Darius Giannoli – *Feel free to open an issue or pull‑request!*

