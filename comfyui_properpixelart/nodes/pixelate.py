import torch
from comfy_api.latest import io
from proper_pixel_art.config import PixelateConfig

from ..config_type import PixelateConfigType
from ..core.convert import pixelate_image

DEFAULT_CONFIG = PixelateConfig()


class ProperPixelArt(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="ComfyUI_ProperPixelArt_Pixelate",
            display_name="Proper Pixel Art",
            category="image/Proper Pixel Art",
            inputs=[
                io.Image.Input("image"),
                io.Int.Input(
                    "num_colors",
                    default=DEFAULT_CONFIG.num_colors,
                    min=0,
                    max=256,
                    tooltip="0 = no quantization",
                ),
                io.Int.Input(
                    "initial_upscale_factor",
                    default=DEFAULT_CONFIG.initial_upscale_factor,
                    min=1,
                    max=8,
                    tooltip="Upscale before grid detection.",
                ),
                io.Int.Input(
                    "pixel_width",
                    default=DEFAULT_CONFIG.pixel_width,
                    min=0,
                    max=256,
                    tooltip="0 = auto-detect",
                ),
                io.Int.Input(
                    "scale_result",
                    default=DEFAULT_CONFIG.scale_result,
                    min=1,
                    max=20,
                    tooltip="1 = no scaling",
                ),
                io.Boolean.Input(
                    "transparent_background",
                    default=DEFAULT_CONFIG.transparent_background,
                    tooltip="Make the most common boundary color transparent.",
                ),
                PixelateConfigType.Input("config", optional=True),
                io.String.Input(
                    "intermediate_dir",
                    optional=True,
                    default="",
                    multiline=False,
                    tooltip="Directory for intermediate images. Empty = disabled.",
                ),
            ],
            outputs=[io.Image.Output()],
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
        return io.NodeOutput(
            pixelate_image(
                image=image,
                num_colors=num_colors,
                initial_upscale_factor=initial_upscale_factor,
                pixel_width=pixel_width,
                scale_result=scale_result,
                transparent_background=transparent_background,
                config=config,
                intermediate_dir=intermediate_dir,
            ),
        )
