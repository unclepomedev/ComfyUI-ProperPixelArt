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
    return nodes


def test_schema(node_list):
    defaults = PixelateConfig()
    node_ids = set()
    for node in node_list:
        assert issubclass(node, comfy_api.io.ComfyNode)
        assert isinstance(node.define_schema(), comfy_api.io.Schema)
        schema = node.GET_SCHEMA()
        assert schema.node_id and schema.node_id not in node_ids
        node_ids.add(schema.node_id)
        inputs = {widget.id: widget for widget in schema.inputs}
        for name in (
            "num_colors",
            "initial_upscale_factor",
            "pixel_width",
            "scale_result",
            "transparent_background",
        ):
            assert inputs[name].default == getattr(defaults, name)


def test_execute(node_list):
    cells = np.random.default_rng(42).integers(0, 256, size=(32, 32, 3), dtype=np.uint8)
    source = Image.fromarray(cells).resize((512, 512), Image.Resampling.NEAREST)
    image = torch.from_numpy(np.array(source, dtype=np.float32) / 255).unsqueeze(0)
    for node in node_list:
        output = node.execute(
            image=image,
            num_colors=0,
            initial_upscale_factor=1,
            pixel_width=0,
            scale_result=1,
            transparent_background=False,
        )
        assert isinstance(output, comfy_api.io.NodeOutput)
        assert len(output.result) == 1
        result = output.result[0]
        assert isinstance(result, torch.Tensor)
        assert result.ndim == 4
        assert result.shape[0] == 1 and result.shape[-1] == 4
        assert result.shape[1] > 1 and result.shape[2] > 1
        assert result.dtype == torch.float32
        assert torch.all((result >= 0) & (result <= 1))
