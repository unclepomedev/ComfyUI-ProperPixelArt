from dataclasses import replace
from pathlib import Path

from proper_pixel_art.config import PixelateConfig
from proper_pixel_art.video import pixelate_video

from .convert import build_image_config


def build_video_config(
    num_colors: int,
    initial_upscale_factor: int,
    pixel_width: int,
    scale_result: int,
    transparent_background: bool,
    num_sample_frames: int = 8,
    output_format: str = "gif",
    base_config: PixelateConfig | None = None,
) -> PixelateConfig:
    cfg = build_image_config(
        num_colors=num_colors,
        initial_upscale_factor=initial_upscale_factor,
        pixel_width=pixel_width,
        scale_result=scale_result,
        transparent_background=transparent_background,
        base_config=base_config,
    )

    return replace(
        cfg,
        video=replace(
            cfg.video,
            num_sample_frames=num_sample_frames,
            output_format=output_format,
        ),
    )


def pixelate_video_file(
    input_path: str,
    output_path: str,
    num_colors: int,
    initial_upscale_factor: int,
    pixel_width: int,
    scale_result: int,
    transparent_background: bool,
    num_sample_frames: int = 8,
    output_format: str = "gif",
    config: PixelateConfig | None = None,
    intermediate_dir: str = "",
) -> str:
    cfg = build_video_config(
        num_colors=num_colors,
        initial_upscale_factor=initial_upscale_factor,
        pixel_width=pixel_width,
        scale_result=scale_result,
        transparent_background=transparent_background,
        num_sample_frames=num_sample_frames,
        output_format=output_format,
        base_config=config,
    )
    return str(
        pixelate_video(
            input_path=Path(input_path),
            output_path=Path(output_path),
            config=cfg,
            intermediate_dir=Path(intermediate_dir) if intermediate_dir else None,
        )
    )
