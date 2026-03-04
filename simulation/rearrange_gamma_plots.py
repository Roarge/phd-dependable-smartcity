#!/usr/bin/env python3
"""
Rearrange wide gamma evolution plots from 1xN horizontal rows into
2x2 grids for A4 readability.

Does NOT re-run the simulation -- works only with existing PNG files.
"""

from PIL import Image
import os

BASE = os.path.dirname(os.path.abspath(__file__))


def split_horizontal_panels(img, n_panels):
    """Split an image with N equally-spaced horizontal panels."""
    w, h = img.size
    panel_w = w // n_panels
    panels = []
    for i in range(n_panels):
        x0 = i * panel_w
        x1 = (i + 1) * panel_w if i < n_panels - 1 else w
        panels.append(img.crop((x0, 0, x1, h)))
    return panels


def arrange_2x2(panels, bg_color=(255, 255, 255)):
    """Arrange up to 4 panels into a 2x2 grid."""
    n = len(panels)
    pw = max(p.size[0] for p in panels)
    ph = max(p.size[1] for p in panels)

    cols = 2
    rows = (n + cols - 1) // cols

    out_w = pw * cols
    out_h = ph * rows
    out = Image.new("RGB", (out_w, out_h), bg_color)

    for idx, panel in enumerate(panels):
        row, col = divmod(idx, cols)
        x = col * pw
        y = row * ph
        out.paste(panel, (x, y))

    return out


def process_file(rel_path, n_panels, suffix="_grid"):
    """Load a wide PNG, split into panels, rearrange as 2x2, save."""
    full_path = os.path.join(BASE, rel_path)
    if not os.path.exists(full_path):
        print(f"  SKIP (not found): {rel_path}")
        return None

    img = Image.open(full_path)
    print(f"  Input: {rel_path} ({img.size[0]}x{img.size[1]}, {n_panels} panels)")

    panels = split_horizontal_panels(img, n_panels)
    grid = arrange_2x2(panels)

    # Save next to original with suffix
    base_name, ext = os.path.splitext(full_path)
    out_path = base_name + suffix + ext
    grid.save(out_path, dpi=(150, 150))
    print(f"  Output: {os.path.relpath(out_path, BASE)} ({grid.size[0]}x{grid.size[1]})")
    return out_path


def main():
    print("Rearranging wide gamma evolution plots for A4 readability")
    print("=" * 60)

    jobs = [
        ("phas_eai/results/extension3/ext3_gamma_baselines.png", 3),
        ("phas_eai/results/extension3/ext3_gamma_dynamic.png", 4),
        ("phas_eai/results/combined/combined_gamma_baselines.png", 4),
        ("phas_eai/results/combined/combined_gamma_phas.png", 3),
    ]

    for rel_path, n_panels in jobs:
        process_file(rel_path, n_panels)
        print()

    print("Done. Original files are unchanged.")


if __name__ == "__main__":
    main()
