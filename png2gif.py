from PIL import Image
import imageio.v2 as imageio
import numpy as np


def cover_resize(img: Image.Image, target_size: tuple[int, int]) -> Image.Image:
    """
    类似 CSS 的 background-size: cover
    按比例缩放后中心裁剪到目标尺寸
    """
    target_w, target_h = target_size
    w, h = img.size

    scale = max(target_w / w, target_h / h)
    new_w = int(w * scale)
    new_h = int(h * scale)

    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))


def ease_out_back(t: float, s: float = 1.4) -> float:
    """
    带一点回弹感的 ease-out
    t 范围 0~1
    """
    t -= 1.0
    return 1.0 + (s + 1.0) * t * t * t + s * t * t


def paste_rgba_clipped(base: Image.Image, overlay: Image.Image, x: int, y: int) -> Image.Image:
    """
    把 RGBA overlay 粘贴到 base 上，支持 overlay 一部分在画布外
    """
    base = base.convert("RGBA")
    overlay = overlay.convert("RGBA")

    bw, bh = base.size
    ow, oh = overlay.size

    left = max(0, x)
    top = max(0, y)
    right = min(bw, x + ow)
    bottom = min(bh, y + oh)

    if right <= left or bottom <= top:
        return base

    crop = overlay.crop((left - x, top - y, right - x, bottom - y))

    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    layer.paste(crop, (left, top), crop)

    return Image.alpha_composite(base, layer)


def get_overlay_box(
    base_size: tuple[int, int],
    overlay_scale: float = 1 / 3,
    margin_ratio: float = 0.0,
):
    """
    返回左下角小图区域的位置和尺寸
    """
    bw, bh = base_size
    box_w = int(bw * overlay_scale)
    box_h = int(bh * overlay_scale)

    margin_x = int(bw * margin_ratio)
    margin_y = int(bh * margin_ratio)

    x = margin_x
    y = bh - box_h - margin_y

    return x, y, box_w, box_h


def stage1_float_in_overlay(
    img1: Image.Image,
    img3: Image.Image,
    overlay_scale: float = 1 / 3,
    margin_ratio: float = 0.0,
    still_frames: int = 4,
    enter_frames: int = 8,
    hold_frames: int = 4,
):
    """
    第一阶段：
    - 先停留几帧，只显示 img1
    - 然后 img3 作为完整小图层，从左下方快速浮入
    - 最后停留几帧
    """
    base = img1.convert("RGBA")
    bw, bh = base.size

    x, y, box_w, box_h = get_overlay_box(
        base_size=(bw, bh),
        overlay_scale=overlay_scale,
        margin_ratio=margin_ratio,
    )

    frames = []

    for _ in range(still_frames):
        frames.append(np.array(base))

    for i in range(enter_frames):
        p = (i + 1) / enter_frames
        e = ease_out_back(p)

        scale = 0.78 + 0.22 * e
        cur_w = max(1, int(box_w * scale))
        cur_h = max(1, int(box_h * scale))

        overlay_cur = cover_resize(img3.convert("RGBA"), (cur_w, cur_h))

        offset_down = int((1.0 - p) * 18)

        cur_x = x
        cur_y = bh - cur_h - int(bh * margin_ratio) + offset_down

        frame = paste_rgba_clipped(base, overlay_cur, cur_x, cur_y)
        frames.append(np.array(frame))

    final_overlay = cover_resize(img3.convert("RGBA"), (box_w, box_h))
    final_frame = paste_rgba_clipped(base, final_overlay, x, y)

    for _ in range(hold_frames):
        frames.append(np.array(final_frame))

    return frames, (x, y, box_w, box_h)


def stage2_diagonal_cover_exclude_overlay(
    composite_frame: np.ndarray,
    img2: Image.Image,
    overlay_box: tuple[int, int, int, int],
    n_frames: int = 24,
    feather: int = 36,
):
    """
    第二阶段：
    用第二张图从左下 -> 右上覆盖当前画面，
    但跳过 overlay_box 对应的小区域，不覆盖那一块。
    """
    h, w = composite_frame.shape[:2]

    target = cover_resize(img2.convert("RGBA"), (w, h))
    target_np = np.array(target).astype(np.float32)
    base_np = composite_frame.astype(np.float32)

    yy, xx = np.mgrid[0:h, 0:w]

    # 左下角最先开始，右上角最后结束
    score = xx + (h - 1 - yy)
    score = score.astype(np.float32)

    score_min = 0.0
    score_max = float((w - 1) + (h - 1))

    ox, oy, ow, oh = overlay_box

    # 保护区域 mask：左下角第三张图所在区域永远不被第二张图覆盖
    protect_mask = np.zeros((h, w), dtype=np.float32)
    protect_mask[oy:oy + oh, ox:ox + ow] = 1.0

    frames = []

    for i in range(n_frames):
        progress = i / (n_frames - 1)
        threshold = score_min + progress * (score_max - score_min)

        if feather <= 0:
            mask = (score <= threshold).astype(np.float32)
        else:
            half = feather / 2.0
            mask = 1.0 - (score - (threshold - half)) / max(feather, 1e-6)
            mask = np.clip(mask, 0.0, 1.0)

        # 保护左下角小区域：该区域强制不覆盖
        mask = mask * (1.0 - protect_mask)
        mask = mask[..., None]

        frame = base_np * (1.0 - mask) + target_np * mask
        frame = np.clip(frame, 0, 255).astype(np.uint8)
        frames.append(frame)

    return frames


def save_gif(frames, out_path: str, fps: int = 18):
    imageio.mimsave(out_path, frames, duration=1 / fps, loop=0)
    print(f"Saved GIF to: {out_path}")


def main():
    img1_path = "temp_images/dit_content.png"   # 第一张图：初始底图
    img2_path = "temp_images/dit_target.png"   # 第二张图：最终覆盖图
    img3_path = "temp_images/dit_ref.png"   # 第三张图：浮入左下角的小图

    overlay_scale = 1 / 3
    margin_ratio = 0.0

    img1 = Image.open(img1_path).convert("RGBA")
    img2 = Image.open(img2_path).convert("RGBA")
    img3 = Image.open(img3_path).convert("RGBA")

    img2 = cover_resize(img2, img1.size)

    # 第一阶段：第三张图浮入
    stage1_frames, overlay_box = stage1_float_in_overlay(
        img1=img1,
        img3=img3,
        overlay_scale=overlay_scale,
        margin_ratio=margin_ratio,
        still_frames=4,
        enter_frames=8,
        hold_frames=4,
    )

    composite_last = stage1_frames[-1]

    # 第二阶段：第二张图覆盖，但跳过左下角第三张图区域
    stage2_frames = stage2_diagonal_cover_exclude_overlay(
        composite_frame=composite_last,
        img2=img2,
        overlay_box=overlay_box,
        n_frames=24,
        feather=36,   # 改成 0 就是硬切换
    )

    all_frames = stage1_frames + stage2_frames

    save_gif(all_frames, out_path="two_stage_result_keep_overlay.gif", fps=18)


if __name__ == "__main__":
    main()