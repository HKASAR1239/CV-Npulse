# Shape Detector – Point-Cloud Primitive Recognition  
Detect **spheres**, **cylinders** and **cuboids/tablets** from PLY files or from an Intel® RealSense™ D435i depth-camera stream.

<p align="center">
  <img src="docs/demo.gif" width="550" alt="Live demo">
</p>

---

## ✨ Features
| Capability | Details |
|------------|---------|
| **Offline files** | Reads `.ply`, `.pcd`, `.xyz`, … with [Open3D] |
| **Live capture** | Single-frame grab from D435i via `pyrealsense2` |
| **Robust detection** | Oriented bounding box *+* lightweight RANSAC checks |
| **Cross-platform** | macOS/Linux (files) & Windows VM (camera) |
| **Lean dependencies** | `open3d`, `numpy` – that’s all (plus `pyrealsense2` if you need live) |

---

## 🗂 Folder layout
```
GeometrySelection/
│
├─ main.py                # CLI entry-point
├─ requirements.txt
├─ README.md
│
└─ shape_detector/        # Python package
   ├─ io.py               # RealSense & file I/O
   ├─ ransac.py           # mini-RANSAC fits (sphere, cylinder)
   ├─ detect.py           # detection logic
   └─ visualize.py        # Open3D viewer helpers
```

---

## 🚀 Quick start

### 1. Clone & install (virtual-env recommended)
```bash
python3 -m venv venv               # create environment
source venv/bin/activate           # macOS/Linux
# .\venv\Scripts\activate          # Windows
pip install -r requirements.txt
```
> **Live capture?**  
> `pip install pyrealsense2` (official Python Wheel).

### 2. Detect a PLY file
```bash
python main.py --input samples/vase.ply --visualize
# -> Detected shape: cylindrical
```

### 3. One-shot capture from RealSense
```bash
python main.py --live --visualize
```

---

## 🧠 Algorithm in a nutshell

1. **Down-sample** the cloud (`voxel_down_sample`) for speed.  
2. Compute an **Oriented Bounding Box** (PCA).  
3. Use box **extents** to generate shape hypotheses:  
   * spheres → three similar axes  
   * cylinders → two similar (radius) + one longer (height)  
4. **Confirm** the best hypothesis with a light RANSAC fit.  
5. Display the cloud, OBB (red wire-frame) and coordinate frame (XYZ).

Thresholds (`detect.py`) are tuned for everyday objects but can be adapted easily.

---

## ⚙️ Tuning

| Parameter (in `detect.py`) | Effect |
|----------------------------|--------|
| `vox` (down-sample)        | ↑ speed / ↓ detail |
| `iso_thr`                  | tolerance to accept sphere axes equality |
| `cyl_thr`                  | tolerance between the two radii of a cylinder |
| `length_ratio`             | min height-to-radius ratio for cylinders |
| `inlier_ratio` thresholds  | how strict the RANSAC confirmation is |
| `distance_threshold`       | absolute RANSAC distance tolerance |

---

## 📚 References
* **Open3D**: [open3d.org] – the backbone for point-cloud processing & visualisation.  
* **Intel RealSense SDK**: `pyrealsense2` for Python binding.

---

## 📝 License
MIT – do whatever you want, but give credit.  
Contributions & issues are welcome – feel free to open a PR!

---
## Authors
Darius Giannoli & Gabriel Taieb
