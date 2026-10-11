from pathlib import Path

import numpy as np
import pytest
from PIL import Image, ImageSequence
from proper_pixel_art.config import PixelateConfig
from proper_pixel_art.video import pixelate_video

from comfyui_properpixelart.core.video import (
    build_video_config,
    pixelate_video_file,
)
from tests.helpers import MODIFIED_INPUTS, create_gif, upstream_config


@pytest.mark.parametrize("with_config", [False, True])
def test_video_equivalence(tmp_path, with_config):
    source = create_gif(tmp_path / "input.gif")
    actual_dir = tmp_path / "actual"
    expected_dir = tmp_path / "expected"
    actual_dir.mkdir()
    expected_dir.mkdir()
    config = upstream_config(MODIFIED_INPUTS) if with_config else None
    kwargs = dict(
        num_colors=0,
        initial_upscale_factor=1,
        pixel_width=0,
        scale_result=1,
        transparent_background=False,
        num_sample_frames=2,
        config=config,
    )
    expected_cfg = build_video_config(
        num_colors=0,
        initial_upscale_factor=1,
        pixel_width=0,
        scale_result=1,
        transparent_background=False,
        num_sample_frames=2,
        output_format="gif",
        base_config=config,
    )
    expected = pixelate_video(
        input_path=source,
        output_path=expected_dir,
        config=expected_cfg,
    )
    actual = pixelate_video_file(
        input_path=str(source),
        output_path=str(actual_dir),
        output_format="gif",
        **kwargs,
    )
    assert isinstance(actual, str)
    assert Path(actual).name == expected.name
    with Image.open(actual) as result, Image.open(expected) as direct:
        assert result.format == direct.format == "GIF"
        assert result.size == direct.size
        assert result.width > 1 and result.height > 1
        assert result.n_frames == direct.n_frames == 2
        assert result.info["loop"] == direct.info["loop"]
        for frame, reference in zip(
            ImageSequence.Iterator(result), ImageSequence.Iterator(direct), strict=True
        ):
            np.testing.assert_array_equal(
                np.array(frame.convert("RGBA")), np.array(reference.convert("RGBA"))
            )
            assert frame.info["duration"] == reference.info["duration"]


def test_video_mapping_handwritten():
    base = PixelateConfig(
        mesh=PixelateConfig().mesh,
    )
    # num_colors=0, pixel_width=0, output_format="mp4"
    cfg = build_video_config(
        num_colors=0,
        initial_upscale_factor=1,
        pixel_width=0,
        scale_result=1,
        transparent_background=False,
        num_sample_frames=4,
        output_format="mp4",
        base_config=base,
    )
    assert cfg.colors.method == "dominant"
    assert cfg.pixel_width is None
    assert cfg.video.output_format == "mp4"
    assert cfg.video.num_sample_frames == 4

    # num_colors=8, pixel_width=12, output_format="gif"
    cfg8 = build_video_config(
        num_colors=8,
        initial_upscale_factor=2,
        pixel_width=12,
        scale_result=2,
        transparent_background=True,
        num_sample_frames=6,
        output_format="gif",
        base_config=base,
    )
    assert cfg8.colors.method == "palette"
    assert cfg8.colors.palette.num_colors == 8
    assert cfg8.pixel_width == 12
    assert cfg8.video.output_format == "gif"
    assert cfg8.video.num_sample_frames == 6
