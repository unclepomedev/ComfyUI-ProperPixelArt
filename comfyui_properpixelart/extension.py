from comfy_api.latest import ComfyExtension, io

from .nodes.config import ProperPixelArtConfig
from .nodes.pixelate import ProperPixelArt


class ProperPixelArtExtension(ComfyExtension):
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [ProperPixelArt, ProperPixelArtConfig]


async def comfy_entrypoint() -> ProperPixelArtExtension:
    return ProperPixelArtExtension()
