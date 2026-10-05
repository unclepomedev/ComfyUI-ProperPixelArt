from comfy_api.latest import ComfyExtension, io

from .nodes.config import ProperPixelArtConfig
from .nodes.pixelate import ProperPixelArt
from .nodes.video import ProperPixelArtVideo


class ProperPixelArtExtension(ComfyExtension):
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [ProperPixelArt, ProperPixelArtConfig, ProperPixelArtVideo]


async def comfy_entrypoint() -> ProperPixelArtExtension:
    return ProperPixelArtExtension()
