import os

import folder_paths
from comfy_api.latest import io
from proper_pixel_art.cli import VIDEO_SUFFIXES
from proper_pixel_art.config import PixelateConfig

from ..config_type import PixelateConfigType
from ..core.video import pixelate_video_file

DEFAULT_CONFIG = PixelateConfig()
SUPPORTED_VIDEO_EXTS = sorted(suffix.lower() for suffix in VIDEO_SUFFIXES)


class ProperPixelArtVideo(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        input_dir = folder_paths.get_input_directory()
        try:
            files = [
                f
                for f in os.listdir(input_dir)
                if os.path.isfile(os.path.join(input_dir, f))
            ]
        except FileNotFoundError:
            files = []
        files = folder_paths.filter_files_extensions(
            files,
            SUPPORTED_VIDEO_EXTS,
        )

        return io.Schema(
            node_id="ComfyUI_ProperPixelArt_Video",
            display_name="Proper Pixel Art Video / GIF",
            category="image/Proper Pixel Art",
            is_output_node=True,
            inputs=[
                io.Combo.Input(
                    "input_path",
                    options=sorted(files),
                    upload=io.UploadType.video,
                    tooltip="Source video or GIF from the ComfyUI input directory.",
                ),
                io.Int.Input(
                    "num_colors",
                    default=DEFAULT_CONFIG.num_colors,
                    min=0,
                    max=256,
                    tooltip="Number of colors to quantize the frames to. 0 skips quantization and preserves all colors.",
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
                    tooltip="Width of pixels in the input frames. 0 auto-detects pixel width.",
                ),
                io.Int.Input(
                    "scale_result",
                    default=DEFAULT_CONFIG.scale_result,
                    min=1,
                    max=20,
                    tooltip="Width of pixels in the output animation. 1 means no scaling.",
                ),
                io.Boolean.Input(
                    "transparent_background",
                    default=DEFAULT_CONFIG.transparent_background,
                    tooltip="Makes pixels matching the most common boundary color transparent. GIF output supports only binary transparency.",
                ),
                io.Int.Input(
                    "num_sample_frames",
                    default=8,
                    min=1,
                    tooltip="Number of frames to sample for mesh and palette detection across the video or GIF.",
                ),
                io.Combo.Input(
                    "output_format",
                    options=["Auto", "mp4", "gif"],
                    default="Auto",
                    tooltip="Output container format. Auto infers the format from the input extension (mp4 for non-GIF inputs).",
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
                    tooltip="Subfolder in the ComfyUI output directory to save intermediate algorithm visualization images. Empty disables saving.",
                ),
            ],
            outputs=[
                io.String.Output(
                    display_name="output_path",
                    tooltip="Server-side file path to the saved video or GIF in the ComfyUI output directory.",
                )
            ],
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
        resolved_input_path = folder_paths.get_annotated_filepath(input_path)
        resolved_intermediate_dir = (
            folder_paths.get_annotated_filepath(
                intermediate_dir,
                default_dir=folder_paths.get_output_directory(),
            )
            if intermediate_dir
            else ""
        )
        return io.NodeOutput(
            pixelate_video_file(
                input_path=resolved_input_path,
                output_path=folder_paths.get_output_directory(),
                num_colors=num_colors,
                initial_upscale_factor=initial_upscale_factor,
                pixel_width=pixel_width,
                scale_result=scale_result,
                transparent_background=transparent_background,
                num_sample_frames=num_sample_frames,
                output_format=output_format,
                config=config,
                intermediate_dir=resolved_intermediate_dir,
            )
        )
