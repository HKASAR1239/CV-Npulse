import argparse
from pathlib import Path

from shape_detector import io, detect, visualize


def parse_args():
    p = argparse.ArgumentParser(description="Detect primitive shapes in a point cloud")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--input", type=Path, help="Path to .ply/.pcd/.xyz file")
    g.add_argument("--live", action="store_true", help="Capture one frame from RealSense")
    p.add_argument("--visualize", action="store_true", help="Show Open3D viewer")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    if args.live:
        print("Capturing RealSense frame ...")
        pcd = io.capture_realsense_frame()
    else:
        print(f"Loading {args.input} ...")
        pcd = io.load_point_cloud(args.input)

    shape = detect.detect_shape(pcd, verbose=True)
    print(f"Detected shape: {shape}")

    if args.visualize:
        visualize.show(pcd, shape)


if __name__ == "__main__":
    main()
