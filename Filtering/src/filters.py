"""Low‑level filtering primitives used by the point‑cloud pipeline."""
from __future__ import annotations

import numpy as np
import open3d as o3d
from typing import Tuple, List

# ---------- general helpers ----------------------------------

def _select_by_index(pc: o3d.geometry.PointCloud, indices: List[int]) -> o3d.geometry.PointCloud:
    """Return point‑cloud made of *indices* (keeps attributes)."""
    mask = np.zeros(len(pc.points), dtype=bool)
    mask[indices] = True
    return pc.select_by_index(np.where(mask)[0])

# ---------- step 0: invalid / NaN removal ---------------------

def remove_invalid_points(pc: o3d.geometry.PointCloud) -> o3d.geometry.PointCloud:
    pc.remove_non_finite_points()
    return pc

# ---------- step 1a: Statistical Outlier Removal -------------

def statistical_outlier_removal(pc: o3d.geometry.PointCloud,
                                nb_neighbors: int = 30,
                                std_ratio: float = 1.5) -> o3d.geometry.PointCloud:
    pc, ind = pc.remove_statistical_outlier(nb_neighbors, std_ratio)
    return pc

# ---------- step 1b: Radius Outlier Removal -------------------

def radius_outlier_removal(pc: o3d.geometry.PointCloud,
                           nb_points: int = 3,
                           radius: float = 0.02) -> o3d.geometry.PointCloud:
    pc, ind = pc.remove_radius_outlier(nb_points, radius)
    return pc

# ---------- step 2: Voxel grid down‑sampling ------------------

def voxel_downsample(pc: o3d.geometry.PointCloud, voxel_size: float = 0.005) -> o3d.geometry.PointCloud:
    return pc.voxel_down_sample(voxel_size)

# ---------- step 3: dominant plane removal (RANSAC) -----------

def remove_planes_ransac(pc: o3d.geometry.PointCloud,
                         distance_threshold: float = 0.01,
                         ransac_n: int = 3,
                         num_iterations: int = 1000,
                         max_planes: int = 1) -> o3d.geometry.PointCloud:
    """Iteratively segment and remove dominant planes."""
    remaining = pc
    for _ in range(max_planes):
        if len(remaining.points) < 50:
            break
        plane_model, inliers = remaining.segment_plane(distance_threshold,
                                                       ransac_n,
                                                       num_iterations)
        if len(inliers) / len(remaining.points) < 0.30:  # stop if plane is not big
            break
        remaining = _select_by_index(remaining, list(set(range(len(remaining.points))) - set(inliers)))
    return remaining

# ---------- step 5a: bounding‑box crop ------------------------

def crop_bounding_box(pc: o3d.geometry.PointCloud,
                      min_bound: Tuple[float, float, float],
                      max_bound: Tuple[float, float, float]) -> o3d.geometry.PointCloud:
    bbox = o3d.geometry.AxisAlignedBoundingBox(min_bound=min_bound, max_bound=max_bound)
    return pc.crop(bbox)

# ---------- step 5b: Euclidean clustering ---------------------

def select_largest_cluster(pc: o3d.geometry.PointCloud,
                           eps: float = 0.02,
                           min_points: int = 1000) -> o3d.geometry.PointCloud:
    labels = np.array(pc.cluster_dbscan(eps=eps, min_points=min_points, print_progress=False))
    if labels.size == 0:
        return pc
    largest_label = int(np.bincount(labels[labels >= 0]).argmax())
    indices = np.where(labels == largest_label)[0]
    return _select_by_index(pc, indices)

# ---------- step 6: normals & curvature -----------------------

def estimate_normals(pc: o3d.geometry.PointCloud, k: int = 30) -> o3d.geometry.PointCloud:
    pc.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamKNN(k))
    pc.normalize_normals()
    return pc

# ---------- step 7: centering + scale -------------------------

def center_and_scale(pc: o3d.geometry.PointCloud) -> Tuple[o3d.geometry.PointCloud, float]:
    center = pc.get_center()
    pc.translate(-center)
    bbox = pc.get_axis_aligned_bounding_box()
    scale = 1.0 / max(bbox.extent)
    pc.scale(scale, center=(0., 0., 0.))
    return pc, scale