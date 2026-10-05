default:
	@just --list

fmt:
    uv run ruff format comfyui_properpixelart tests

test:
    uv run pytest
