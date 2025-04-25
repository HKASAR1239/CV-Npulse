"""
RANSAC très léger pour :
  • sphère  → fit_sphere(...)
  • cylindre → fit_cylinder(...)

Chaque fonction renvoie :
  sphere   : (centre(3,), rayon, inlier_ratio)
  cylinder : (axis_point(3,), axis_dir(3,), rayon, inlier_ratio)
"""

from __future__ import annotations
import numpy as np

__all__ = ["fit_sphere", "fit_cylinder"]


# --------------------------------------------------------------------------- #
#  S P H E R E                                                                #
# --------------------------------------------------------------------------- #
def fit_sphere(points: np.ndarray,
               it: int = 1000,
               thr: float = 0.015) -> tuple[np.ndarray | None,
                                             float | None,
                                             float]:
    """
    RANSAC sphère :
      - it  : nombre d'itérations
      - thr : tolérance (mètres) pour qu’un point soit inlier
    """
    n = points.shape[0]
    if n < 4:
        return None, None, 0.0

    best_ratio = 0.0
    best = None
    rng = np.random.default_rng()

    for _ in range(it):
        p1, p2, p3, p4 = points[rng.choice(n, 4, replace=False)]

        # Résolution linéaire du centre
        A = np.vstack([2 * (p2 - p1),
                       2 * (p3 - p1),
                       2 * (p4 - p1)])
        b = np.array([np.dot(p2, p2) - np.dot(p1, p1),
                      np.dot(p3, p3) - np.dot(p1, p1),
                      np.dot(p4, p4) - np.dot(p1, p1)])
        try:
            c = np.linalg.solve(A, b)                   # centre
        except np.linalg.LinAlgError:
            continue

        r = np.linalg.norm(p1 - c)
        d = np.abs(np.linalg.norm(points - c, axis=1) - r)
        inliers = d < thr
        ratio = inliers.sum() / n
        if ratio > best_ratio:
            best_ratio, best = ratio, (c, r)

    return (*best, best_ratio) if best else (None, None, 0.0)


# --------------------------------------------------------------------------- #
#  C Y L I N D E R                                                            #
# --------------------------------------------------------------------------- #
def fit_cylinder(points: np.ndarray,
                 it: int = 1000,
                 thr: float = 0.02) -> tuple[np.ndarray | None,
                                               np.ndarray | None,
                                               float | None,
                                               float]:
    """
    RANSAC cylindre :
      - thr : distance max entre point et surface latérale
    """
    n = points.shape[0]
    if n < 5:
        return None, None, None, 0.0

    best_ratio = 0.0
    best = None
    rng = np.random.default_rng()

    for _ in range(it):
        p1, p2, p3 = points[rng.choice(n, 3, replace=False)]

        axis_dir = p2 - p1
        norm = np.linalg.norm(axis_dir)
        if norm < 1e-3:
            continue
        axis_dir /= norm

        r = np.linalg.norm(np.cross(p3 - p1, axis_dir))
        d = np.linalg.norm(np.cross(points - p1, axis_dir), axis=1) - r
        inliers = np.abs(d) < thr
        ratio = inliers.sum() / n
        if ratio > best_ratio:
            best_ratio, best = ratio, (p1, axis_dir, r)

    return (*best, best_ratio) if best else (None, None, None, 0.0)
