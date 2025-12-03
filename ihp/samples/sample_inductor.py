"""This script generates a sample inductor from the IHP PDK."""

import gdsfactory as gf

from ihp import PDK
from ihp.cells import inductors

if __name__ == "__main__":
    PDK.activate()
    c = inductors.inductor2()
    gdspath = c.write_gds()
    gf.show(gdspath)
