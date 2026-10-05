from pathlib import Path

import numpy as np
import pytest
from PIL import Image, ImageSequence
from proper_pixel_art.video import pixelate_video

from comfyui_properpixelart.core.video import pixelate_video_file
from tests.helpers import MODIFIED_INPUTS, create_gif, upstream_config


@pytest.mark.parametrize("output_format", ["Auto", "gif"])
@pytest.mark.parametrize("with_config", [False, True])
def test_video_equivalence(tmp_path, output_format, with_config):
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
    expected = pixelate_video(
        input_path=source,
        output_path=expected_dir,
        output_format=None if output_format == "Auto" else output_format,
        **kwargs,
    )
    actual = pixelate_video_file(
        input_path=str(source),
        output_path=str(actual_dir),
        output_format=output_format,
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
