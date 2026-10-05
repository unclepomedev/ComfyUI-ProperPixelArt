import pytest
from proper_pixel_art.config import PixelateConfig

from tests.helpers import MODIFIED_INPUTS, config_inputs, upstream_config


@pytest.mark.parametrize("modified", [False, True])
def test_build_config(modified):
    defaults = PixelateConfig()
    inputs = config_inputs(defaults)
    if modified:
        inputs.update(MODIFIED_INPUTS)
    result = upstream_config(inputs)
    assert config_inputs(result) == inputs
    assert result.colors.background_candidates is None
    if not modified:
        assert result == PixelateConfig()


@pytest.mark.parametrize(
    "name",
    [
        "crop_border_pixels",
        "canny_low",
        "canny_high",
        "closure_kernel_size",
        "cluster_threshold",
        "hough_threshold",
        "min_line_len",
        "max_line_gap",
        "alpha_threshold",
        "bin_size",
        "top_colors_limit",
        "thumbnail_w",
        "thumbnail_h",
    ],
)
def test_integer_cast(name):
    inputs = config_inputs(PixelateConfig()) | MODIFIED_INPUTS
    expected = inputs.copy()
    inputs[name] += 0.75
    result = config_inputs(upstream_config(inputs))
    assert result == expected
    assert type(result[name]) is int
