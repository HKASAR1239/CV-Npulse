"""Minimal RealSense frame capture to Open3D point‑cloud."""
import pyrealsense2 as rs
import numpy as np
import open3d as o3d


def capture_pointcloud(device_index: int = 0, frames: int = 30) -> o3d.geometry.PointCloud:
    pipe = rs.pipeline()
    cfg = rs.config()
    cfg.enable_device_from_file(False)
    cfg.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    cfg.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    if device_index is not None:
        cfg.enable_device_from_file(False)
    pipe.start(cfg)

    for _ in range(frames):
        pipe.wait_for_frames()
    frameset = pipe.wait_for_frames()
    depth = frameset.get_depth_frame()
    color = frameset.get_color_frame()

    # Point‑cloud generation
    pc = rs.pointcloud()
    pc.map_to(color)
    points = pc.calculate(depth)

    # Convert to Open3D
    verts = np.asarray(points.get_vertices()).view(np.float32).reshape(-1, 3)
    colors = np.asarray(color.get_data()).reshape(480, 640, 3)
    colors = colors.astype(np.float32) / 255.0
    colors = colors.reshape(-1, 3)

    o3d_pc = o3d.geometry.PointCloud()
    o3d_pc.points = o3d.utility.Vector3dVector(verts)
    o3d_pc.colors = o3d.utility.Vector3dVector(colors)

    pipe.stop()
    return o3d_pc