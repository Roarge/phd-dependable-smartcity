#!/usr/bin/env python3
"""
Post-process existing chart PNGs:
  1. Crop title area from the top of each chart.
  2. Split the two wide gamma evolution strips into sub-panel images.

No simulation re-run required -- works on existing image files.
"""

import os
from PIL import Image
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))


def find_crop_row(path):
    """Detect where the title area ends by analysing dark-pixel density."""
    img = Image.open(path).convert("L")
    arr = np.array(img)
    h = arr.shape[0]

    dark_frac = [(arr[i] < 200).sum() / arr.shape[1]
                 for i in range(min(120, h))]

    title_start = None
    title_end = None
    for i in range(len(dark_frac)):
        if dark_frac[i] > 0.05 and title_start is None:
            title_start = i
        if title_start is not None and dark_frac[i] < 0.02:
            title_end = i
            break

    if title_end is None:
        return 0
    return title_end + 2


def crop_title(path):
    """Auto-detect and crop the title area from the top of an image."""
    crop_row = find_crop_row(path)
    if crop_row == 0:
        print(f"  No title detected: {os.path.basename(path)}")
        return
    img = Image.open(path)
    w, h = img.size
    cropped = img.crop((0, crop_row, w, h))
    cropped.save(path, dpi=(150, 150))
    print(f"  Cropped {crop_row}px: {os.path.basename(path)}  "
          f"({w}x{h} -> {w}x{h - crop_row})")


def split_gamma_strip(path, n_panels, output_specs):
    """
    Split a horizontal strip of n_panels into separate images,
    cropping the title from each.

    output_specs: list of (out_path, panel_indices) tuples.
    """
    # First crop title from the full strip
    crop_row = find_crop_row(path)
    img = Image.open(path)
    w, h = img.size
    if crop_row > 0:
        img = img.crop((0, crop_row, w, h))
        h = h - crop_row

    panel_w = w // n_panels

    for out_path, indices in output_specs:
        left = indices[0] * panel_w
        right = (indices[-1] + 1) * panel_w
        sub = img.crop((left, 0, right, h))
        sub.save(out_path, dpi=(150, 150))
        print(f"  Split panels {indices}: {os.path.basename(out_path)}  "
              f"({right - left}x{h})")


def main():
    # ── Crop titles from standard charts ──
    standard_charts = [
        "kaufmann/results/figure8_all_models.png",
        "kaufmann/results/figure9_system_free_energy.png",
        "phas_eai/results/extension1/ext1_free_energy.png",
        "phas_eai/results/extension1/ext1_convergence_weak.png",
        "phas_eai/results/extension2/ext2_free_energy.png",
        "phas_eai/results/extension2/ext2_convergence_weak.png",
        "phas_eai/results/extension3/ext3_free_energy.png",
        "phas_eai/results/extension4/ext4_free_energy.png",
        "phas_eai/results/extension4/ext4_convergence_weak.png",
        "phas_eai/results/extension5/ext5_free_energy.png",
        "phas_eai/results/extension5/ext5_convergence_weak.png",
        "phas_eai/results/combined/combined_free_energy.png",
        "phas_eai/results/combined/combined_convergence_weak.png",
        "phas_eai/results/alignment/alignment_convergence_weak.png",
        "phas_eai/results/alignment/alignment_2x2_summary.png",
        "phas_eai/results/alignment/alignment_free_energy.png",
    ]

    print("=== Cropping titles ===")
    for rel_path in standard_charts:
        full = os.path.join(BASE, rel_path)
        if os.path.exists(full):
            crop_title(full)
        else:
            print(f"  MISSING: {rel_path}")

    # ── Split gamma strips ──
    print("\n=== Splitting gamma evolution strips ===")

    # Extension 3 gamma: 7 panels
    #   0: K1 Baseline, 1: K3 Goal Alignment, 2: K4 ToM+Alignment
    #   3-6: E3 dynamic conditions
    ext3_gamma = os.path.join(
        BASE, "phas_eai/results/extension3/ext3_gamma_evolution.png")
    if os.path.exists(ext3_gamma):
        d = os.path.dirname(ext3_gamma)
        split_gamma_strip(ext3_gamma, 7, [
            (os.path.join(d, "ext3_gamma_baselines.png"), [0, 1, 2]),
            (os.path.join(d, "ext3_gamma_dynamic.png"), [3, 4, 5, 6]),
        ])

    # Combined gamma: 7 panels
    #   0: K1, 1: K4, 2: E1, 3: E2
    #   4: PHAS scaffold, 5: PHAS scaffold+dyn, 6: PHAS full
    combined_gamma = os.path.join(
        BASE, "phas_eai/results/combined/combined_gamma.png")
    if os.path.exists(combined_gamma):
        d = os.path.dirname(combined_gamma)
        split_gamma_strip(combined_gamma, 7, [
            (os.path.join(d, "combined_gamma_baselines.png"), [0, 1, 2, 3]),
            (os.path.join(d, "combined_gamma_phas.png"), [4, 5, 6]),
        ])

    print("\nDone.")


if __name__ == "__main__":
    main()
