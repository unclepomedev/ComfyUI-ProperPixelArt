default:
	@just --list

fmt:
    uv run ruff format comfyui_properpixelart tests

lintfix:
    uv run ruff check --fix
lf: lintfix

test:
    uv run pytest

comfyui-test ref="v0.38.2":
    #!/usr/bin/env bash
    set -euo pipefail
    mkdir -p .cache
    if [ ! -d .cache/ComfyUI/.git ]; then
        git init .cache/ComfyUI
        git -C .cache/ComfyUI remote add origin https://github.com/comfyanonymous/ComfyUI.git
    fi
    git -C .cache/ComfyUI fetch --depth 1 origin {{quote(ref)}}
    git -C .cache/ComfyUI checkout --detach FETCH_HEAD
    if [ ! -x .cache/comfyui-venv/bin/python ]; then
        uv venv --python 3.13 .cache/comfyui-venv
    fi
    uv pip install --python .cache/comfyui-venv/bin/python --torch-backend cpu -r .cache/ComfyUI/requirements.txt
    uv pip install --python .cache/comfyui-venv/bin/python pytest -r requirements.txt
    PYTHONPATH="$PWD/.cache/ComfyUI" REQUIRE_COMFYUI=1 .cache/comfyui-venv/bin/python -m pytest tests/comfyui -v
