import folder_paths
from comfy_api.latest import io
from proper_pixel_art.config import PixelateConfig

from ..config_type import PixelateConfigType
from ..core.video import pixelate_video_file

DEFAULT_CONFIG = PixelateConfig()


class ProperPixelArtVideo(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="ComfyUI_ProperPixelArt_Video",
            display_name="Proper Pixel Art Video / GIF",
            category="image/Proper Pixel Art",
            is_output_node=True,
            inputs=[
                io.String.Input(
                    "input_path",
                    default="",
                    multiline=False,
                    tooltip="Server-side video or GIF path.",
                ),
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
                ),
                io.Int.Input("num_sample_frames", default=8, min=1),
                io.Combo.Input(
                    "output_format", options=["Auto", "mp4", "gif"], default="Auto"
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
            outputs=[io.String.Output(display_name="output_path")],
        )

    @classmethod
    def execute(
        cls,
        input_path: str,
        num_colors: int,
        initial_upscale_factor: int,
        pixel_width: int,
        scale_result: int,
        transparent_background: bool,
        num_sample_frames: int = 8,
        output_format: str = "Auto",
        config: PixelateConfig | None = None,
        intermediate_dir: str = "",
    ) -> io.NodeOutput:
        return io.NodeOutput(
            pixelate_video_file(
                input_path=input_path,
                output_path=folder_paths.get_output_directory(),
                num_colors=num_colors,
                initial_upscale_factor=initial_upscale_factor,
                pixel_width=pixel_width,
                scale_result=scale_result,
                transparent_background=transparent_background,
                num_sample_frames=num_sample_frames,
                output_format=output_format,
                config=config,
                intermediate_dir=intermediate_dir,
            )
        )
