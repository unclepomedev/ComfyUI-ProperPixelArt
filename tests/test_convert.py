import numpy as np
import pytest
import torch
from PIL import Image
from proper_pixel_art import pixelate
from proper_pixel_art.config import PixelateConfig

from comfyui_properpixelart.core.convert import (
    pil_to_tensor,
    pixelate_image,
    tensor_to_pil,
)


def pixel_art(channels):
    cells = np.random.default_rng(42).integers(
        0, 256, size=(32, 32, channels), dtype=np.uint8
    )
    return Image.fromarray(cells).resize((512, 512), Image.Resampling.NEAREST)


@pytest.mark.parametrize("channels", [3, 4])
@pytest.mark.parametrize(
    "num_colors,pixel_width,scale_result,transparent_background",
    [(0, 0, 1, False), (8, 16, 2, True)],
)
@pytest.mark.parametrize("with_config", [False, True])
def test_equivalence(
    channels, num_colors, pixel_width, scale_result, transparent_background, with_config
):
    source = pixel_art(channels)
    image = pil_to_tensor(source)
    config = (
        PixelateConfig(
            num_colors=4,
            initial_upscale_factor=2,
            pixel_width=2,
            scale_result=3,
            transparent_background=not transparent_background,
        )
        if with_config
        else None
    )
    kwargs = {
        "num_colors": num_colors,
        "initial_upscale_factor": 1,
        "pixel_width": pixel_width,
        "scale_result": scale_result,
        "transparent_background": transparent_background,
        "config": config,
    }
    expected = pixelate(source, **kwargs)
    assert expected.width > 1 and expected.height > 1
    actual = pixelate_image(image, **kwargs)
    assert expected.mode == "RGBA"
    assert actual.dtype == torch.float32
    assert actual.shape == (1, expected.height, expected.width, 4)
    assert 0 <= actual.min() <= actual.max() <= 1
    np.testing.assert_array_equal(
        np.asarray(tensor_to_pil(actual)), np.asarray(expected)
    )


@pytest.mark.parametrize("channels", [3, 4])
@pytest.mark.parametrize("dtype", [torch.float32, torch.float16, torch.bfloat16])
def test_roundtrip(channels, dtype):
    source = pixel_art(channels)
    image = pil_to_tensor(source).to(device="cpu", dtype=dtype)
    before = image.clone()
    result = tensor_to_pil(image)
    assert result.mode == ("RGB" if channels == 3 else "RGBA")
    np.testing.assert_array_equal(np.asarray(result), np.asarray(source))
    assert torch.equal(image, before)


def test_rounding_and_clipping():
    image = torch.tensor([[[[-0.1, 0.5, 1.1], [0.49, 0.51, 0.0]]]])
    np.testing.assert_array_equal(
        np.asarray(tensor_to_pil(image)), [[[0, 128, 255], [125, 130, 0]]]
    )


@pytest.mark.parametrize("channels", [3, 4])
def test_inputs_unchanged(channels):
    source = pixel_art(channels)
    before = source.tobytes(), source.mode, source.size
    image = pil_to_tensor(source)
    original = image.clone()
    tensor_to_pil(image)
    pixelate_image(image, 0, 1, 4, 1, False)
    assert torch.equal(image, original)
    assert (source.tobytes(), source.mode, source.size) == before
    image.zero_()
    assert (source.tobytes(), source.mode, source.size) == before


def test_intermediate_dir(tmp_path):
    source = pixel_art(4)
    actual_dir = tmp_path / "wrapped"
    expected_dir = tmp_path / "direct"
    actual_dir.mkdir()
    expected_dir.mkdir()
    actual = pixelate_image(
        pil_to_tensor(source), 8, 1, 4, 1, False, intermediate_dir=str(actual_dir)
    )
    expected = pixelate(
        source,
        num_colors=8,
        initial_upscale_factor=1,
        pixel_width=4,
        scale_result=1,
        transparent_background=False,
        intermediate_dir=expected_dir,
    )
    np.testing.assert_array_equal(
        np.asarray(tensor_to_pil(actual)), np.asarray(expected)
    )
    assert {p.name for p in actual_dir.iterdir()} == {
        p.name for p in expected_dir.iterdir()
    }
    assert any(actual_dir.iterdir())


def test_invalid_num_colors_propagates():
    source = pixel_art(4)
    kwargs = {
        "num_colors": 300,
        "initial_upscale_factor": 1,
        "pixel_width": 16,
        "scale_result": 1,
        "transparent_background": False,
    }
    with pytest.raises(ValueError) as expected:
        pixelate(source, **kwargs)
    with pytest.raises(type(expected.value)) as actual:
        pixelate_image(pil_to_tensor(source), **kwargs)
    assert str(actual.value) == str(expected.value)


def test_missing_intermediate_dir_propagates(tmp_path):
    source = pixel_art(4)
    missing_dir = tmp_path / "missing"
    assert not missing_dir.exists()
    kwargs = {
        "num_colors": 0,
        "initial_upscale_factor": 1,
        "pixel_width": 16,
        "scale_result": 1,
        "transparent_background": False,
    }
    with pytest.raises(FileNotFoundError) as expected:
        pixelate(source, intermediate_dir=missing_dir, **kwargs)
    with pytest.raises(type(expected.value)) as actual:
        pixelate_image(
            pil_to_tensor(source), intermediate_dir=str(missing_dir), **kwargs
        )
    assert str(actual.value) == str(expected.value)
