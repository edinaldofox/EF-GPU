"""Render a GDSII layout to PNG with KLayout in non-interactive mode.

Usage:
  EF_GPU_GDS=path/to/layout.gds EF_GPU_LAYOUT_PNG=/tmp/layout.png \
    klayout -z -r scripts/render-gds-layout.py
"""

import os

import pya


input_gds = os.environ["EF_GPU_GDS"]
output_png = os.environ["EF_GPU_LAYOUT_PNG"]

view = pya.LayoutView()
view.set_config("background-color", "#101820")
view.set_config("grid-visible", "false")
view.set_config("text-visible", "false")
view.load_layout(input_gds, 0)
view.max_hier()
view.zoom_fit()
view.save_image_with_options(output_png, 2400, 1600, 0, 0, 0)
