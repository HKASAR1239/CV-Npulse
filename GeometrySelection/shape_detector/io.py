"""
I/O utilities: read file or capture RealSense frame
"""
from pathlib import Path
import numpy as np
import open3d as o3d


def load_point_cloud(path: Path) -> o3d.geometry.PointCloud:
    if not path.exists():
        raise FileNotFoundError(path)
    pcd = o3d.io.read_point_cloud(str(path))
    if pcd.is_empty():
        raise ValueError(f"Empty point cloud: {path}")
    return pcd


def capture_realsense_frame() -> o3d.geometry.PointCloud:  # pragma: no cover
    try:
        import pyrealsense2 as rs
    except ImportError as exc:
        raise RuntimeError("pyrealsense2 not installed") from exc

    pipeline = rs.pipeline()
    cfg = rs.config()
    cfg.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    pipeline.start(cfg)

    try:
        for _ in range(5):          # warm-up
            pipeline.wait_for_frames()
        frames = pipeline.wait_for_frames()
        depth = frames.get_depth_frame()
        if not depth:
            raise RuntimeError("No depth frame")
        pc = rs.pointcloud()
        points = pc.calculate(depth)
        vtx = np.asanyarray(points.get_vertices(), dtype=np.float32)
        xyz = vtx.view(np.float32).reshape(-1, 3)
    finally:
        pipeline.stop()

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(xyz)
    return pcd
