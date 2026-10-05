import logging
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from proper_pixel_art import pixelate
from proper_pixel_art.config import PixelateConfig

logger = logging.getLogger(__name__)


def tensor_to_pil(image: torch.Tensor) -> Image.Image:
    pixels = image[0].detach().float().cpu().numpy()
    return Image.fromarray(np.clip(np.rint(pixels * 255), 0, 255).astype(np.uint8))


def pil_to_tensor(image: Image.Image) -> torch.Tensor:
    pixels = np.array(image, dtype=np.float32) / 255
    return torch.from_numpy(pixels).unsqueeze(0)


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
    if image.shape[0] >= 2:
        logger.warning(
            "Received %d images; processing only the first image and ignoring the rest.",
            image.shape[0],
        )
    result = pixelate(
        image=tensor_to_pil(image),
        num_colors=num_colors,
        initial_upscale_factor=initial_upscale_factor,
        pixel_width=pixel_width,
        scale_result=scale_result,
        transparent_background=transparent_background,
        config=config,
        intermediate_dir=Path(intermediate_dir) if intermediate_dir else None,
    )
    return pil_to_tensor(result)
