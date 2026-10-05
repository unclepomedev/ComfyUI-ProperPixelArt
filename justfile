default:
	@just --list

fmt:
    uv run ruff format comfyui_properpixelart tests

lintfix:
    uv run ruff check --fix
lf: lintfix

test:
    uv run pytest
