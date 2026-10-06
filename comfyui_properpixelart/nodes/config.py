from comfy_api.latest import io
from proper_pixel_art.config import PixelateConfig
from proper_pixel_art.web import build_config

from ..config_type import PixelateConfigType

DEFAULT_CONFIG = PixelateConfig()


class ProperPixelArtConfig(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        mesh = DEFAULT_CONFIG.mesh
        hough = mesh.hough
        colors = DEFAULT_CONFIG.colors
        return io.Schema(
            node_id="ComfyUI_ProperPixelArt_Config",
            display_name="Proper Pixel Art Config",
            category="image/Proper Pixel Art",
            inputs=[
                io.Int.Input(
                    "crop_border_pixels",
                    default=mesh.crop_border_pixels,
                    tooltip="Number of border pixels trimmed before edge detection.",
                ),
                io.Int.Input(
                    "canny_low",
                    default=mesh.canny_thresholds[0],
                    tooltip="Lower Canny edge detection threshold.",
                ),
                io.Int.Input(
                    "canny_high",
                    default=mesh.canny_thresholds[1],
                    tooltip="Upper Canny edge detection threshold.",
                ),
                io.Int.Input(
                    "closure_kernel_size",
                    default=mesh.closure_kernel_size,
                    tooltip="Kernel size for morphological closing.",
                ),
                io.Int.Input(
                    "cluster_threshold",
                    default=mesh.cluster_threshold,
                    tooltip="Maximum distance in pixels to merge nearby grid lines.",
                ),
                io.Float.Input(
                    "angle_threshold_deg",
                    default=mesh.angle_threshold_deg,
                    step=1,
                    round=False,
                    tooltip="Tolerance angle in degrees for accepting vertical and horizontal lines.",
                ),
                io.Float.Input(
                    "trim_outlier_fraction",
                    default=mesh.trim_outlier_fraction,
                    step=0.01,
                    round=False,
                    tooltip="Tail fraction of grid gap outliers trimmed when estimating pixel width.",
                ),
                io.Float.Input(
                    "rho",
                    default=hough.rho,
                    step=0.1,
                    round=False,
                    tooltip="Hough transform distance resolution in pixels.",
                ),
                io.Float.Input(
                    "theta_deg",
                    default=hough.theta_deg,
                    step=0.1,
                    round=False,
                    tooltip="Hough transform angle resolution in degrees.",
                ),
                io.Int.Input(
                    "hough_threshold",
                    default=hough.threshold,
                    tooltip="Minimum accumulator votes to accept a line in Hough transform.",
                ),
                io.Int.Input(
                    "min_line_len",
                    default=hough.min_line_len,
                    tooltip="Minimum line length in pixels to accept in Hough transform.",
                ),
                io.Int.Input(
                    "max_line_gap",
                    default=hough.max_line_gap,
                    tooltip="Maximum gap between line segments in pixels to join them in Hough transform.",
                ),
                io.Int.Input(
                    "alpha_threshold",
                    default=colors.alpha_threshold,
                    tooltip="Alpha threshold above or equal to which a pixel is considered opaque.",
                ),
                io.Float.Input(
                    "transparency_majority_fraction",
                    default=colors.transparency_majority_fraction,
                    step=0.01,
                    round=False,
                    tooltip="Fraction of transparent pixels in a cell required to treat the cell as transparent.",
                ),
                io.Combo.Input(
                    "quantize_method",
                    options=["MEDIANCUT", "MAXCOVERAGE", "FASTOCTREE"],
                    default=colors.quantize_method,
                    tooltip="PIL.Image.Quantize method name for color quantization.",
                ),
                io.Int.Input(
                    "bin_size",
                    default=colors.bin_size,
                    min=1,
                    tooltip="RGB bin size used when finding dominant colors without quantization.",
                ),
                io.Int.Input(
                    "top_colors_limit",
                    default=colors.top_colors_limit,
                    tooltip="Number of common opaque colors sampled when picking a background color.",
                ),
                io.Int.Input(
                    "thumbnail_w",
                    default=colors.thumbnail_size[0],
                    tooltip="Width downscale size for color analysis.",
                ),
                io.Int.Input(
                    "thumbnail_h",
                    default=colors.thumbnail_size[1],
                    tooltip="Height downscale size for color analysis.",
                ),
            ],
            outputs=[
                PixelateConfigType.Output(
                    display_name="config",
                    tooltip="Advanced configuration object for Proper Pixel Art nodes.",
                )
            ],
        )

    @classmethod
    def execute(cls, **kwargs) -> io.NodeOutput:
        return io.NodeOutput(
            build_config(
                num_colors=DEFAULT_CONFIG.num_colors,
                initial_upscale_factor=DEFAULT_CONFIG.initial_upscale_factor,
                pixel_width=DEFAULT_CONFIG.pixel_width,
                scale_result=DEFAULT_CONFIG.scale_result,
                transparent_background=DEFAULT_CONFIG.transparent_background,
                **kwargs,
            ),
        )
