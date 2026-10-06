# ComfyUI-ProperPixelArt

Unofficial ComfyUI wrapper for [proper-pixel-art](https://github.com/KennethJAllen/proper-pixel-art): "Fixes AI pixel art images, video, or sprite web uploads". Follows upstream behavior.

## Install

Clone into `custom_nodes/` and run `pip install -r requirements.txt`.

## Nodes

See [docs/nodes.md](docs/nodes.md) for detailed inputs and outputs of each node.

- **Proper Pixel Art**: IMAGE to RGBA IMAGE. Only the first image of a batch is processed.
- **Proper Pixel Art Config**: Advanced settings. Connect to `config`.
- **Proper Pixel Art Video / GIF**: Saves to the output directory and returns the path.

## Notes

- `input_path` and `intermediate_dir` are server-side paths with no restriction; use only with trusted workflow users.
- Video/GIF: the output directory name must not contain a dot.
