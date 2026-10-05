from dataclasses import asdict

import numpy as np
from PIL import Image
from proper_pixel_art.config import PixelateConfig
from proper_pixel_art.web import build_config as upstream_build_config

MODIFIED_INPUTS = {
    "crop_border_pixels": 2,
    "canny_low": 41,
    "canny_high": 183,
    "closure_kernel_size": 5,
    "cluster_threshold": 7,
    "angle_threshold_deg": 3.5,
    "trim_outlier_fraction": 0.12,
    "rho": 1.5,
    "theta_deg": 0.75,
    "hough_threshold": 61,
    "min_line_len": 73,
    "max_line_gap": 11,
    "alpha_threshold": 137,
    "transparency_majority_fraction": 0.65,
    "quantize_method": "FASTOCTREE",
    "bin_size": 40,
    "top_colors_limit": 9,
    "thumbnail_w": 129,
    "thumbnail_h": 257,
}


def config_inputs(config):
    mesh = asdict(config.mesh)
    colors = asdict(config.colors)
    hough = mesh.pop("hough")
    mesh["canny_low"], mesh["canny_high"] = mesh.pop("canny_thresholds")
    hough["hough_threshold"] = hough.pop("threshold")
    colors["thumbnail_w"], colors["thumbnail_h"] = colors.pop("thumbnail_size")
    colors.pop("background_candidates")
    return mesh | hough | colors


def upstream_config(inputs):
    main = asdict(PixelateConfig())
    main.pop("mesh")
    main.pop("colors")
    return upstream_build_config(**main, **inputs)


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
