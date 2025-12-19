"""Capacitor components for IHP PDK."""

import gdsfactory as gf
from gdsfactory import Component
from gdsfactory.typings import LayerSpec


@gf.cell
def cmim(
    width: float = 5.0,
    length: float = 5.0,
    capacitance: float | None = None,
    model: str = "cmim",
    layer_metal4: LayerSpec = "Metal4drawing",
    layer_metal5: LayerSpec = "Metal5drawing",
    layer_mim: LayerSpec = "MIMdrawing",
    layer_via4: LayerSpec = "Via4drawing",
    layer_via_mim: LayerSpec = "Vmimdrawing",
    layer_topmetal1: LayerSpec = "TopMetal1drawing",
    layer_topvia1: LayerSpec = "TopVia1drawing",
    layer_cap_mark: LayerSpec = "MemCapdrawing",
    layer_nofill: LayerSpec = "Metal4nofill",
) -> Component:
    """Create a MIM (Metal-Insulator-Metal) capacitor.

    Args:
        width: Width of the capacitor in micrometers.
        length: Length of the capacitor in micrometers.
        capacitance: Target capacitance in fF (optional).
        model: Device model name.
        layer_metal4: Bottom plate metal layer.
        layer_metal5: Top plate metal layer.
        layer_mim: MIM dielectric layer.
        layer_via4: Via layer for top plate connection.
        layer_topmetal1: Top metal layer for connections.
        layer_topvia1: Via to top metal layer.
        layer_cap_mark: Capacitor marker layer.
        layer_nofill: No metal filler layer.

    Returns:
        Component with MIM capacitor layout.
    """
    c = Component()

    # Design rules
    mim_min_size = 0.5
    via_dim = 0.42  # Extracted from PDK
    via_spacing = 2*via_dim # Extracted from PDK
    via_extension = via_dim # Extracted from PDK
    bottom_plate_extension = 0.6 # Extracted from PDK
    cap_density = 1.5  # fF/um^2 (example value)

    # Validate dimensions
    width = max(width, mim_min_size)
    length = max(length, mim_min_size)

    # Grid snap
    grid = 0.005
    width = round(width / grid) * grid
    length = round(length / grid) * grid

    # Calculate capacitance if not provided
    if capacitance is None:
        capacitance = width * length * cap_density

    # Bottom plate (Metal4)
    bottom_plate_width = width + 2 * bottom_plate_extension
    bottom_plate_length = length + 2 * bottom_plate_extension

    bottom_plate = c << gf.components.rectangle(
        size=(bottom_plate_width, bottom_plate_length),
        layer=layer_metal5,
    )
    bottom_plate.xmin=-bottom_plate_extension
    bottom_plate.ymin=-bottom_plate_extension

    # MIM dielectric layer
    mim_layer = c << gf.components.rectangle(
        size=(width, length),
        layer=layer_mim,
    )

    # The top plate is an extension of the via array, so we create it after the vias.
    # First, the number of vias needs to be defined. They are squares of via_dim, and spacing via_spacing.
    # Let's assume we have a grid of n_x by n_y vias. The top plate will extend this array by via_extension on each side.
    # So the length of the top plate will be:
    # L_top = n_x*via_dim + (n_x-1)*via_spacing + 2*via_extension = 3*n_x*via_dim, for spacing = 2*via_dim and extension = via_dim.
    # The PDK gives the maximum vias for which the top plate dimensions do not exceed the insulator dimensions by more than 0.115um.

    # Via array for top plate connection
    n_vias_x = 1
    n_vias_y = 1

    top_electrode_width = 3 * n_vias_x * via_dim
    top_electrode_length = 3 * n_vias_y * via_dim

    # This condition was found empirically to match the PDK layout
    while top_electrode_width + 3*via_dim < width + 0.115:
        n_vias_x += 1
        top_electrode_width = 3 * n_vias_x * via_dim
    while top_electrode_length + 3*via_dim < length + 0.115:
        n_vias_y += 1
        top_electrode_length = 3 * n_vias_y * via_dim


    for i in range(n_vias_x):
        for j in range(n_vias_y):
            # The bottom left corner of the top electrode is at (width - top_electrode_width)/2 - 0.005, (length - top_electrode_length)/2 - 0.005
            x = (width - top_electrode_width)/2 - 0.005 + via_extension + i*(via_dim + via_spacing)
            y = (length - top_electrode_length)/2 - 0.005 + via_extension + j*(via_dim + via_spacing)

            via = gf.components.rectangle(
                size=(via_dim, via_dim),
                layer=layer_via_mim,
            )
            via_ref = c.add_ref(via)
            via_ref.move((x, y))

    # Top plate (Metal5)
    top_plate = c << gf.components.rectangle(
        size=(top_electrode_width, top_electrode_length),
        layer=layer_topmetal1,
    )
    top_plate.xmin = (width - top_electrode_width)/2 - 0.005
    top_plate.ymin = (length - top_electrode_length)/2 - 0.005

    # Add ports
    c.add_port(
        name="B",
        center=(width/2, length/2),
        width=width + 2 * bottom_plate_extension,
        orientation=0,
        layer=layer_metal5,
        port_type="electrical",
    )

    c.add_port(
        name="T",
        center=(top_plate.x, top_plate.y),
        width=top_electrode_width,
        orientation=180,
        layer=layer_topmetal1,
        port_type="electrical",
    )

    # Add metadata
    c.info["model"] = model
    c.info["width"] = width
    c.info["length"] = length
    c.info["capacitance_fF"] = capacitance
    c.info["area_um2"] = width * length

    return c


@gf.cell
def rfcmim(
    width: float = 10.0,
    length: float = 10.0,
    capacitance: float | None = None,
    model: str = "rfcmim",
    layer_activ: LayerSpec = "Activdrawing",
    layer_cont: LayerSpec = "Contdrawing",
    layer_metal1: LayerSpec = "Metal1drawing",
    layer_metal1_pin: LayerSpec = "Metal1pin",
    layer_metal2: LayerSpec = "Metal2drawing",
    layer_psd: LayerSpec = "pSDdrawing",
    layer_metal3: LayerSpec = "Metal3drawing",
    layer_mim: LayerSpec = "MIMdrawing",
    layer_pwell: LayerSpec = "PWelldrawing",
    layer_metal4: LayerSpec = "Metal4drawing",
    layer_text: LayerSpec = "TEXTdrawing",
    layer_metal5: LayerSpec = "Metal5drawing",
    layer_metal5_pin: LayerSpec = "Metal5pin",
    layer_topmetal1: LayerSpec = "TopMetal1drawing",
    layer_topmetal1_pin: LayerSpec = "TopMetal1pin",
    layer_topvia1: LayerSpec = "TopVia1drawing",
    layer_via_mim: LayerSpec = "Vmimdrawing",
) -> Component:
    """Create an RF MIM capacitor with optimized layout.

    Args:
        width: Width of the capacitor in micrometers.
        length: Length of the capacitor in micrometers.
        capacitance: Target capacitance in fF (optional).
        model: Device model name.
        layer_metal3: Ground shield metal layer.
        layer_metal4: Bottom plate metal layer.
        layer_metal5: Top plate metal layer.
        layer_mim: MIM dielectric layer.
        layer_via4: Via layer for top plate connection.
        layer_topmetal1: Top metal layer for connections.
        layer_topvia1: Via to top metal layer.
        layer_rfpad: RF pad marker layer.
        layer_cap_mark: Capacitor marker layer.

    Returns:
        Component with RF MIM capacitor layout.
    """
    c = Component()

    # Design rules for RF capacitor
    mim_min_size = 5.0  # Larger minimum for RF
    via_dim = 0.42  # Extracted from PDK
    via_spacing = 0.44 # Extracted from PDK
    via_extension = 0.78 # Extracted from PDK
    cont_dim = 0.16 # Contact dimension from PDK
    cont_spacing_x = 0.185 # Contact spacing from PDK
    cont_spacing_y = 0.215 # Contact spacing from PDK
    cont_extension = 0.36 # Contact extension from PDK
    psd_extra_extension = 0.03 # Additional extension for pSD layer
    pwell_extension = 3.0
    cap_density = 1.5  # fF/um^2
    activ_external_extension = 5.6
    activ_internal_extension = 3.6
    metal5_extension = 0.6
    shield_width = width + 4.0
    shield_length = length + 4.0
    bottom_plate_length = length + 2.0
    shield_enclosure = 2.0

    # Validate dimensions
    width = max(width, mim_min_size)
    length = max(length, mim_min_size)

    # Grid snap
    grid = 0.005
    width = round(width / grid) * grid
    length = round(length / grid) * grid

    # Calculate capacitance if not provided
    if capacitance is None:
        capacitance = width * length * cap_density

    # MIM dielectric layer
    mim_layer = c << gf.components.rectangle(
        size=(length, width),
        layer=layer_mim,
    )

    # The top plate is an extension of the via array, so we create it after the vias.
    # First, the number of vias needs to be defined. They are squares of via_dim, and spacing via_spacing.
    # Let's assume we have a grid of n_x by n_y vias. The top plate will extend this array by via_extension on each side.
    # So the length of the top plate will be:
    # L_top = n_x*via_dim + (n_x-1)*via_spacing + 2*via_extension = 3*n_x*via_dim, for spacing = 2*via_dim and extension = via_dim.
    # The PDK gives the maximum vias for which the top plate dimensions do not exceed the insulator dimensions by more than 0.115um.

    # Via array for top plate connection
    n_vias_x = 1
    n_vias_y = 1

    top_electrode_length = n_vias_x * via_dim + (n_vias_x - 1) * via_spacing + 2 * via_extension
    top_electrode_width = n_vias_y * via_dim + (n_vias_y - 1) * via_spacing + 2 * via_extension

    # The addition of a grid point results in extension by via_dim + via_spacing
    # This condition was found empirically to match the PDK layout
    via_spacing_x = via_spacing
    via_spacing_y = via_spacing
    while top_electrode_length + via_dim + via_spacing < length + 0.115:
        n_vias_x += 1
        top_electrode_length = n_vias_x * via_dim + (n_vias_x - 1) * via_spacing + 2 * via_extension
    while top_electrode_length < length:
        via_spacing_x += 0.005
        top_electrode_length = n_vias_x * via_dim + (n_vias_x - 1) * via_spacing_x + 2 * via_extension

    while top_electrode_width + via_dim + via_spacing < width + 0.115:
        n_vias_y += 1
        top_electrode_width = n_vias_y * via_dim + (n_vias_y - 1) * via_spacing + 2 * via_extension
    while top_electrode_width < width:
        via_spacing_y += 0.005
        top_electrode_width = n_vias_y * via_dim + (n_vias_y - 1) * via_spacing_y + 2 * via_extension

    for i in range(n_vias_x):
        for j in range(n_vias_y):
            # The bottom left corner of the top electrode is at (width - top_electrode_width)/2 - 0.005, (length - top_electrode_length)/2 - 0.005
            x = via_extension + i*(via_dim + via_spacing_x)
            y = via_extension + j*(via_dim + via_spacing_y)
            via = gf.components.rectangle(
                size=(via_dim, via_dim),
                layer=layer_via_mim,
            )
            via_ref = c.add_ref(via)
            via_ref.move((x, y))

    # ----------------
    # Active Drawing
    # ----------------
    activ = c << gf.components.rectangle(
        size=(length + 2*activ_external_extension, width + 2*activ_external_extension),
        layer=layer_activ,
    )
    activ.xmin = -activ_external_extension
    activ.ymin = -activ_external_extension

    c.add_polygon(
        [
            (-activ_internal_extension, -activ_internal_extension),
            (-activ_internal_extension, width + activ_internal_extension),
            (length + activ_internal_extension, width + activ_internal_extension),
            (length + activ_internal_extension, width/2 + 1.5),
            (length + activ_external_extension, width/2 + 1.5),
            (length + activ_external_extension, width/2 - 1.5),
            (length + activ_internal_extension, width/2 - 1.5),
            (length + activ_internal_extension, -activ_internal_extension),
        ],
        layer=layer_activ,
    )

    # ----------------
    # Cont Drawing
    # ----------------

    # Top and bottom extension
    n_cont_x = 1
    n_cont_y = 1

    top_length = n_cont_x * cont_dim + (n_cont_x - 1) * cont_spacing_x + 2 * cont_extension
    top_width = n_cont_y * cont_dim + (n_cont_y - 1) * cont_spacing_y + 2 * cont_extension
    # The addition of a grid point results in extension by via_dim + via_spacing
    # This condition was found empirically to match the PDK layout

    while top_length + cont_dim + cont_spacing_x < length + 2*activ_external_extension + 0.115:
        n_cont_x += 1
        top_length = n_cont_x * cont_dim + (n_cont_x - 1) * cont_spacing_x + 2 * cont_extension

    while top_width + cont_dim + cont_spacing_y < activ_external_extension - activ_internal_extension + 0.115:
        n_cont_y += 1
        top_width = n_cont_y * cont_dim + (n_cont_y - 1) * cont_spacing_y + 2 * cont_extension

    for i in range(n_cont_x):
        for j in range(n_cont_y):
            x = - activ_external_extension + cont_extension + i*(cont_dim + cont_spacing_x)
            y = width + activ_internal_extension + cont_extension + j*(cont_dim + cont_spacing_y)
            cont = gf.components.rectangle(
                size=(cont_dim, cont_dim),
                layer=layer_cont,
            )
            cont_ref = c.add_ref(cont)
            cont_ref.move((x, y))

            y = - activ_external_extension + cont_extension + j*(cont_dim + cont_spacing_y)
            cont = gf.components.rectangle(
                size=(cont_dim, cont_dim),
                layer=layer_cont,
            )
            cont_ref = c.add_ref(cont)
            cont_ref.move((x, y))

    # Left and right extension, where the gaps between contacts are different than before
    cont_spacing_x = 0.21 # Contact spacing from PDK
    cont_spacing_y = 0.185 # Contact spacing from PDK
    n_cont_x = 1
    n_cont_y = 1

    top_length = n_cont_x * cont_dim + (n_cont_x - 1) * cont_spacing_x + 2 * cont_extension
    top_width = n_cont_y * cont_dim + (n_cont_y - 1) * cont_spacing_y + 2 * cont_extension
    # The addition of a grid point results in extension by via_dim + via_spacing
    # This condition was found empirically to match the PDK layout

    while top_length + cont_dim + cont_spacing_x < activ_external_extension - activ_internal_extension:
        n_cont_x += 1
        top_length = n_cont_x * cont_dim + (n_cont_x - 1) * cont_spacing_x + 2 * cont_extension

    while top_width + cont_dim + cont_spacing_y < width + 2*activ_internal_extension:
        n_cont_y += 1
        top_width = n_cont_y * cont_dim + (n_cont_y - 1) * cont_spacing_y + 2 * cont_extension

    for i in range(n_cont_x):
        for j in range(n_cont_y):
            x = - activ_external_extension + cont_extension + i*(cont_dim + cont_spacing_x)
            y = - activ_internal_extension + cont_extension + j*(cont_dim + cont_spacing_y)
            cont = gf.components.rectangle(
                size=(cont_dim, cont_dim),
                layer=layer_cont,
            )
            cont_ref = c.add_ref(cont)
            cont_ref.move((x, y))

            if y < width/2 - 1.5 - cont_extension or y > width/2 + 1.5 + cont_extension:
                x = length + activ_internal_extension + cont_extension + i*(cont_dim + cont_spacing_x)
                cont = gf.components.rectangle(
                    size=(cont_dim, cont_dim),
                    layer=layer_cont,
                )
                cont_ref = c.add_ref(cont)
                cont_ref.move((x, y))

    # ----------------
    # Metal 1
    # ----------------
    metal1_drawing = c << gf.components.rectangle(
        size=(length + 2*activ_external_extension, width + 2*activ_external_extension),
        layer=layer_metal1,
    )
    metal1_drawing.xmin = -activ_external_extension
    metal1_drawing.ymin = -activ_external_extension

    # ----------------
    # Metal 1 pin
    # ----------------
    metal1_pin = c << gf.components.rectangle(
        size=(length + 2*activ_external_extension, activ_external_extension - activ_internal_extension),
        layer=layer_metal1_pin,
    )
    metal1_pin.xmin = -activ_external_extension
    metal1_pin.ymin = -activ_external_extension

    # ----------------
    # Metal 2
    # ----------------
    metal2_drawing = c << gf.components.rectangle(
        size=(length + 2*activ_external_extension, width + 2*activ_external_extension),
        layer=layer_metal2,
    )
    metal2_drawing.xmin = -activ_external_extension
    metal2_drawing.ymin = -activ_external_extension


    # ----------------
    # pSD
    # ----------------
    c.add_polygon(
        [
            (-activ_external_extension - psd_extra_extension, width + activ_internal_extension - psd_extra_extension),
            (-activ_external_extension - psd_extra_extension, -activ_external_extension - psd_extra_extension),
            (length + activ_external_extension + psd_extra_extension, - activ_external_extension - psd_extra_extension),
            (length + activ_external_extension + psd_extra_extension, width + activ_external_extension + psd_extra_extension),
            (-activ_external_extension - psd_extra_extension, width + activ_external_extension + psd_extra_extension),
            (-activ_external_extension - psd_extra_extension, width + activ_internal_extension - psd_extra_extension),
            (length + activ_internal_extension - psd_extra_extension, width + activ_internal_extension - psd_extra_extension),
            (length + activ_internal_extension - psd_extra_extension, -activ_internal_extension + psd_extra_extension),
            (-activ_internal_extension + psd_extra_extension, -activ_internal_extension + psd_extra_extension),
            (-activ_internal_extension + psd_extra_extension, width + activ_internal_extension - psd_extra_extension),
        ],
        layer=layer_psd,
    )

    # ----------------
    # Metal 3
    # ----------------
    metal3_drawing = c << gf.components.rectangle(
        size=(length + 2*activ_external_extension, width + 2*activ_external_extension),
        layer=layer_metal3,
    )
    metal3_drawing.xmin = -activ_external_extension
    metal3_drawing.ymin = -activ_external_extension

    # ----------------
    # PWell
    # ----------------
    pwell = c << gf.components.rectangle(
        size=(length + 2*pwell_extension, width + 2*pwell_extension),
        layer=layer_pwell,
    )
    pwell.xmin = -pwell_extension
    pwell.ymin = -pwell_extension
    # ----------------
    # Metal 4
    # ----------------
    metal4_drawing = c << gf.components.rectangle(
        size=(length + 2*activ_external_extension, width + 2*activ_external_extension),
        layer=layer_metal4,
    )
    metal4_drawing.xmin = -activ_external_extension
    metal4_drawing.ymin = -activ_external_extension

    # ----------------
    # Metal 5
    # ----------------
    metal5_drawing = c << gf.components.rectangle(
        size=(length + 2*activ_external_extension, width + 2*activ_external_extension),
        layer=layer_metal5,
    )
    metal5_drawing.xmin = -activ_external_extension
    metal5_drawing.ymin = -activ_external_extension

    metal5_internal = c << gf.components.rectangle(
        size=(length + 2*metal5_extension, width + 2*metal5_extension),
        layer=layer_metal5,
    )
    metal5_internal.xmin = -metal5_extension
    metal5_internal.ymin = -metal5_extension
    c.add_polygon(
        [
            (length + metal5_extension, width/2 + 1.5),
            (length + metal5_extension, width/2 - 1.5),
            (length + activ_external_extension, width/2 - 1.5),
            (length + activ_external_extension, width/2 + 1.5),
        ],
        layer=layer_metal5,
    )

    metal5_pin = c << gf.components.rectangle(
        size=(activ_external_extension - activ_internal_extension, 3.0),
        layer=layer_metal5_pin,
    )
    metal5_pin.xmin = length + activ_internal_extension
    metal5_pin.ymin = width/2 - 1.5

    # ----------------
    # Top Metal 1
    # ----------------
    top_metal1_drawing = c << gf.components.rectangle(
        size=(length + 2*activ_external_extension, width + 2*activ_external_extension),
        layer=layer_topmetal1,
    )
    top_metal1_drawing.xmin = -activ_external_extension
    top_metal1_drawing.ymin = -activ_external_extension

    top_metal1_internal = c << gf.components.rectangle(
        size=(length - 2*cont_extension, width - 2*cont_extension),
        layer=layer_topmetal1,
    )
    top_metal1_internal.xmin = cont_extension
    top_metal1_internal.ymin = cont_extension

    top_metal1_pin = c << gf.components.rectangle(
        size=(activ_external_extension - activ_internal_extension, 3.0),
        layer=layer_topmetal1_pin,
    )
    top_metal1_pin.xmin = -activ_external_extension
    top_metal1_pin.ymin = width/2 - 1.5

    # Add ports
    c.add_port(
        name="TIE",
        center=(length/2, -activ_internal_extension/2 - activ_external_extension / 2),
        width=activ_external_extension - activ_internal_extension,
        orientation=180,
        layer=layer_metal1_pin,
        port_type="electrical",
    )

    c.add_port(
        name="MINUS",
        center=(length + activ_internal_extension/2 + activ_external_extension/2, width/2),
        width=3.0,
        orientation=0,
        layer=layer_metal5_pin,
        port_type="electrical",
    )

    c.add_port(
        name="PLUS",
        center=(- activ_internal_extension/2 - activ_external_extension/2, width/2),
        width=3.0,
        orientation=180,
        layer=layer_topmetal1_pin,
        port_type="electrical",
    )

    # # Add ports
    # c.add_port(
    #     name="P1",
    #     center=(-(bottom_plate_length / 2 + 1.0), 0),
    #     width=2.0,
    #     orientation=180,
    #     layer=layer_metal4,
    #     port_type="electrical",
    # )

    # c.add_port(
    #     name="P2",
    #     center=(length / 2 + 2.0, 0),
    #     width=2.0,
    #     orientation=0,
    #     layer=layer_topmetal1,
    #     port_type="electrical",
    # )

    # c.add_port(
    #     name="GND",
    #     center=(0, -shield_width / 2),
    #     width=shield_length,
    #     orientation=270,
    #     layer=layer_metal3,
    #     port_type="electrical",
    # )

    # Add metadata
    c.info["model"] = model
    c.info["width"] = width
    c.info["length"] = length
    c.info["capacitance_fF"] = capacitance
    c.info["area_um2"] = width * length
    c.info["type"] = "rf_capacitor"

    return c


if __name__ == "__main__":
    from gdsfactory.difftest import xor

    from ihp import PDK, cells2

    PDK.activate()

    # Test the components
    width = 6.99
    length = 8
    # c0 = cells2.cmim(width=width, length=length)  # original
    # c1 = cmim(width=width, length=length)  # New
    # # c = gf.grid([c0, c1], spacing=100)

    # c = xor(c0, c1)
    # c.show()
    # c0.show()
    # c1.show()

    c0_rf = cells2.rfcmim(width=width, length=length)  # original
    c1_rf = rfcmim(width=width, length=length)  # New
    # c = gf.grid([c0, c1], spacing=100)
    c_rf = xor(c0_rf, c1_rf)
    c_rf.show()
