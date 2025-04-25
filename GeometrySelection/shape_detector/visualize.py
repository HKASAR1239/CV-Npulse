"""
Open3D visualisation helpers
"""
import open3d as o3d
from .detect import _obb


def show(pcd: o3d.geometry.PointCloud, label: str) -> None:
    obb = _obb(pcd)
    obb.color = (1, 0, 0)  # red
    frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=obb.extent.max()*0.2)
    o3d.visualization.draw_geometries([pcd, obb, frame],
                                      window_name=f"Detected: {label}")
