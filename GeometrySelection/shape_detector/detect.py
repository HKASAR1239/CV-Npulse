"""
Détection : sphère / cylindre / cuboïde-tablette
"""
from __future__ import annotations
import numpy as np
import open3d as o3d
from .ransac import fit_sphere, fit_cylinder


# --------------------------------------------------------------------------- #
def _down(pc, vox=0.005):
    return pc.voxel_down_sample(vox)


def _obb(pc):
    return pc.get_oriented_bounding_box()


# --------------------------------------------------------------------------- #
def detect_shape(pcd: o3d.geometry.PointCloud, verbose: bool = False) -> str:
    """Retourne 'spherical', 'cylindrical' ou 'cuboid/tablet'."""
    pcd_d = _down(pcd)
    obb = _obb(pcd_d)
    ext = np.asarray(obb.extent)          # (lx, ly, lz)
    e1, e2, e3 = np.sort(ext)             # e1 ≤ e2 ≤ e3
    if verbose:
        print(f"Extents: {ext}")

    # ---------- Sphère ------------------------------------------------------
    iso_thr = 0.15                       # axes ≈ ±15 %
    if np.allclose(ext, ext.mean(), rtol=iso_thr):
        thr_s = 0.015 * ext.mean()       # 1.5 % du diamètre
        _, _, inl = fit_sphere(np.asarray(pcd_d.points), thr=thr_s)
        if verbose:
            print(f"Sphere inliers: {inl:.2%}")
        if inl > 0.70:
            return "spherical"

    # ---------- Cylindre ----------------------------------------------------
    cyl_thr = 0.15                       # rayonX ≈ rayonY ±15 %
    length_ratio = 1.15                  # hauteur ≥ 1.15 × rayon
    radius_est = (e1 + e2) / 2
    looks_cyl = abs(e1 - e2) < cyl_thr * radius_est and e3 > length_ratio * radius_est
    if looks_cyl:
        # essai Open3D (si ≥0.18)
        try:
            _, inliers = pcd_d.segment_cylinder(distance_threshold=0.02 * radius_est,
                                                ransac_n=3,
                                                num_iterations=1000)
            inlier_ratio = len(inliers) / len(pcd_d.points)
            if verbose:
                print(f"O3D cylinder inliers: {inlier_ratio:.2%}")
        except AttributeError:
            inlier_ratio = 0.0

        # fallback RANSAC maison si besoin
        if inlier_ratio < 0.25:
            thr_c = 0.03 * radius_est    # 3 % du rayon
            _, _, _, inlier_ratio = fit_cylinder(np.asarray(pcd_d.points), thr=thr_c)
            if verbose:
                print(f"Fallback cylinder inliers: {inlier_ratio:.2%}")

        if inlier_ratio > 0.25:
            return "cylindrical"

    # ---------- Par défaut ---------------------------------------------------
    return "cuboid/tablet"
