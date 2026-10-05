from pathlib import Path

from proper_pixel_art.config import PixelateConfig
from proper_pixel_art.video import pixelate_video


def pixelate_video_file(
    input_path: str,
    output_path: str,
    num_colors: int,
    initial_upscale_factor: int,
    pixel_width: int,
    scale_result: int,
    transparent_background: bool,
    num_sample_frames: int = 8,
    output_format: str = "Auto",
    config: PixelateConfig | None = None,
    intermediate_dir: str = "",
) -> str:
    return str(
        pixelate_video(
            input_path=Path(input_path),
            output_path=Path(output_path),
            num_colors=num_colors,
            initial_upscale_factor=initial_upscale_factor,
            pixel_width=pixel_width,
            scale_result=scale_result,
            transparent_background=transparent_background,
            num_sample_frames=num_sample_frames,
            output_format=None if output_format == "Auto" else output_format,
            config=config,
            intermediate_dir=Path(intermediate_dir) if intermediate_dir else None,
        )
    )
