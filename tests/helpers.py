from dataclasses import asdict

import numpy as np
import torch
from PIL import Image
from proper_pixel_art.config import (
    PixelateConfig,
)

MODIFIED_INPUTS = {
    "crop_border_pixels": 3,
    "canny_low": 41,
    "canny_high": 183,
    "closure_kernel_size": 5,
    "cluster_threshold": 7,
    "angle_threshold_deg": 3.5,
    "trim_outlier_fraction": 0.12,
    "snap_lines": False,
    "snap_search_window_ratio": 0.4,
    "snap_min_search_window": 3,
    "snap_strength_threshold": 0.6,
    "anchor_snap_window": 3,
    "max_axis_width_ratio": 2.0,
    "validate_width": False,
    "width_keep_tolerance": 1.2,
    "width_replace_tolerance": 0.3,
    "profile_width_min_gaps": 4,
    "split_leftover_fraction": 0.5,
    "rho": 1.5,
    "theta_deg": 0.75,
    "hough_threshold": 61,
    "min_line_len": 73,
    "max_line_gap": 11,
    "alpha_threshold": 137,
    "transparency_majority_fraction": 0.65,
    "quantize_method": "FASTOCTREE",
    "dither": "FLOYDSTEINBERG",
    "kmeans": 2,
    "bin_size": 40,
    "merge_distance": 15,
    "merge_linkage": "average",
    "max_linkage_colors": 2048,
    "top_colors_limit": 9,
    "thumbnail_w": 129,
    "thumbnail_h": 257,
}


def config_inputs(config: PixelateConfig) -> dict:
    mesh = asdict(config.mesh)
    colors = asdict(config.colors)
    hough = mesh.pop("hough")
    palette = colors.pop("palette")
    dominant = colors.pop("dominant")

    mesh["canny_low"], mesh["canny_high"] = mesh.pop("canny_thresholds")
    hough["hough_threshold"] = hough.pop("threshold")
    colors["thumbnail_w"], colors["thumbnail_h"] = colors.pop("thumbnail_size")
    colors.pop("background_candidates")
    colors.pop("method")
    palette.pop("num_colors")

    return mesh | hough | palette | dominant | colors


def upstream_config(inputs: dict) -> PixelateConfig:
    d = dict(inputs)
    hough_keys = {"rho", "theta_deg", "hough_threshold", "min_line_len", "max_line_gap"}
    mesh_keys = {
        "crop_border_pixels",
        "closure_kernel_size",
        "cluster_threshold",
        "angle_threshold_deg",
        "trim_outlier_fraction",
        "snap_lines",
        "snap_search_window_ratio",
        "snap_min_search_window",
        "snap_strength_threshold",
        "anchor_snap_window",
        "max_axis_width_ratio",
        "validate_width",
        "width_keep_tolerance",
        "width_replace_tolerance",
        "profile_width_min_gaps",
        "split_leftover_fraction",
    }
    palette_keys = {"quantize_method", "dither", "kmeans"}
    dominant_keys = {
        "bin_size",
        "merge_distance",
        "merge_linkage",
        "max_linkage_colors",
    }
    color_keys = {
        "alpha_threshold",
        "transparency_majority_fraction",
        "top_colors_limit",
    }

    hough_data = {k: d[k] for k in hough_keys if k in d}
    if "hough_threshold" in hough_data:
        hough_data["threshold"] = hough_data.pop("hough_threshold")

    mesh_data = {k: d[k] for k in mesh_keys if k in d}
    if "canny_low" in d and "canny_high" in d:
        mesh_data["canny_thresholds"] = (d["canny_low"], d["canny_high"])
    if hough_data:
        mesh_data["hough"] = hough_data

    palette_data = {k: d[k] for k in palette_keys if k in d}
    dominant_data = {k: d[k] for k in dominant_keys if k in d}
    color_data = {k: d[k] for k in color_keys if k in d}
    if "thumbnail_w" in d and "thumbnail_h" in d:
        color_data["thumbnail_size"] = (d["thumbnail_w"], d["thumbnail_h"])
    if palette_data:
        color_data["palette"] = palette_data
    if dominant_data:
        color_data["dominant"] = dominant_data

    nested: dict = {}
    if mesh_data:
        nested["mesh"] = mesh_data
    if color_data:
        nested["colors"] = color_data

    return PixelateConfig.from_dict(nested)


def create_pixel_art_tensor(
    grid_size: int = 32,
    image_size: int = 512,
    seed: int = 42,
    channels: int = 3,
):
    cells = np.random.default_rng(seed).integers(
        0, 256, size=(grid_size, grid_size, channels), dtype=np.uint8
    )
    img = Image.fromarray(cells).resize(
        (image_size, image_size), Image.Resampling.NEAREST
    )
    return torch.from_numpy(np.array(img, dtype=np.float32) / 255).unsqueeze(0)


def create_gif(path):
    cells = np.random.default_rng(42).integers(0, 256, size=(32, 32, 3), dtype=np.uint8)
    frames = [
        Image.fromarray(np.roll(cells, shift, axis=0)).resize(
            (512, 512), Image.Resampling.NEAREST
        )
        for shift in range(2)
    ]
    frames[0].save(
        path, save_all=True, append_images=frames[1:], duration=[80, 160], loop=0
    )
    return path
