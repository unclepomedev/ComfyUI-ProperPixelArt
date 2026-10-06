import os

import torch
from comfy_api.latest import io
from proper_pixel_art.config import PixelateConfig

from ..config_type import PixelateConfigType
from ..core.convert import pixelate_image
from .paths import resolve_intermediate_dir

DEFAULT_CONFIG = PixelateConfig()


class ProperPixelArt(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="ComfyUI_ProperPixelArt_Pixelate",
            display_name="Proper Pixel Art",
            category="image/Proper Pixel Art",
            inputs=[
                io.Image.Input(
                    "image",
                    tooltip="Source image tensor to convert to true-resolution pixel art.",
                ),
                io.Int.Input(
                    "num_colors",
                    default=DEFAULT_CONFIG.num_colors,
                    min=0,
                    max=256,
                    tooltip="Number of colors to quantize the image to. 0 skips quantization and preserves all colors.",
                ),
                io.Int.Input(
                    "initial_upscale_factor",
                    default=DEFAULT_CONFIG.initial_upscale_factor,
                    min=1,
                    max=8,
                    tooltip="Initial image upscale factor before grid detection. Useful if detected spacing is too large.",
                ),
                io.Int.Input(
                    "pixel_width",
                    default=DEFAULT_CONFIG.pixel_width,
                    min=0,
                    max=256,
                    tooltip="Width of pixels in the input image. 0 auto-detects pixel width.",
                ),
                io.Int.Input(
                    "scale_result",
                    default=DEFAULT_CONFIG.scale_result,
                    min=1,
                    max=20,
                    tooltip="Width of pixels in the output image. 1 means no scaling.",
                ),
                io.Boolean.Input(
                    "transparent_background",
                    default=DEFAULT_CONFIG.transparent_background,
                    tooltip="Makes pixels matching the most common boundary color transparent.",
                ),
                PixelateConfigType.Input(
                    "config",
                    optional=True,
                    tooltip="Optional advanced configuration overriding algorithm defaults.",
                ),
                io.String.Input(
                    "intermediate_dir",
                    optional=True,
                    default="",
                    multiline=False,
                    tooltip="Subfolder in the ComfyUI output directory to save intermediate algorithm visualization images into numbered subfolders (0, 1, ...) for each image. Empty disables saving.",
                ),
            ],
            outputs=[
                io.Image.Output(
                    is_output_list=True,
                    tooltip="List of pixelated true-resolution images as RGBA tensors.",
                )
            ],
        )

    @classmethod
    def execute(
        cls,
        image: torch.Tensor,
        num_colors: int,
        initial_upscale_factor: int,
        pixel_width: int,
        scale_result: int,
        transparent_background: bool,
        config: PixelateConfig | None = None,
        intermediate_dir: str = "",
    ) -> io.NodeOutput:
        num_images = image.shape[0]
        intermediate_dirs: list[str] = []
        if intermediate_dir:
            base_dir = resolve_intermediate_dir(intermediate_dir)
            for i in range(num_images):
                numbered_rel = os.path.join(base_dir, str(i))
                intermediate_dirs.append(resolve_intermediate_dir(numbered_rel))

        results = []
        for i in range(num_images):
            target_intermediate_dir = intermediate_dirs[i] if intermediate_dir else ""
            out = pixelate_image(
                image=image[i : i + 1],
                num_colors=num_colors,
                initial_upscale_factor=initial_upscale_factor,
                pixel_width=pixel_width,
                scale_result=scale_result,
                transparent_background=transparent_background,
                config=config,
                intermediate_dir=target_intermediate_dir,
            )
            results.append(out)

        return io.NodeOutput(results)
