import os

import folder_paths


def resolve_intermediate_dir(intermediate_dir: str) -> str:
    """Resolve intermediate_dir under ComfyUI output directory."""
    if not intermediate_dir:
        return ""

    output_dir = folder_paths.get_output_directory()
    resolved_path = folder_paths.get_annotated_filepath(
        intermediate_dir,
        default_dir=output_dir,
    )
    if not folder_paths.is_within_directory(output_dir, resolved_path):
        raise ValueError(f"Invalid file path: {intermediate_dir!r}")

    os.makedirs(resolved_path, exist_ok=True)
    return resolved_path
