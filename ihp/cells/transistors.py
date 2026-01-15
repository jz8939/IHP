"""Transistor components for IHP PDK."""

import gdsfactory as gf
from gdsfactory import Component
from gdsfactory.typings import LayerSpec


@gf.cell
def nmos(
    width: float = 1.0,
    length: float = 0.13,
    nf: int = 1,
    m: int = 1,
    model: str = "sg13_lv_nmos",
    layer_gatpoly: LayerSpec = "GatPolydrawing",
    layer_activ: LayerSpec = "Activdrawing",
    layer_nsd: LayerSpec = "nSDdrawing",
    layer_cont: LayerSpec = "Contdrawing",
    layer_metal1: LayerSpec = "Metal1drawing",
) -> Component:
    """Create an NMOS transistor.

    Args:
        width: Total width of the transistor in micrometers.
        length: Gate length in micrometers.
        nf: Number of fingers.
        m: Multiplier (number of parallel devices).
        model: Device model name.
        layer_gatpoly: Gate polysilicon layer.
        layer_activ: Active region layer.
        layer_nsd: N+ source/drain implant layer.
        layer_cont: Contact layer.
        layer_metal1: Metal1 layer.

    Returns:
        Component with NMOS transistor layout.
    """
    c = Component()

    # Design rules
    gate_min_width = 0.15
    gate_min_length = 0.13
    cont_size = 0.16
    cont_spacing = 0.18
    cont_gate_spacing = 0.14
    cont_enc_active = 0.07
    cont_enc_metal = 0.06
    poly_extension = 0.18
    active_extension = 0.23
    psd_enclosure = 0.12

    # Calculate dimensions
    gate_width = max(width / nf, gate_min_width)
    gate_length = max(length, gate_min_length)

    # Grid snap
    grid = 0.005
    gate_width = round(gate_width / grid) * grid
    gate_length = round(gate_length / grid) * grid

    # Create transistor fingers
    finger_pitch = gate_width + 2 * cont_gate_spacing + cont_size

    for i in range(nf):
        x_offset = i * finger_pitch

        # Gate poly
        gate = gf.components.rectangle(
            size=(gate_length, gate_width + 2 * poly_extension),
            layer=layer_gatpoly,
        )
        gate_ref = c.add_ref(gate)
        gate_ref.movex(x_offset)

        # Active region
        active_width = gate_width
        active_length = gate_length + 2 * active_extension
        active = gf.components.rectangle(
            size=(active_length, active_width),
            layer=layer_activ,
        )
        active_ref = c.add_ref(active)
        active_ref.move((x_offset - active_extension, poly_extension))

        # Source/Drain contacts
        # Calculate number of contacts
        n_cont_y = int((active_width - cont_size) / cont_spacing) + 1

        # Source contacts (left)
        for j in range(n_cont_y):
            y_pos = poly_extension + j * cont_spacing

            cont = gf.components.rectangle(
                size=(cont_size, cont_size),
                layer=layer_cont,
            )
            cont_ref = c.add_ref(cont)
            cont_ref.move((x_offset - active_extension + cont_enc_active, y_pos))

            # Metal1 for source
            m1 = gf.components.rectangle(
                size=(cont_size + 2 * cont_enc_metal, cont_size + 2 * cont_enc_metal),
                layer=layer_metal1,
            )
            m1_ref = c.add_ref(m1)
            m1_ref.move(
                (
                    x_offset - active_extension + cont_enc_active - cont_enc_metal,
                    y_pos - cont_enc_metal,
                )
            )

        # Drain contacts (right)
        for j in range(n_cont_y):
            y_pos = poly_extension + j * cont_spacing

            cont = gf.components.rectangle(
                size=(cont_size, cont_size),
                layer=layer_cont,
            )
            cont_ref = c.add_ref(cont)
            cont_ref.move((x_offset + gate_length + cont_gate_spacing, y_pos))

            # Metal1 for drain
            m1 = gf.components.rectangle(
                size=(cont_size + 2 * cont_enc_metal, cont_size + 2 * cont_enc_metal),
                layer=layer_metal1,
            )
            m1_ref = c.add_ref(m1)
            m1_ref.move(
                (
                    x_offset + gate_length + cont_gate_spacing - cont_enc_metal,
                    y_pos - cont_enc_metal,
                )
            )

    # N+ implant
    nsd = gf.components.rectangle(
        size=(nf * finger_pitch + active_extension, gate_width + 2 * psd_enclosure),
        layer=layer_nsd,
    )
    nsd_ref = c.add_ref(nsd)
    nsd_ref.move((-active_extension - psd_enclosure, poly_extension - psd_enclosure))

    # Add ports
    c.add_port(
        name="G",
        center=(nf * finger_pitch / 2, -poly_extension),
        width=gate_length,
        orientation=270,
        layer=layer_gatpoly,
        port_type="electrical",
    )

    c.add_port(
        name="S",
        center=(-active_extension, gate_width / 2 + poly_extension),
        width=gate_width,
        orientation=180,
        layer=layer_metal1,
        port_type="electrical",
    )

    c.add_port(
        name="D",
        center=(gate_length + active_extension, gate_width / 2 + poly_extension),
        width=gate_width,
        orientation=0,
        layer=layer_metal1,
        port_type="electrical",
    )

    # Add metadata
    c.info["model"] = model
    c.info["width"] = width
    c.info["length"] = length
    c.info["nf"] = nf
    c.info["m"] = m
    c.info["type"] = "nmos"

    # VLSIR simulation metadata
    c.info["vlsir"] = {
        "model": "sg13_lv_nmos",
        "spice_type": "SUBCKT",
        "spice_lib": "sg13g2_moslv_mod.lib",
        "port_order": ["d", "g", "s", "b"],
        "port_map": {"D": "d", "G": "g", "S": "s"},
        "params": {
            "w": width * 1e-6,
            "l": length * 1e-6,
            "ng": nf,
            "m": m,
        },
    }

    return c


@gf.cell
def pmos(
    width: float = 1.0,
    length: float = 0.13,
    nf: int = 1,
    m: int = 1,
    model: str = "sg13_lv_pmos",
    layer_nwell: LayerSpec = "NWelldrawing",
    layer_gatpoly: LayerSpec = "GatPolydrawing",
    layer_activ: LayerSpec = "Activdrawing",
    layer_psd: LayerSpec = "pSDdrawing",
    layer_cont: LayerSpec = "Contdrawing",
    layer_metal1: LayerSpec = "Metal1drawing",
) -> Component:
    """Create a PMOS transistor.

    Args:
        width: Total width of the transistor in micrometers.
        length: Gate length in micrometers.
        nf: Number of fingers.
        m: Multiplier (number of parallel devices).
        model: Device model name.
        layer_nwell: N-well layer.
        layer_gatpoly: Gate polysilicon layer.
        layer_activ: Active region layer.
        layer_psd: P+ source/drain implant layer.
        layer_cont: Contact layer.
        layer_metal1: Metal1 layer.

    Returns:
        Component with PMOS transistor layout.
    """
    c = Component()

    # Design rules
    gate_min_width = 0.15
    gate_min_length = 0.13
    cont_size = 0.16
    cont_spacing = 0.18
    cont_gate_spacing = 0.14
    cont_enc_active = 0.07
    cont_enc_metal = 0.06
    poly_extension = 0.18
    active_extension = 0.23
    nwell_enclosure = 0.31
    psd_enclosure = 0.12

    # Calculate dimensions
    gate_width = max(width / nf, gate_min_width)
    gate_length = max(length, gate_min_length)

    # Grid snap
    grid = 0.005
    gate_width = round(gate_width / grid) * grid
    gate_length = round(gate_length / grid) * grid

    # N-Well
    nwell_width = gate_width + 2 * nwell_enclosure
    nwell_length = gate_length + 2 * active_extension + 2 * nwell_enclosure
    nwell = gf.components.rectangle(
        size=(nwell_length * nf, nwell_width),
        layer=layer_nwell,
    )
    nwell_ref = c.add_ref(nwell)
    nwell_ref.move(
        (-active_extension - nwell_enclosure, poly_extension - nwell_enclosure)
    )

    # Create transistor fingers
    finger_pitch = gate_width + 2 * cont_gate_spacing + cont_size

    for i in range(nf):
        x_offset = i * finger_pitch

        # Gate poly
        gate = gf.components.rectangle(
            size=(gate_length, gate_width + 2 * poly_extension),
            layer=layer_gatpoly,
        )
        gate_ref = c.add_ref(gate)
        gate_ref.movex(x_offset)

        # Active region
        active_width = gate_width
        active_length = gate_length + 2 * active_extension
        active = gf.components.rectangle(
            size=(active_length, active_width),
            layer=layer_activ,
        )
        active_ref = c.add_ref(active)
        active_ref.move((x_offset - active_extension, poly_extension))

        # Source/Drain contacts
        n_cont_y = int((active_width - cont_size) / cont_spacing) + 1

        # Source contacts (left)
        for j in range(n_cont_y):
            y_pos = poly_extension + j * cont_spacing

            cont = gf.components.rectangle(
                size=(cont_size, cont_size),
                layer=layer_cont,
            )
            cont_ref = c.add_ref(cont)
            cont_ref.move((x_offset - active_extension + cont_enc_active, y_pos))

            # Metal1 for source
            m1 = gf.components.rectangle(
                size=(cont_size + 2 * cont_enc_metal, cont_size + 2 * cont_enc_metal),
                layer=layer_metal1,
            )
            m1_ref = c.add_ref(m1)
            m1_ref.move(
                (
                    x_offset - active_extension + cont_enc_active - cont_enc_metal,
                    y_pos - cont_enc_metal,
                )
            )

        # Drain contacts (right)
        for j in range(n_cont_y):
            y_pos = poly_extension + j * cont_spacing

            cont = gf.components.rectangle(
                size=(cont_size, cont_size),
                layer=layer_cont,
            )
            cont_ref = c.add_ref(cont)
            cont_ref.move((x_offset + gate_length + cont_gate_spacing, y_pos))

            # Metal1 for drain
            m1 = gf.components.rectangle(
                size=(cont_size + 2 * cont_enc_metal, cont_size + 2 * cont_enc_metal),
                layer=layer_metal1,
            )
            m1_ref = c.add_ref(m1)
            m1_ref.move(
                (
                    x_offset + gate_length + cont_gate_spacing - cont_enc_metal,
                    y_pos - cont_enc_metal,
                )
            )

    # P+ implant
    psd = gf.components.rectangle(
        size=(nf * finger_pitch + active_extension, gate_width + 2 * psd_enclosure),
        layer=layer_psd,
    )
    psd_ref = c.add_ref(psd)
    psd_ref.move((-active_extension - psd_enclosure, poly_extension - psd_enclosure))

    # Add ports
    c.add_port(
        name="G",
        center=(nf * finger_pitch / 2, -poly_extension),
        width=gate_length,
        orientation=270,
        layer=layer_gatpoly,
        port_type="electrical",
    )

    c.add_port(
        name="S",
        center=(-active_extension, gate_width / 2 + poly_extension),
        width=gate_width,
        orientation=180,
        layer=layer_metal1,
        port_type="electrical",
    )

    c.add_port(
        name="D",
        center=(gate_length + active_extension, gate_width / 2 + poly_extension),
        width=gate_width,
        orientation=0,
        layer=layer_metal1,
        port_type="electrical",
    )

    # Add metadata
    c.info["model"] = model
    c.info["width"] = width
    c.info["length"] = length
    c.info["nf"] = nf
    c.info["m"] = m
    c.info["type"] = "pmos"

    # VLSIR simulation metadata
    c.info["vlsir"] = {
        "model": "sg13_lv_pmos",
        "spice_type": "SUBCKT",
        "spice_lib": "sg13g2_moslv_mod.lib",
        "port_order": ["d", "g", "s", "b"],
        "port_map": {"D": "d", "G": "g", "S": "s"},
        "params": {
            "w": width * 1e-6,
            "l": length * 1e-6,
            "ng": nf,
            "m": m,
        },
    }

    return c


@gf.cell
def nmos_hv(
    width: float = 1.0,
    length: float = 0.45,
    nf: int = 1,
    m: int = 1,
    model: str = "sg13_hv_nmos",
    layer_thickgateox: LayerSpec = "ThickGateOxdrawing",
    layer_gatpoly: LayerSpec = "GatPolydrawing",
    layer_activ: LayerSpec = "Activdrawing",
    layer_nsd: LayerSpec = "nSDdrawing",
    layer_cont: LayerSpec = "Contdrawing",
    layer_metal1: LayerSpec = "Metal1drawing",
) -> Component:
    """Create a high-voltage NMOS transistor.

    Args:
        width: Total width of the transistor in micrometers.
        length: Gate length in micrometers.
        nf: Number of fingers.
        m: Multiplier (number of parallel devices).
        model: Device model name.
        layer_thickgateox: Thick gate oxide layer.
        layer_gatpoly: Gate polysilicon layer.
        layer_activ: Active region layer.
        layer_nsd: N+ source/drain implant layer.
        layer_cont: Contact layer.
        layer_metal1: Metal1 layer.

    Returns:
        Component with HV NMOS transistor layout.
    """
    c = Component()

    # Add base nmos as reference
    nmos_ref = c << nmos(
        width=width,
        length=length,
        nf=nf,
        m=m,
        model=model,
        layer_gatpoly=layer_gatpoly,
        layer_activ=layer_activ,
        layer_nsd=layer_nsd,
        layer_cont=layer_cont,
        layer_metal1=layer_metal1,
    )

    # Add thick gate oxide layer
    thick_ox = gf.components.rectangle(
        size=(length + 0.5, width + 0.5),
        layer=layer_thickgateox,
        centered=True,
    )
    c.add_ref(thick_ox)

    # Copy ports from base nmos
    c.add_ports(nmos_ref.ports)

    c.info["type"] = "nmos_hv"

    # VLSIR simulation metadata
    c.info["vlsir"] = {
        "model": "sg13_hv_nmos",
        "spice_type": "SUBCKT",
        "spice_lib": "sg13g2_moshv_mod.lib",
        "port_order": ["d", "g", "s", "b"],
        "port_map": {"D": "d", "G": "g", "S": "s"},
        "params": {
            "w": width * 1e-6,
            "l": length * 1e-6,
            "ng": nf,
            "m": m,
        },
    }

    return c


@gf.cell
def pmos_hv(
    width: float = 1.0,
    length: float = 0.45,
    nf: int = 1,
    m: int = 1,
    model: str = "sg13_hv_pmos",
    layer_thickgateox: LayerSpec = "ThickGateOxdrawing",
    layer_nwell: LayerSpec = "NWelldrawing",
    layer_gatpoly: LayerSpec = "GatPolydrawing",
    layer_activ: LayerSpec = "Activdrawing",
    layer_psd: LayerSpec = "pSDdrawing",
    layer_cont: LayerSpec = "Contdrawing",
    layer_metal1: LayerSpec = "Metal1drawing",
) -> Component:
    """Create a high-voltage PMOS transistor.

    Args:
        width: Total width of the transistor in micrometers.
        length: Gate length in micrometers.
        nf: Number of fingers.
        m: Multiplier (number of parallel devices).
        model: Device model name.
        layer_thickgateox: Thick gate oxide layer.
        layer_nwell: N-well layer.
        layer_gatpoly: Gate polysilicon layer.
        layer_activ: Active region layer.
        layer_psd: P+ source/drain implant layer.
        layer_cont: Contact layer.
        layer_metal1: Metal1 layer.

    Returns:
        Component with HV PMOS transistor layout.
    """
    c = Component()

    # Add base pmos as reference
    pmos_ref = c << pmos(
        width=width,
        length=length,
        nf=nf,
        m=m,
        model=model,
        layer_nwell=layer_nwell,
        layer_gatpoly=layer_gatpoly,
        layer_activ=layer_activ,
        layer_psd=layer_psd,
        layer_cont=layer_cont,
        layer_metal1=layer_metal1,
    )

    # Add thick gate oxide layer
    thick_ox = gf.components.rectangle(
        size=(length + 0.5, width + 0.5),
        layer=layer_thickgateox,
        centered=True,
    )
    c.add_ref(thick_ox)

    # Copy ports from base pmos
    c.add_ports(pmos_ref.ports)

    c.info["type"] = "pmos_hv"

    # VLSIR simulation metadata
    c.info["vlsir"] = {
        "model": "sg13_hv_pmos",
        "spice_type": "SUBCKT",
        "spice_lib": "sg13g2_moshv_mod.lib",
        "port_order": ["d", "g", "s", "b"],
        "port_map": {"D": "d", "G": "g", "S": "s"},
        "params": {
            "w": width * 1e-6,
            "l": length * 1e-6,
            "ng": nf,
            "m": m,
        },
    }

    return c


@gf.cell
def rfnmos(
    width: float = 2.0,
    length: float = 0.13,
    nf: int = 2,
    m: int = 1,
    model: str = "sg13_lv_rfnmos",
    layer_gatpoly: LayerSpec = "GatPolydrawing",
    layer_activ: LayerSpec = "Activdrawing",
    layer_nsd: LayerSpec = "nSDdrawing",
    layer_cont: LayerSpec = "Contdrawing",
    layer_metal1: LayerSpec = "Metal1drawing",
) -> Component:
    """Create an RF NMOS transistor with optimized layout.

    Args:
        width: Total width of the transistor in micrometers.
        length: Gate length in micrometers.
        nf: Number of fingers (should be even for RF).
        m: Multiplier (number of parallel devices).
        model: Device model name.
        layer_gatpoly: Gate polysilicon layer.
        layer_activ: Active region layer.
        layer_nsd: N+ source/drain implant layer.
        layer_cont: Contact layer.
        layer_metal1: Metal1 layer.

    Returns:
        Component with RF NMOS transistor layout.
    """
    # Ensure even number of fingers for RF layout
    if nf % 2 != 0:
        nf = nf + 1

    c = Component()

    # Add base nmos as reference
    nmos_ref = c << nmos(
        width=width,
        length=length,
        nf=nf,
        m=m,
        model=model,
        layer_gatpoly=layer_gatpoly,
        layer_activ=layer_activ,
        layer_nsd=layer_nsd,
        layer_cont=layer_cont,
        layer_metal1=layer_metal1,
    )

    # Add substrate shielding for RF
    shield_layer = (37, 0)  # Example shield layer
    shield = gf.components.rectangle(
        size=(length * nf * 1.5, width * 1.2),
        layer=shield_layer,
        centered=True,
    )
    c.add_ref(shield)

    # Copy ports from base nmos
    c.add_ports(nmos_ref.ports)

    c.info["type"] = "rfnmos"

    # VLSIR simulation metadata
    c.info["vlsir"] = {
        "model": "sg13_lv_nmos",
        "spice_type": "SUBCKT",
        "spice_lib": "sg13g2_moslv_mod.lib",
        "port_order": ["d", "g", "s", "b"],
        "port_map": {"D": "d", "G": "g", "S": "s"},
        "params": {
            "w": width * 1e-6,
            "l": length * 1e-6,
            "ng": nf,
            "m": m,
            "rfmode": 1,  # Enable RF mode
        },
    }

    return c


@gf.cell
def rfpmos(
    width: float = 2.0,
    length: float = 0.13,
    nf: int = 2,
    m: int = 1,
    model: str = "sg13_lv_rfpmos",
    layer_nwell: LayerSpec = "NWelldrawing",
    layer_gatpoly: LayerSpec = "GatPolydrawing",
    layer_activ: LayerSpec = "Activdrawing",
    layer_psd: LayerSpec = "pSDdrawing",
    layer_cont: LayerSpec = "Contdrawing",
    layer_metal1: LayerSpec = "Metal1drawing",
) -> Component:
    """Create an RF PMOS transistor with optimized layout.

    Args:
        width: Total width of the transistor in micrometers.
        length: Gate length in micrometers.
        nf: Number of fingers (should be even for RF).
        m: Multiplier (number of parallel devices).
        model: Device model name.
        layer_nwell: N-well layer.
        layer_gatpoly: Gate polysilicon layer.
        layer_activ: Active region layer.
        layer_psd: P+ source/drain implant layer.
        layer_cont: Contact layer.
        layer_metal1: Metal1 layer.

    Returns:
        Component with RF PMOS transistor layout.
    """
    # Ensure even number of fingers for RF layout
    if nf % 2 != 0:
        nf = nf + 1

    c = Component()

    # Add base pmos as reference
    pmos_ref = c << pmos(
        width=width,
        length=length,
        nf=nf,
        m=m,
        model=model,
        layer_nwell=layer_nwell,
        layer_gatpoly=layer_gatpoly,
        layer_activ=layer_activ,
        layer_psd=layer_psd,
        layer_cont=layer_cont,
        layer_metal1=layer_metal1,
    )

    # Add substrate shielding for RF
    shield_layer = (37, 0)  # Example shield layer
    shield = gf.components.rectangle(
        size=(length * nf * 1.5, width * 1.2),
        layer=shield_layer,
        centered=True,
    )
    c.add_ref(shield)

    # Copy ports from base pmos
    c.add_ports(pmos_ref.ports)

    c.info["type"] = "rfpmos"

    # VLSIR simulation metadata
    c.info["vlsir"] = {
        "model": "sg13_lv_pmos",
        "spice_type": "SUBCKT",
        "spice_lib": "sg13g2_moslv_mod.lib",
        "port_order": ["d", "g", "s", "b"],
        "port_map": {"D": "d", "G": "g", "S": "s"},
        "params": {
            "w": width * 1e-6,
            "l": length * 1e-6,
            "ng": nf,
            "m": m,
            "rfmode": 1,  # Enable RF mode
        },
    }

    return c


if __name__ == "__main__":
    from gdsfactory.difftest import xor

    from ihp import PDK
    from ihp.cells import fixed

    PDK.activate()

    # Test the components
    c0 = fixed.nmos()  # original
    c1 = nmos()  # New
    # c = gf.grid([c0, c1], spacing=100)
    c = xor(c0, c1)
    c.show()

    # c0 = cells.pmos()  # original
    # c1 = pmos()  # New
    # # c = gf.grid([c0, c1], spacing=100)
    # c = xor(c0, c1)
    # c.show()

    # c0 = cells.rfnmos()  # original
    # c1 = rfnmos()  # New
    # # c = gf.grid([c0, c1], spacing=100)
    # c = xor(c0, c1)
    # c.show()
