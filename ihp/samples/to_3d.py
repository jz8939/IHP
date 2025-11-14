"""This script generates a reticle with all the cells in the library."""

from ihp import PDK, cells

if __name__ == "__main__":
    PDK.activate()
    c = cells.via_stack_with_pads()
    s = c.to_3d()
    s.show()
