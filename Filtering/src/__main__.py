"""CLI wrapper: run pipeline on a file or live RealSense frame."""
from __future__ import annotations

import argparse
from pathlib import Path

import open3d as o3d

from pipeline import PointCloudPipeline
from rs_capture import capture_pointcloud


def parse_args():
    ap = argparse.ArgumentParser(description='RealSense point‑cloud filtering pipeline')
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument('--input', '-i', type=str, help='Path to .ply/.pcd/.xyz/.bag file')
    src.add_argument('--device', type=int, help='RealSense device index (numeric)')

    ap.add_argument('--frames', type=int, default=30, help='Frames to skip before snapshot')
    ap.add_argument('--config', type=str, default=Path(__file__).with_name('params.yaml'))
    ap.add_argument('--out', '-o', type=str, help='Output filename (.ply). If omitted, just visualizes.')
    ap.add_argument('--visualize', action='store_true', help='Show Open3D viewer before/after')
    return ap.parse_args()


def load_pointcloud(path: Path) -> o3d.geometry.PointCloud:
    if path.suffix.lower() == '.bag':
        raise ValueError('Reading directly from .bag not implemented; play it and save to .ply first.')
    return o3d.io.read_point_cloud(str(path))


def main():
    args = parse_args()
    pipeline = PointCloudPipeline.from_yaml(args.config)

    if args.input:
        pc = load_pointcloud(Path(args.input))
    else:
        pc = capture_pointcloud(device_index=args.device, frames=args.frames)

    filtered = pipeline(pc, visualize=args.visualize)

    if args.out:
        o3d.io.write_point_cloud(args.out, filtered)
        print(f'Saved filtered cloud to {args.out}')

if __name__ == '__main__':
    main()