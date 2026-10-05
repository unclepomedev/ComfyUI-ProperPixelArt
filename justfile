default:
	@just --list

fmt:
    uv run ruff format comfyui_properpixelart tests

lintfix:
    uv run ruff check --fix
lf: lintfix

test:
    uv run pytest

PYTHON_VERSION := "3.13"
[env('PYTHONPATH', justfile_directory() / '.cache/ComfyUI')]
[env('REQUIRE_COMFYUI', '1')]
comfyui-test ref="v0.38.2":
    git init .cache/ComfyUI
    git -C .cache/ComfyUI fetch --depth 1 https://github.com/comfyanonymous/ComfyUI.git {{quote(ref)}}
    git -C .cache/ComfyUI checkout --detach FETCH_HEAD
    uv venv --allow-existing --python {{ PYTHON_VERSION }} .cache/comfyui-venv
    uv pip install --python .cache/comfyui-venv --torch-backend cpu -r .cache/ComfyUI/requirements.txt -r requirements.txt pytest
    uv run --no-project --python .cache/comfyui-venv python -m pytest tests/comfyui -v

test-all: test comfyui-test
