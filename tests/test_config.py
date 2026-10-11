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
