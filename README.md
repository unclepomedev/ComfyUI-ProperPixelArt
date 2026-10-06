# ComfyUI-ProperPixelArt

Unofficial ComfyUI wrapper for [proper-pixel-art](https://github.com/KennethJAllen/proper-pixel-art): "Fixes AI pixel art images, video, or sprite web uploads". Follows upstream behavior.

## Install

Clone into `custom_nodes/` and run `pip install -r requirements.txt`.

## Nodes

See [docs/nodes.md](docs/nodes.md) for detailed inputs and outputs of each node.

- **Proper Pixel Art**: IMAGE to list of RGBA IMAGEs. Each image in a batch is processed independently.
- **Proper Pixel Art Config**: Advanced settings. Connect to `config`.
- **Proper Pixel Art Video / GIF**: Saves to the output directory and returns the path.

## Notes

- Video/GIF: the output directory name must not contain a dot.
