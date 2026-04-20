from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


SUPPORTED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".webp",
    ".tif",
    ".tiff",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Merge all images in a directory into a single horizontal row. "
            "Each image is resized proportionally to the minimum height found "
            "in the directory."
        )
    )
    parser.add_argument("input_dir", type=Path, help="Directory that contains images")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output image path. Defaults to <input_dir>/merged_row.png",
    )
    parser.add_argument(
        "--background",
        default="transparent",
        help=(
            "Background color for the output canvas. Use 'transparent' or a PIL "
            "color value such as 'white', '#ffffff', or '#112233'."
        ),
    )
    return parser.parse_args()


def find_images(input_dir: Path) -> list[Path]:
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")
    if not input_dir.is_dir():
        raise NotADirectoryError(f"Input path is not a directory: {input_dir}")

    images = sorted(
        path
        for path in input_dir.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not images:
        raise ValueError(f"No supported images found in directory: {input_dir}")

    return images


def resize_to_height(image: Image.Image, target_height: int) -> Image.Image:
    width, height = image.size
    if height <= 0:
        raise ValueError("Encountered an image with invalid height.")

    scale = target_height / height
    target_width = max(1, round(width * scale))
    return image.resize((target_width, target_height), Image.Resampling.LANCZOS)


def build_canvas(size: tuple[int, int], background: str) -> Image.Image:
    width, height = size
    if background.lower() == "transparent":
        return Image.new("RGBA", (width, height), (0, 0, 0, 0))
    return Image.new("RGBA", (width, height), background)


def prepare_for_save(canvas: Image.Image, output_path: Path) -> Image.Image:
    if output_path.suffix.lower() in {".jpg", ".jpeg"}:
        rgb_canvas = Image.new("RGB", canvas.size, "white")
        rgb_canvas.paste(canvas, mask=canvas.getchannel("A"))
        return rgb_canvas
    return canvas


def merge_images_in_row(image_paths: list[Path], output_path: Path, background: str) -> Path:
    opened_images: list[Image.Image] = []
    try:
        for image_path in image_paths:
            opened_images.append(Image.open(image_path).convert("RGBA"))

        min_height = min(image.height for image in opened_images)
        resized_images = [resize_to_height(image, min_height) for image in opened_images]

        total_width = sum(image.width for image in resized_images)
        canvas = build_canvas((total_width, min_height), background)

        x_offset = 0
        for image in resized_images:
            canvas.paste(image, (x_offset, 0), image)
            x_offset += image.width

        output_path.parent.mkdir(parents=True, exist_ok=True)
        save_image = prepare_for_save(canvas, output_path)
        save_image.save(output_path)
        return output_path
    finally:
        for image in opened_images:
            image.close()


def main() -> None:
    args = parse_args()
    input_dir = args.input_dir.resolve()
    output_path = args.output.resolve() if args.output else input_dir / "merged_row.png"

    image_paths = find_images(input_dir)
    saved_path = merge_images_in_row(image_paths, output_path, args.background)

    print(f"Merged {len(image_paths)} images into: {saved_path}")


if __name__ == "__main__":
    main()
