# RealSense Point‑Cloud Filtering Pipeline

> Clean, down‑sample, segment and normalise 3‑D point‑clouds captured with an **Intel RealSense D435i** (or any depth sensor producing standard PLY/PCD/XYZ files) using **Open3D**. The pipeline is cross‑platform (macOS ▸ Windows ▸ Raspberry Pi 5) and can be run offline on saved files or online on live camera streams.

---
## ✨  What the project does

1. **Acquisition & integrity checks**  — strip NaNs/invalid depth pixels.
2. **Noise & outlier filtering**  — Statistical Outlier Removal (SOR) + Radius Outlier Removal (ROR).
3. **Voxel grid down‑sampling**  — uniform density, smaller file size.
4. **Dominant plane removal**  — remove table/floor with RANSAC.
5. **ROI refinement**  — optional axis‑aligned crop + Euclidean clustering; keeps the largest object.
6. **Surface feature estimation**  — surface normals (+ curvature) for downstream tasks.
7. **Normalisation**  — translate cloud to the origin and scale it to the unit cube.
8. **Export or in‑memory return**  — save as *.ply* or hand over to your ML / SLAM pipeline.

Everything is orchestrated by **`PointCloudPipeline`** (see `src/pipeline.py`). Parameters live in **`src/params.yaml`** and can be overridden at the command line.

---
## 📂  Repository layout

```
├── requirements.txt         # Python deps (same on every OS)
├── README.md                # this file
└── src/
    ├── __init__.py
    ├── params.yaml          # tweak me!
    ├── filters.py           # low‑level building blocks
    ├── pipeline.py          # high‑level class
    ├── rs_capture.py        # RealSense live capture helper
    └── __main__.py          # CLI entry‑point (`python -m src`)
```

---
## ⚙️  Prerequisites

| Component         | macOS (arm64/x86) | Windows 10/11 | Raspberry Pi OS 64‑bit |
|-------------------|-------------------|---------------|------------------------|
| Python ≥ 3.9      | ✅                | ✅            | ✅                     |
| Open3D ≥ 0.18.0   | `pip install open3d` <br>*(M‑series: use arm64 wheel)* | `pip install open3d` | `pip install open3d==0.18.0 --no-build-isolation` |
| pyrealsense2      | `pip install pyrealsense2` | Official Intel wheel | `pip install pyrealsense2==2.54.1.5040` |
| C++ build tools   | –                 | MSVC BuildTools | `sudo apt-get install build-essential` |

### System packages (Pi only)
```bash
sudo apt-get update && sudo apt-get install libopenblas-dev liblapack-dev libx11-dev libglu1-mesa-dev
```

---
## 🚀  Quick start

```bash
# 1. Clone & create an isolated Python env
python -m venv venv              # or conda create -n realsense python=3.10
source venv/bin/activate         # Windows: venv\Scripts\activate

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Run on an existing PLY file and visualise
python -m src --input sample.ply --visualize --out sample_filtered.ply

# 4. Or capture a single frame live from a connected RealSense (index 0)
python -m src --device 0 --frames 30 --visualize --out snapshot_filtered.ply
```

> **Tip :** `--visualize` pops up an Open3D window before *and* after filtering so you can eyeball the effect of each stage.

---
## 🎛️  Tuning parameters

All numeric settings are listed in `src/params.yaml`:

```yaml
sor:
  k: 30          # neighbours
  std_ratio: 1.5 # σ cut‑off
voxel:
  size: 0.005    # m
plane:
  eps: 0.01      # RANSAC threshold (m)
cluster:
  eps: 0.02      # DB‑SCAN radius (m)
  min_points: 1000
```

Override any of them from the CLI, e.g. increase voxel size to 1 cm:
```bash
python -m src -i scan.ply --visualize --voxel.size 0.01
```
(The argument parser converts `--foo.bar` into the nested YAML key.)

---
## 🛠️  Integrating in another project

```python
import open3d as o3d
from src.pipeline import PointCloudPipeline

pc = o3d.io.read_point_cloud("some_cloud.pcd")
pipe = PointCloudPipeline.from_yaml("src/params.yaml")
clean_pc = pipe(pc)  # returns open3d.geometry.PointCloud
```

On Raspberry Pi the same code runs unchanged — just be mindful of RAM (down‑sample early if the raw cloud is huge).

---
## 🧐  Troubleshooting & FAQ

| Problem | Fix |
|---------|------|
| *pyrealsense2* wheel not found on Apple Silicon | Use Intel’s universal wheel or Homebrew `librealsense` + build from source. |
| Viewer window empty / black | Ensure you call `estimate_normals` *after* down‑sampling; otherwise OpenGL may cull the normals. |
| Performance on Pi is slow | 1) increase `voxel.size` to 1–2 cm, 2) disable `cluster.enabled`, 3) compile Open3D with OpenMP. |
| Multiple planes remain | increase `plane.iterations` or loop `max_planes` in `filters.remove_planes_ransac()`. |

---
## 📜  License

MIT License © 2025 — feel free to use, modify and distribute. Give credit where it’s due 🙂

---
## Authors
Darius Giannoli and Gabriel Taïeb

