from dataclasses import replace
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from proper_pixel_art import pixelate
from proper_pixel_art.config import PixelateConfig


def tensor_to_pil(image: torch.Tensor) -> Image.Image:
    pixels = image[0].detach().float().cpu().numpy()
    return Image.fromarray(np.clip(np.rint(pixels * 255), 0, 255).astype(np.uint8))


def pil_to_tensor(image: Image.Image) -> torch.Tensor:
    pixels = np.array(image, dtype=np.float32) / 255
    return torch.from_numpy(pixels).unsqueeze(0)


def build_image_config(
    num_colors: int,
    initial_upscale_factor: int,
    pixel_width: int,
    scale_result: int,
    transparent_background: bool,
    base_config: PixelateConfig | None = None,
) -> PixelateConfig:
    cfg = base_config if base_config is not None else PixelateConfig()

    resolved_pixel_width = None if pixel_width == 0 else pixel_width

    cfg = replace(
        cfg,
        initial_upscale_factor=initial_upscale_factor,
        scale_result=scale_result,
        transparent_background=transparent_background,
        pixel_width=resolved_pixel_width,
    )

    if num_colors == 0:
        cfg = replace(
            cfg,
            colors=replace(cfg.colors, method="dominant"),
        )
    else:
        cfg = replace(
            cfg,
            colors=replace(
                cfg.colors,
                method="palette",
                palette=replace(cfg.colors.palette, num_colors=num_colors),
            ),
        )

    return cfg


def pixelate_image(
    image: torch.Tensor,
    num_colors: int,
    initial_upscale_factor: int,
    pixel_width: int,
    scale_result: int,
    transparent_background: bool,
    config: PixelateConfig | None = None,
    intermediate_dir: str = "",
) -> torch.Tensor:
    cfg = build_image_config(
        num_colors=num_colors,
        initial_upscale_factor=initial_upscale_factor,
        pixel_width=pixel_width,
        scale_result=scale_result,
        transparent_background=transparent_background,
        base_config=config,
    )
    result = pixelate(
        image=tensor_to_pil(image),
        config=cfg,
        intermediate_dir=Path(intermediate_dir) if intermediate_dir else None,
    )
    return pil_to_tensor(result.image)
