from comfy_api.latest import io
from proper_pixel_art.config import (
    ColorConfig,
    DominantConfig,
    HoughConfig,
    MeshConfig,
    PaletteConfig,
    PixelateConfig,
)

from ..config_type import PixelateConfigType

DEFAULT_CONFIG = PixelateConfig()


class ProperPixelArtConfig(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        mesh = DEFAULT_CONFIG.mesh
        hough = mesh.hough
        colors = DEFAULT_CONFIG.colors
        palette = colors.palette
        dominant = colors.dominant
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
                io.Boolean.Input(
                    "snap_lines",
                    default=mesh.snap_lines,
                    tooltip="Align detected lines to local edge energy peaks.",
                ),
                io.Float.Input(
                    "snap_search_window_ratio",
                    default=mesh.snap_search_window_ratio,
                    step=0.01,
                    round=False,
                    tooltip="Ratio of estimated pixel width used as snap search half-window.",
                ),
                io.Int.Input(
                    "snap_min_search_window",
                    default=mesh.snap_min_search_window,
                    tooltip="Minimum snap search half-window in pixels.",
                ),
                io.Float.Input(
                    "snap_strength_threshold",
                    default=mesh.snap_strength_threshold,
                    step=0.05,
                    round=False,
                    tooltip="Minimum normalized gradient magnitude along a candidate line to trigger snapping.",
                ),
                io.Int.Input(
                    "anchor_snap_window",
                    default=mesh.anchor_snap_window,
                    tooltip="Search half-window in pixels when snapping the grid origin to an edge anchor.",
                ),
                io.Float.Input(
                    "max_axis_width_ratio",
                    default=mesh.max_axis_width_ratio,
                    step=0.1,
                    round=False,
                    tooltip="Maximum allowed ratio between horizontal and vertical pixel widths.",
                ),
                io.Boolean.Input(
                    "validate_width",
                    default=mesh.validate_width,
                    tooltip="Check estimated grid spacing against edge profile peaks.",
                ),
                io.Float.Input(
                    "width_keep_tolerance",
                    default=mesh.width_keep_tolerance,
                    step=0.1,
                    round=False,
                    tooltip="Relative tolerance within which profile-validated width is preferred.",
                ),
                io.Float.Input(
                    "width_replace_tolerance",
                    default=mesh.width_replace_tolerance,
                    step=0.05,
                    round=False,
                    tooltip="Relative error threshold for replacing an inconsistent grid width.",
                ),
                io.Int.Input(
                    "profile_width_min_gaps",
                    default=mesh.profile_width_min_gaps,
                    tooltip="Minimum number of line gaps required to accept a profile-based width estimate.",
                ),
                io.Float.Input(
                    "split_leftover_fraction",
                    default=mesh.split_leftover_fraction,
                    step=0.05,
                    round=False,
                    tooltip="Fraction of remaining interval length above which a line gap is further split.",
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
                    min=0,
                    max=255,
                    tooltip="Alpha threshold above or equal to which a pixel is considered opaque.",
                ),
                io.Float.Input(
                    "transparency_majority_fraction",
                    default=colors.transparency_majority_fraction,
                    min=0.0,
                    max=1.0,
                    step=0.01,
                    round=False,
                    tooltip="Fraction of transparent pixels in a cell required to treat the cell as transparent.",
                ),
                io.Combo.Input(
                    "quantize_method",
                    options=["MEDIANCUT", "MAXCOVERAGE", "FASTOCTREE"],
                    default=palette.quantize_method,
                    tooltip="PIL.Image.Quantize method name for color quantization.",
                ),
                io.Combo.Input(
                    "dither",
                    options=["NONE", "FLOYDSTEINBERG"],
                    default=palette.dither,
                    tooltip="Dithering mode applied during color quantization.",
                ),
                io.Int.Input(
                    "kmeans",
                    default=palette.kmeans,
                    min=0,
                    tooltip="Number of KMeans iterations for quantization clustering (0 disables KMeans).",
                ),
                io.Int.Input(
                    "bin_size",
                    default=dominant.bin_size,
                    min=1,
                    tooltip="RGB bin size used when clustering dominant cell colors.",
                ),
                io.Int.Input(
                    "merge_distance",
                    default=dominant.merge_distance,
                    min=0,
                    tooltip="Maximum RGB Euclidean distance between colors merged into a single cluster.",
                ),
                io.Combo.Input(
                    "merge_linkage",
                    options=["complete", "average", "single"],
                    default=dominant.merge_linkage,
                    tooltip="Linkage criterion used for hierarchical agglomerative color clustering.",
                ),
                io.Int.Input(
                    "max_linkage_colors",
                    default=dominant.max_linkage_colors,
                    min=2,
                    tooltip="Upper limit on the number of candidate colors before switching to fast merge.",
                ),
                io.Int.Input(
                    "top_colors_limit",
                    default=colors.top_colors_limit,
                    min=1,  # this is from the Web UI
                    tooltip="Number of common opaque colors sampled when picking a background color.",
                ),
                io.Int.Input(
                    "thumbnail_w",
                    default=colors.thumbnail_size[0],
                    min=1,
                    tooltip="Width downscale size for color analysis.",
                ),
                io.Int.Input(
                    "thumbnail_h",
                    default=colors.thumbnail_size[1],
                    min=1,
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
    def execute(
        cls,
        crop_border_pixels: int,
        canny_low: int,
        canny_high: int,
        closure_kernel_size: int,
        cluster_threshold: int,
        angle_threshold_deg: float,
        trim_outlier_fraction: float,
        snap_lines: bool,
        snap_search_window_ratio: float,
        snap_min_search_window: int,
        snap_strength_threshold: float,
        anchor_snap_window: int,
        max_axis_width_ratio: float,
        validate_width: bool,
        width_keep_tolerance: float,
        width_replace_tolerance: float,
        profile_width_min_gaps: int,
        split_leftover_fraction: float,
        rho: float,
        theta_deg: float,
        hough_threshold: int,
        min_line_len: int,
        max_line_gap: int,
        alpha_threshold: int,
        transparency_majority_fraction: float,
        quantize_method: str,
        dither: str,
        kmeans: int,
        bin_size: int,
        merge_distance: int,
        merge_linkage: str,
        max_linkage_colors: int,
        top_colors_limit: int,
        thumbnail_w: int,
        thumbnail_h: int,
    ) -> io.NodeOutput:
        hough = HoughConfig(
            rho=rho,
            theta_deg=theta_deg,
            threshold=hough_threshold,
            min_line_len=min_line_len,
            max_line_gap=max_line_gap,
        )
        mesh = MeshConfig(
            crop_border_pixels=crop_border_pixels,
            canny_thresholds=(canny_low, canny_high),
            closure_kernel_size=closure_kernel_size,
            cluster_threshold=cluster_threshold,
            angle_threshold_deg=angle_threshold_deg,
            trim_outlier_fraction=trim_outlier_fraction,
            snap_lines=snap_lines,
            snap_search_window_ratio=snap_search_window_ratio,
            snap_min_search_window=snap_min_search_window,
            snap_strength_threshold=snap_strength_threshold,
            anchor_snap_window=anchor_snap_window,
            max_axis_width_ratio=max_axis_width_ratio,
            validate_width=validate_width,
            width_keep_tolerance=width_keep_tolerance,
            width_replace_tolerance=width_replace_tolerance,
            profile_width_min_gaps=profile_width_min_gaps,
            split_leftover_fraction=split_leftover_fraction,
            hough=hough,
        )
        palette = PaletteConfig(
            num_colors=DEFAULT_CONFIG.colors.palette.num_colors,
            quantize_method=quantize_method,
            dither=dither,
            kmeans=kmeans,
        )
        dominant = DominantConfig(
            bin_size=bin_size,
            merge_distance=merge_distance,
            merge_linkage=merge_linkage,
            max_linkage_colors=max_linkage_colors,
        )
        colors = ColorConfig(
            method=DEFAULT_CONFIG.colors.method,
            alpha_threshold=alpha_threshold,
            transparency_majority_fraction=transparency_majority_fraction,
            top_colors_limit=top_colors_limit,
            thumbnail_size=(thumbnail_w, thumbnail_h),
            background_candidates=None,
            palette=palette,
            dominant=dominant,
        )
        config = PixelateConfig(
            mesh=mesh,
            colors=colors,
        )
        return io.NodeOutput(config)
