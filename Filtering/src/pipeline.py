"""High‑level pipeline orchestration."""
from __future__ import annotations

import yaml
import open3d as o3d
from pathlib import Path
from typing import Union, Optional

import filters as fl

class PointCloudPipeline:
    """Run all filtering stages on an Open3D point‑cloud."""
    def __init__(self, params: dict):
        self.p = params

    @classmethod
    def from_yaml(cls, yaml_path: Union[str, Path]):
        with open(yaml_path, 'r') as f:
            params = yaml.safe_load(f)
        return cls(params)

    # -----------------------------------------------------
    def __call__(self, pc: o3d.geometry.PointCloud, visualize: bool = False) -> o3d.geometry.PointCloud:
        if visualize:
            o3d.visualization.draw_geometries([pc], window_name='Raw input')

        pc = fl.remove_invalid_points(pc)

        pc = fl.statistical_outlier_removal(pc, **self.p['sor'])
        pc = fl.radius_outlier_removal(pc, **self.p['ror'])

        pc = fl.voxel_downsample(pc, **self.p['voxel'])
        pc = fl.remove_planes_ransac(pc, **self.p['plane'])

        if self.p['crop']['enabled']:
            pc = fl.crop_bounding_box(pc, self.p['crop']['min'], self.p['crop']['max'])

        if self.p['cluster']['enabled']:
            pc = fl.select_largest_cluster(pc, **self.p['cluster'])

        pc = fl.estimate_normals(pc, **self.p['normals'])
        pc, _ = fl.center_and_scale(pc)

        if visualize:
            o3d.visualization.draw_geometries([pc], window_name='Filtered')
        return pc