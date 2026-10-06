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

from tests.helpers import MODIFIED_INPUTS, config_inputs, create_gif, upstream_config
from tools.generate_docs import generate_nodes_markdown

if "REQUIRE_COMFYUI" in os.environ:
    import comfy_api.latest as comfy_api
else:
    comfy_api = pytest.importorskip("comfy_api.latest")

from proper_pixel_art.cli import VIDEO_SUFFIXES


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
        "ComfyUI_ProperPixelArt_Video",
    }
    return indexed


@pytest.mark.parametrize(
    "node_id", ["ComfyUI_ProperPixelArt_Pixelate", "ComfyUI_ProperPixelArt_Video"]
)
def test_schema(node_list, node_id):
    defaults = PixelateConfig()
    schema = node_list[node_id].GET_SCHEMA()
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
    assert inputs["bin_size"].min == 1
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
    inputs.update(quantize_method="FASTOCTREE")
    config = node_list["ComfyUI_ProperPixelArt_Config"].execute(**inputs).result[0]
    node = node_list["ComfyUI_ProperPixelArt_Pixelate"]
    main_inputs = dict(
        image=image,
        num_colors=8,
        initial_upscale_factor=1,
        pixel_width=0,
        scale_result=1,
        transparent_background=False,
    )
    output = node.execute(**main_inputs, config=config)
    default_output = node.execute(**main_inputs)
    assert_image_output(output)
    assert_image_output(default_output)
    assert not torch.equal(output.result[0], default_output.result[0])


def test_video_schema(node_list):
    schema = node_list["ComfyUI_ProperPixelArt_Video"].GET_SCHEMA()
    inputs = {widget.id: widget for widget in schema.inputs}
    image_inputs = {
        widget.id: widget
        for widget in node_list["ComfyUI_ProperPixelArt_Pixelate"].GET_SCHEMA().inputs
    }
    for name in ("num_colors", "initial_upscale_factor", "pixel_width", "scale_result"):
        assert inputs[name].min == image_inputs[name].min
        assert inputs[name].max == image_inputs[name].max
    assert schema.is_output_node
    assert inputs["input_path"].upload == comfy_api.io.UploadType.video
    assert inputs["output_format"].options == ["Auto", "mp4", "gif"]
    assert inputs["output_format"].default == "Auto"
    assert inputs["num_sample_frames"].default == 8
    assert inputs["num_sample_frames"].min == 1
    assert inputs["config"].optional
    assert inputs["intermediate_dir"].optional
    assert inputs["intermediate_dir"].default == ""
    assert len(schema.outputs) == 1


def test_video_supported_extensions(node_list, video_directories):
    input_dir = video_directories["input"]
    node_cls = node_list["ComfyUI_ProperPixelArt_Video"]

    # Create dummy files for every upstream supported suffix in the input directory and an unsupported extension.
    created_names = []
    for idx, suffix in enumerate(sorted(VIDEO_SUFFIXES)):
        filename = f"sample_{idx}{suffix.lower()}"
        (input_dir / filename).touch()
        created_names.append(filename)
    (input_dir / "ignored.txt").touch()

    schema = node_cls.define_schema()
    inputs = {widget.id: widget for widget in schema.inputs}
    options = inputs["input_path"].options
    assert options == sorted(created_names)


@pytest.fixture
def video_directories(tmp_path):
    folder_paths = sys.modules["folder_paths"]
    prev_input = folder_paths.get_input_directory()
    prev_output = folder_paths.get_output_directory()
    prev_temp = folder_paths.get_temp_directory()
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    temp_dir = tmp_path / "temp"
    input_dir.mkdir()
    output_dir.mkdir()
    temp_dir.mkdir()
    folder_paths.set_input_directory(str(input_dir))
    folder_paths.set_output_directory(str(output_dir))
    folder_paths.set_temp_directory(str(temp_dir))
    try:
        yield {"input": input_dir, "output": output_dir, "temp": temp_dir}
    finally:
        folder_paths.set_input_directory(prev_input)
        folder_paths.set_output_directory(prev_output)
        folder_paths.set_temp_directory(prev_temp)


def test_video_execute(node_list, video_directories):
    input_dir = video_directories["input"]
    output_dir = video_directories["output"]
    create_gif(input_dir / "input.gif")
    node = node_list["ComfyUI_ProperPixelArt_Video"]
    main_inputs = dict(
        input_path="input.gif",
        num_colors=0,
        initial_upscale_factor=1,
        pixel_width=0,
        scale_result=1,
        transparent_background=False,
    )
    output = node.execute(
        **main_inputs,
        config=node_list["ComfyUI_ProperPixelArt_Config"]
        .execute(**MODIFIED_INPUTS)
        .result[0],
    )
    assert isinstance(output, comfy_api.io.NodeOutput)
    assert len(output.result) == 1
    assert isinstance(output.result[0], str)
    path = Path(output.result[0])
    assert path.is_file()
    assert path.parent == output_dir
    with Image.open(path) as result:
        assert result.format == "GIF"
        assert result.n_frames == 2
        assert result.width > 1 and result.height > 1
        configured_frame = np.array(result.convert("RGBA"))
    default_output = node.execute(**main_inputs)
    with Image.open(default_output.result[0]) as result:
        assert not np.array_equal(configured_frame, np.array(result.convert("RGBA")))


def test_input_path_traversal_rejected(node_list, video_directories):
    node = node_list["ComfyUI_ProperPixelArt_Video"]
    with pytest.raises(ValueError):
        node.execute(
            input_path="../outside.gif",
            num_colors=0,
            initial_upscale_factor=1,
            pixel_width=0,
            scale_result=1,
            transparent_background=False,
        )


def test_intermediate_dir_traversal_rejected(node_list, image, video_directories):
    pixelate_node = node_list["ComfyUI_ProperPixelArt_Pixelate"]
    with pytest.raises(ValueError):
        pixelate_node.execute(
            image=image,
            num_colors=8,
            initial_upscale_factor=1,
            pixel_width=16,
            scale_result=1,
            transparent_background=False,
            intermediate_dir="../escape",
        )


def test_intermediate_dir_existing_subfolder(node_list, image, video_directories):
    output_dir = video_directories["output"]
    pixelate_node = node_list["ComfyUI_ProperPixelArt_Pixelate"]
    valid_subfolder = output_dir / "inter_steps"
    valid_subfolder.mkdir()
    pixelate_node.execute(
        image=image,
        num_colors=8,
        initial_upscale_factor=1,
        pixel_width=16,
        scale_result=1,
        transparent_background=False,
        intermediate_dir="inter_steps",
    )
    saved_files = list(valid_subfolder.iterdir())
    assert len(saved_files) > 0


def test_intermediate_dir_nonexistent_subfolder(node_list, image, video_directories):
    output_dir = video_directories["output"]
    input_dir = video_directories["input"]

    # Pixelate node with a non-existent subfolder
    pixelate_node = node_list["ComfyUI_ProperPixelArt_Pixelate"]
    new_pixelate_subfolder = output_dir / "new_pixelate_dir"
    assert not new_pixelate_subfolder.exists()
    pixelate_node.execute(
        image=image,
        num_colors=8,
        initial_upscale_factor=1,
        pixel_width=16,
        scale_result=1,
        transparent_background=False,
        intermediate_dir="new_pixelate_dir",
    )
    assert new_pixelate_subfolder.is_dir()
    assert len(list(new_pixelate_subfolder.iterdir())) > 0

    # Video node with a non-existent subfolder
    create_gif(input_dir / "input_for_inter.gif")
    video_node = node_list["ComfyUI_ProperPixelArt_Video"]
    new_video_subfolder = output_dir / "new_video_dir"
    assert not new_video_subfolder.exists()
    video_node.execute(
        input_path="input_for_inter.gif",
        num_colors=0,
        initial_upscale_factor=1,
        pixel_width=0,
        scale_result=1,
        transparent_background=False,
        intermediate_dir="new_video_dir",
    )
    assert new_video_subfolder.is_dir()
    assert len(list(new_video_subfolder.iterdir())) > 0


def test_intermediate_dir_empty_saves_nothing(node_list, image, video_directories):
    output_dir = video_directories["output"]
    pixelate_node = node_list["ComfyUI_ProperPixelArt_Pixelate"]

    initial_items = set(output_dir.iterdir())
    pixelate_node.execute(
        image=image,
        num_colors=8,
        initial_upscale_factor=1,
        pixel_width=16,
        scale_result=1,
        transparent_background=False,
        intermediate_dir="",
    )
    after_items = set(output_dir.iterdir())
    assert initial_items == after_items


@pytest.mark.parametrize(
    "annotated_dir",
    ["sub [input]", "sub [temp]"],
)
@pytest.mark.parametrize(
    "node_key",
    ["ComfyUI_ProperPixelArt_Pixelate", "ComfyUI_ProperPixelArt_Video"],
)
def test_intermediate_dir_annotation_rejected(
    node_list, image, video_directories, node_key, annotated_dir
):
    node = node_list[node_key]
    input_dir = video_directories["input"]
    output_dir = video_directories["output"]
    temp_dir = video_directories["temp"]

    if node_key == "ComfyUI_ProperPixelArt_Video":
        create_gif(input_dir / "sample.gif")
        kwargs = dict(
            input_path="sample.gif",
            num_colors=0,
            initial_upscale_factor=1,
            pixel_width=0,
            scale_result=1,
            transparent_background=False,
            intermediate_dir=annotated_dir,
        )
    else:
        kwargs = dict(
            image=image,
            num_colors=8,
            initial_upscale_factor=1,
            pixel_width=16,
            scale_result=1,
            transparent_background=False,
            intermediate_dir=annotated_dir,
        )

    initial_input = set(input_dir.iterdir())
    initial_output = set(output_dir.iterdir())
    initial_temp = set(temp_dir.iterdir())

    with pytest.raises(ValueError):
        node.execute(**kwargs)

    assert set(input_dir.iterdir()) == initial_input
    assert set(output_dir.iterdir()) == initial_output
    assert set(temp_dir.iterdir()) == initial_temp


def test_docs_drift(node_list):
    root = Path(__file__).resolve().parents[2]
    docs_file = root / "docs" / "nodes.md"
    assert docs_file.is_file(), (
        f"{docs_file} does not exist. Run `just docs` to generate it."
    )

    expected = generate_nodes_markdown(list(node_list.values()))
    actual = docs_file.read_bytes().decode("utf-8")

    # Normalize line endings to LF
    expected_normalized = expected.replace("\r\n", "\n").replace("\r", "\n")
    actual_normalized = actual.replace("\r\n", "\n").replace("\r", "\n")

    assert actual_normalized == expected_normalized, (
        "docs/nodes.md is out of sync with node schemas. Run `just docs` to regenerate it."
    )
