"""Inductor components for IHP PDK."""

import math

import gdsfactory as gf
from gdsfactory import Component
from gdsfactory.typings import LayerSpec, LayerSpecs


def inductor_min_diameter(width: float, space: float, turns: int, grid: float) -> float:
    """Calculate minimum diameter for inductor.

    Args:
        width: Width of the inductor trace in micrometers.
        space: Space between turns in micrometers.
        turns: Number of turns.
        grid: Grid resolution.

    Returns:
        Minimum diameter in micrometers.
    """
    min_d = 2 * turns * (width + space) + 4 * width
    return round(min_d / grid) * grid


@gf.cell
def inductor2(
    width: float = 2.0,
    space: float = 2.1,
    diameter: float = 25.35,
    resistance: float = 0.5777,
    inductance: float = 33.303e-12,
    turns: int = 1,
    layer_metal: LayerSpec = "TopMetal2drawing",
    layer_inductor: LayerSpec = "INDdrawing",
    layer_metal_pin: LayerSpec = "TopMetal2pin",
    layers_no_fill: LayerSpecs = (
        "Activnofill",
        "GatPolynofill",
        "Metal1nofill",
        "Metal2nofill",
        "Metal3nofill",
        "Metal4nofill",
        "Metal5nofill",
        "TopMetal1nofill",
        "TopMetal2nofill",
        "PWellblock",
    ),
) -> Component:
    """Create a 2-turn inductor.

    Args:
        width: Width of the inductor trace in micrometers.
        space: Space between turns in micrometers.
        diameter: Inner diameter in micrometers.
        resistance: Resistance in ohms.
        inductance: Inductance in henries.
        turns: Number of turns (default 1 for inductor2).
        block_qrc: Block QRC layer.

    Returns:
        Component with inductor layout.
    """
    c = Component()

    # Grid fixing for manufacturing constraints
    grid = 0.01
    w = round(width / (2 * grid)) * 2 * grid
    s = round(space / grid) * grid
    d = round(diameter / (2 * grid)) * 2 * grid

    # Calculate geometry parameters
    r = d / 2 + s
    octagon_center_y = 3 * r
    pi_over_4 = math.radians(45)

    path_points = []
    path_points.append((+space / 2, octagon_center_y - r * math.cos(pi_over_4 / 2)))

    for i in range(-2, 6):
        angle = i * pi_over_4 + pi_over_4 / 2
        r = d / 2 + s
        x = r * math.cos(angle)
        y = r * math.sin(angle) + octagon_center_y

        if -2 <= i < 2:
            path_points.append((x, y))
        else:
            path_points.append((x, y))

    path_points.append((-space / 2, octagon_center_y - r * math.cos(pi_over_4 / 2)))

    # Create the path
    path = gf.Path(path_points)
    _ = c << gf.path.extrude(path, layer=layer_metal, width=w)

    # Adding ports
    length = 2 * r + s

    port1_trace = c << gf.components.rectangle(size=(s, length), layer=layer_metal)
    port1_trace.move((-s - s / 2, 0))
    c.add_port(name="P1", center=(-s, s), width=s, orientation=270, layer=layer_metal)

    port2_trace = c << gf.components.rectangle(size=(s, length), layer=layer_metal)
    port2_trace.move((s - s / 2, 0))
    c.add_port(name="P2", center=(+s, s), width=s, orientation=270, layer=layer_metal)

    # Add IND layer
    outer_polygon_pts = []
    for i in range(8):
        r_outer = (d / 2 + length) / (math.cos(pi_over_4 / 2))
        angle = i * pi_over_4 + pi_over_4 / 2
        x = r_outer * math.cos(angle)
        y = r_outer * math.sin(angle) + octagon_center_y
        outer_polygon_pts.append((x, y))

    c.add_polygon(points=outer_polygon_pts, layer=layer_inductor)

    # Add No fill layers
    for layer in layers_no_fill:
        c.add_polygon(points=outer_polygon_pts, layer=layer)

    # Adding pins
    pin_1_trace = c << gf.components.rectangle(size=(s, s), layer=layer_metal_pin)
    pin_1_trace.move((s / 2, 0))

    pin_2_trace = c << gf.components.rectangle(size=(s, s), layer=layer_metal_pin)
    pin_2_trace.move((-s - s / 2, 0))

    # Add metadata
    c.info["resistance"] = resistance
    c.info["inductance"] = inductance
    c.info["model"] = "inductor2"
    c.info["turns"] = turns
    c.info["width"] = width
    c.info["space"] = space
    c.info["diameter"] = diameter
    return c


@gf.cell
def inductor3(
    width: float = 2.0,
    space: float = 2.1,
    diameter: float = 24.68,
    resistance: float = 1.386,
    inductance: float = 221.5e-12,
    turns: int = 2,
    layer_metal: LayerSpec = "TopMetal2drawing",
    layer_inductor: LayerSpec = "INDdrawing",
    layer_metal_pin: LayerSpec = "TopMetal2pin",
    layers_no_fill: LayerSpecs = (
        "Activnofill",
        "GatPolynofill",
        "Metal1nofill",
        "Metal2nofill",
        "Metal3nofill",
        "Metal4nofill",
        "Metal5nofill",
        "TopMetal1nofill",
        "TopMetal2nofill",
        "PWellblock",
    ),
) -> Component:
    """Create a 3-turn inductor.

    Args:
        width: Width of the inductor trace in micrometers.
        space: Space between turns in micrometers.
        diameter: Inner diameter in micrometers.
        resistance: Resistance in ohms.
        inductance: Inductance in henries.
        turns: Number of turns (default 2 for inductor3).
        layer_metal: Metal layer for the inductor trace.
        layer_inductor: IND layer for inductor marking.
        layer_metal_pin: Metal pin layer.
        layers_no_fill: Tuple of no-fill layers to add.

    Returns:
        Component with inductor layout.
    """
    # Use inductor2 as base with different default parameters
    return inductor2(
        width=width,
        space=space,
        diameter=diameter,
        resistance=resistance,
        inductance=inductance,
        turns=turns,
        layer_metal=layer_metal,
        layer_inductor=layer_inductor,
        layer_metal_pin=layer_metal_pin,
        layers_no_fill=layers_no_fill,
    )


if __name__ == "__main__":
    from gdsfactory.difftest import xor

    from ihp import PDK
    from ihp.cells import fixed

    PDK.activate()

    # Test the components
    c0 = fixed.inductor2()  # original
    c1 = inductor2()  # New Parametric
    c = xor(c0, c1)
    c.show()

    # c0 = fixed.inductor3()  # original
    # c1 = inductor3()  # New
    # c = xor(c0, c1)
