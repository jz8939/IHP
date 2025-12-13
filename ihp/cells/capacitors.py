"""Capacitor components for IHP PDK."""

import gdsfactory as gf
from gdsfactory import Component
from gdsfactory.typings import LayerSpec, LayerSpecs

import math

def add_rect(component, size: tuple[float, float], layer: LayerSpec, origin: tuple[float, float], centered: bool = False):
    """Create rectangle, add ref to component and move to origin, return ref."""
    rect = gf.components.rectangle(size=size, layer=layer, centered=centered)
    ref = component.add_ref(rect)
    ref.move(origin)
    return ref


@gf.cell
def cmim(
    width: float = 6.99,
    length: float = 6.99,
    capacitance: float | None = None,
    model: str = "cmim",
    layer_metal5: LayerSpec = "Metal5drawing",
    layer_mim: LayerSpec = "MIMdrawing",
    layer_topmetal1: LayerSpec = "TopMetal1drawing",
    layer_vmim: LayerSpec = "Vmimdrawing",
) -> Component:
    """Create an MIM (Metal-Insulator-Metal) capacitor.

    Args:
        width: MIM plate X-size (um). Scales the MIM/top-plate in X.
        length: MIM plate Y-size (um). Scales the MIM/top-plate in Y.
        capacitance: Optional (kept for compatibility; not used for geometry).
        model: Device model name stored in metadata.
        layer_metal5: Metal5 drawing layer.
        layer_mim: MIM dielectric layer.
        layer_topmetal1: TopMetal1 drawing layer.
        layer_vmim: Vmimdrawing (small tile) layer.

    Returns:
        MIM capacitor component.
    """
    c = Component()

    # Geometrical constants
    METAL_5_MIM_MARGIN = 0.6
    METAL_1_MIM_MARGIN = 0.34
    VMIM_TILE_LENGTH = 0.42
    VMIM_TILE_GAP = 0.84
    GRID_STEP = 0.005

    tile_pitch = VMIM_TILE_LENGTH + VMIM_TILE_GAP

    # Grid snapping
    length = round(length / GRID_STEP) * GRID_STEP
    width = round(width / GRID_STEP) * GRID_STEP

    # Calculate capacitance
    if capacitance is None:
        CAP_DENSITY = 1.54
        area = width * length
        capacitance = area * CAP_DENSITY

    # Draw MIM layer
    add_rect(c, size=(width, length), layer=layer_mim, origin=(0.0, 0.0))

    # Draw Metal5 bottom plate (bigger by METAL_5_MIM_MARGIN)
    metal_5_size_x = width + 2 * METAL_5_MIM_MARGIN
    metal_5_size_y = length + 2 * METAL_5_MIM_MARGIN
    add_rect(
        c,
        size=(metal_5_size_x, metal_5_size_y),
        layer=layer_metal5,
        origin=(-METAL_5_MIM_MARGIN, -METAL_5_MIM_MARGIN),
    )

    # Calculate how many tiles fit in X and Y
    n_tiles_x = int(
        max(
            math.floor((width - 2 * METAL_1_MIM_MARGIN + VMIM_TILE_GAP) / (tile_pitch)),
            0,
        )
    )
    n_tiles_y = int(
        max(
            math.floor((length - 2 * METAL_1_MIM_MARGIN + VMIM_TILE_GAP) / (tile_pitch)),
            0,
        )
    )

    # Compute occupied size of the tile array (including gaps and the edge overlaps)
    occupied_x = (n_tiles_x * (
                tile_pitch) - VMIM_TILE_GAP) + 2 * METAL_1_MIM_MARGIN if n_tiles_x > 0 else 0.0
    occupied_y = (n_tiles_y * (
                tile_pitch) - VMIM_TILE_GAP) + 2 * METAL_1_MIM_MARGIN if n_tiles_y > 0 else 0.0

    # Offsets to center tile array inside the MIM plate, snapped to grid
    x_offset = round(((width - occupied_x) / 2.0) / GRID_STEP) * GRID_STEP - 0.005
    y_offset = round(((length - occupied_y) / 2.0) / GRID_STEP) * GRID_STEP - 0.005

    x_start = METAL_1_MIM_MARGIN + x_offset
    y_start = METAL_1_MIM_MARGIN + y_offset

    # Draw Vmim grid
    for y_iter in range(n_tiles_y):
        y_current = y_start + y_iter * tile_pitch
        x_current = x_start
        for x_iter in range(n_tiles_x):
            add_rect(
                c,
                size=(VMIM_TILE_LENGTH, VMIM_TILE_LENGTH),
                layer=layer_vmim,
                origin=(x_current, y_current),
            )
            x_current = x_current + tile_pitch

    # Derive coordinates of top right corner
    metal_1_x2 = x_start + (n_tiles_x - 1) * tile_pitch + VMIM_TILE_LENGTH + VMIM_TILE_GAP / 2.0
    metal_1_y2 = y_start + (n_tiles_y - 1) * tile_pitch + VMIM_TILE_LENGTH + VMIM_TILE_GAP / 2.0

    # Derive coordinates of left bottom right corner
    metal_1_x1 = METAL_1_MIM_MARGIN + x_offset - VMIM_TILE_GAP / 2.0
    metal_1_y1 = METAL_1_MIM_MARGIN + y_offset - VMIM_TILE_GAP / 2.0

    # Draw TopMetal1 covering the tile-array area (always used; no fallback)
    add_rect(
        c,
        size=(metal_1_x2 - metal_1_x1, metal_1_y2 - metal_1_y1),
        layer=layer_topmetal1,
        origin=(metal_1_x1, metal_1_y1),
    )

    # Add ports
    plus_center = ((metal_1_x1 + metal_1_x2) / 2.0, (metal_1_y1 + metal_1_y2) / 2.0)
    c.add_port(
        name="PLUS",
        center=plus_center,
        width=min(metal_1_x2 - metal_1_x1, metal_1_y2 - metal_1_y1),
        orientation=0,
        layer=layer_topmetal1,
        port_type="electrical",
    )

    minus_center = (-METAL_5_MIM_MARGIN + metal_5_size_x / 2.0, -METAL_5_MIM_MARGIN + metal_5_size_y / 2.0)
    c.add_port(
        name="MINUS",
        center=minus_center,
        width=min(metal_5_size_x, metal_5_size_y),
        orientation=180,
        layer=layer_metal5,
        port_type="electrical",
    )

    # Metadata
    c.info.update(
        {
            "model": model,
            "capacitance": capacitance,
            "mim_length": length,
            "mim_width": width,
            "vmim_tile_length": VMIM_TILE_LENGTH,
            "n_vmim_tiles": (n_tiles_x, n_tiles_y)
        }
    )

    return c


@gf.cell
def rfcmim(
    width: float = 7.0,
    length: float = 7.0,
    capacitance: float | None = None,
    model: str = "rfcmim",
    layer_activ: LayerSpec = "Activdrawing",
    layer_mim: LayerSpec = "MIMdrawing",
    layer_metal1: LayerSpec = "Metal1drawing",
    layer_metal1_pin: LayerSpec = "Metal1pin",
    layer_metal5: LayerSpec = "Metal5drawing",
    layer_metal5_pin: LayerSpec = "Metal5pin",
    layer_topmetal1: LayerSpec = "TopMetal1drawing",
    layer_topmetal1_pin: LayerSpec = "TopMetal1pin",
    layer_vmim: LayerSpec = "Vmimdrawing",
    layer_cont: LayerSpec = "Contdrawing",
    layer_psd: LayerSpec = "pSDdrawing",
    layer_pwellblock: LayerSpec = "PWellblock",
    layers_no_qrc: LayerSpecs = (
        "Activnoqrc",
        "TopMetal1noqrc",
        "Metal1noqrc",
        "Metal2noqrc",
        "Metal3noqrc",
        "Metal4noqrc",
        "Metal5noqrc",
    ),
) -> Component:
    """
    Create an RF MIM capacitor (empty scaffold).

    Args:
        width: Capacitor width in micrometers.
        length: Capacitor length in micrometers.
        capacitance: Target capacitance in fF (optional).
        model: Model name for metadata.
        layer_activ: Active diffusion drawing layer.
        layer_mim: MIM dielectric layer.
        layer_metal1: Metal1 drawing layer.
        layer_metal1_pin: Metal1 pin layer.
        layer_metal5: Metal5 drawing layer.
        layer_metal5_pin: Metal5 pin layer.
        layer_topmetal1: TopMetal1 drawing layer.
        layer_topmetal1_pin: TopMetal1 pin layer.
        layer_vmim: Vmim tile layer.
        layer_cont: Contact drawing layer.
        layer_psd: P-sub diffusion drawing layer.
        layer_pwellblock: P-well block mask.
        layers_no_qrc: No quantitative RC extraction layers

    Returns:
        Model of RF MIM capacitor
    """
    c = Component()

    # Geometrical constants
    MIM_METAL_5_MARGIN = 0.6
    MIM_PWELL_MARGIN = 3
    NO_QRC_PWELL_MARGIN = 2.6

    # Grid snapping
    length = round(length / 0.005) * 0.005
    width = round(width / 0.005) * 0.005

    # Calculate capacitance
    if capacitance is None:
        CAP_DENSITY = 1.54
        area = width * length
        capacitance = area * CAP_DENSITY

    # MIM layer
    add_rect(c, (length, width), layer_mim, origin=(0, 0))

    # PWell block layer
    p_well_length = 2 * MIM_PWELL_MARGIN + length
    p_well_width = 2 * MIM_PWELL_MARGIN + width
    p_well_corner = (-MIM_PWELL_MARGIN, -MIM_PWELL_MARGIN)
    add_rect(c, (p_well_length, p_well_width), layer_pwellblock, origin=p_well_corner)

    # No QRC layers
    no_qrc_length = 2 * (MIM_PWELL_MARGIN + NO_QRC_PWELL_MARGIN) + length
    no_qrc_width = 2 * (MIM_PWELL_MARGIN + NO_QRC_PWELL_MARGIN) + width
    no_qrc_corner = (-MIM_PWELL_MARGIN - NO_QRC_PWELL_MARGIN, -MIM_PWELL_MARGIN - NO_QRC_PWELL_MARGIN)
    for layer in layers_no_qrc:
        add_rect(c, (no_qrc_length, no_qrc_width), layer, origin=no_qrc_corner)

    # Metal5 layer
    metal_5_length = 2 * MIM_METAL_5_MARGIN + length
    metal_5_width = 2 * MIM_METAL_5_MARGIN + width
    metal_5_corner = (-MIM_METAL_5_MARGIN, -MIM_METAL_5_MARGIN)
    add_rect(c, (metal_5_length, metal_5_width), layer_metal5, origin=metal_5_corner)


    return c


if __name__ == "__main__":
    from gdsfactory.difftest import xor

    from ihp import PDK, cells2

    PDK.activate()

    # Test the components
    c0 = cells2.cmim(width=6.99, length=6.99)  # original
    c1 = cmim(width=6.99, length=6.99)  # New
    c = xor(c0, c1)
    c.show()

    # c0 = fixed.rfcmim()  # original
    # c1 = rfcmim()  # New
    # c = xor(c0, c1)
    # c.show()
