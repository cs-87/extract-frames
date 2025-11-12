#!/usr/bin/env python3
"""
extract_frames_tqdm.py

This script extracts frames from a video and saves them as PNG images with
timestamp-based filenames.

It will ask you for:
- Input video path
- Output directory
- Frame extraction interval (in seconds)

Requires:
    pip install opencv-python tqdm
"""

import cv2
import os
from tqdm import tqdm


def ask(prompt: str) -> str:
    """Helper to safely get user input."""
    try:
        return input(prompt).strip()
    except EOFError:
        raise SystemExit("No input provided. Exiting.")


def main():
    # Always take input interactively
    input_path = ask("Enter input video path: ")
    out_dir = ask("Enter output directory: ")
    interval_str = ask("Enter time interval between frames (in seconds): ")

    try:
        interval = float(interval_str)
        if interval <= 0:
            raise ValueError
    except ValueError:
        raise SystemExit("❌ Invalid interval. Please enter a positive number.")

    if not os.path.isfile(input_path):
        raise SystemExit(f"Error: input file '{input_path}' not found.")

    os.makedirs(out_dir, exist_ok=True)

    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise SystemExit(f"Cannot open input video '{input_path}'.")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration_sec = total_frames / fps if fps > 0 else 0

    # Frame count estimate for tqdm
    expected_frames = int(duration_sec // interval) + 1 if duration_sec > 0 else None
    pbar = tqdm(total=expected_frames, unit="frame", desc=os.path.basename(input_path), ncols=100)

    saved = 0
    current_time = 0.0  # in seconds

    while True:
        # Seek to the current time
        cap.set(cv2.CAP_PROP_POS_MSEC, current_time * 1000)
        ret, frame = cap.read()
        if not ret:
            break

        # Compute timestamp
        hh = int(current_time // 3600)
        mm = int((current_time % 3600) // 60)
        ss = int(current_time % 60)
        ms_int = int(round((current_time - int(current_time)) * 1000))

        filename = f"frame_{hh:02d}_{mm:02d}_{ss:02d}.{ms_int:03d}.png"
        outpath = os.path.join(out_dir, filename)

        # Save frame with PNG compression (0-9, lower = better quality)
        cv2.imwrite(outpath, frame, [int(cv2.IMWRITE_PNG_COMPRESSION), 3])
        saved += 1
        pbar.update(1)

        current_time += interval
        if current_time > duration_sec:
            break

    pbar.close()
    cap.release()
    print(f"\n✅ Saved {saved} frames to '{out_dir}' (interval: {interval} sec)")


if __name__ == "__main__":
    main()
