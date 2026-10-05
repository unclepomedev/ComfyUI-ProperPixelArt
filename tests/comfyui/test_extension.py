import asyncio
import importlib.util
import os
import sys
from pathlib import Path

import numpy as np
import pytest
import torch
from PIL import Image
from proper_pixel_art.config import PixelateConfig

from tests.helpers import MODIFIED_INPUTS, config_inputs, upstream_config

if "REQUIRE_COMFYUI" in os.environ:
    import comfy_api.latest as comfy_api
else:
    comfy_api = pytest.importorskip("comfy_api.latest")


@pytest.fixture(scope="module")
def node_list():
    root = Path(__file__).resolve().parents[2]
    module_name = "properpixelart_test_pack"
    spec = importlib.util.spec_from_file_location(
        module_name,
        root / "__init__.py",
        submodule_search_locations=[str(root)],
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    assert callable(module.comfy_entrypoint)

    async def load_nodes():
        extension = await module.comfy_entrypoint()
        assert isinstance(extension, comfy_api.ComfyExtension)
        await extension.on_load()
        return await extension.get_node_list()

    nodes = asyncio.run(load_nodes())
    assert isinstance(nodes, list) and nodes
    indexed = {}
    for node in nodes:
        assert issubclass(node, comfy_api.io.ComfyNode)
        assert isinstance(node.define_schema(), comfy_api.io.Schema)
        schema = node.GET_SCHEMA()
        assert schema.node_id and schema.node_id not in indexed
        indexed[schema.node_id] = node
    assert set(indexed) == {
        "ComfyUI_ProperPixelArt_Pixelate",
        "ComfyUI_ProperPixelArt_Config",
    }
    return indexed


def test_schema(node_list):
    defaults = PixelateConfig()
    schema = node_list["ComfyUI_ProperPixelArt_Pixelate"].GET_SCHEMA()
    inputs = {widget.id: widget for widget in schema.inputs}
    for name in (
        "num_colors",
        "initial_upscale_factor",
        "pixel_width",
        "scale_result",
        "transparent_background",
    ):
        assert inputs[name].default == getattr(defaults, name)


def test_config_schema(node_list):
    schema = node_list["ComfyUI_ProperPixelArt_Config"].GET_SCHEMA()
    inputs = {widget.id: widget for widget in schema.inputs}
    expected = config_inputs(PixelateConfig())
    assert set(inputs) == set(expected)
    for name, value in expected.items():
        assert inputs[name].default == value
    assert inputs["quantize_method"].options == [
        "MEDIANCUT",
        "MAXCOVERAGE",
        "FASTOCTREE",
    ]
    assert len(schema.outputs) == 1


@pytest.mark.parametrize("modified", [False, True])
def test_config_execute(node_list, modified):
    node = node_list["ComfyUI_ProperPixelArt_Config"]
    inputs = config_inputs(PixelateConfig())
    if modified:
        inputs.update(MODIFIED_INPUTS)
    output = node.execute(**inputs)
    assert isinstance(output, comfy_api.io.NodeOutput)
    assert len(output.result) == 1
    assert isinstance(output.result[0], PixelateConfig)
    assert output.result[0] == upstream_config(inputs)
    if not modified:
        assert output.result[0] == PixelateConfig()


@pytest.fixture
def image():
    cells = np.random.default_rng(42).integers(0, 256, size=(32, 32, 3), dtype=np.uint8)
    source = Image.fromarray(cells).resize((512, 512), Image.Resampling.NEAREST)
    return torch.from_numpy(np.array(source, dtype=np.float32) / 255).unsqueeze(0)


def assert_image_output(output):
    assert isinstance(output, comfy_api.io.NodeOutput)
    assert len(output.result) == 1
    result = output.result[0]
    assert isinstance(result, torch.Tensor)
    assert result.ndim == 4
    assert result.shape[0] == 1 and result.shape[-1] == 4
    assert result.shape[1] > 1 and result.shape[2] > 1
    assert result.dtype == torch.float32
    assert torch.all((result >= 0) & (result <= 1))


def test_execute(node_list, image):
    output = node_list["ComfyUI_ProperPixelArt_Pixelate"].execute(
        image=image,
        num_colors=0,
        initial_upscale_factor=1,
        pixel_width=0,
        scale_result=1,
        transparent_background=False,
    )
    assert_image_output(output)


def test_config_connection(node_list, image):
    inputs = config_inputs(PixelateConfig())
    inputs.update(canny_low=40, canny_high=180, thumbnail_w=128, bin_size=40)
    config = node_list["ComfyUI_ProperPixelArt_Config"].execute(**inputs).result[0]
    output = node_list["ComfyUI_ProperPixelArt_Pixelate"].execute(
        image=image,
        num_colors=0,
        initial_upscale_factor=1,
        pixel_width=0,
        scale_result=1,
        transparent_background=False,
        config=config,
    )
    assert_image_output(output)
