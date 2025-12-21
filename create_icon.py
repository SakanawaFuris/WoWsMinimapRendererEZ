from PIL import Image, ImageDraw, ImageFont
import os

# 複数サイズのアイコンを生成
sizes = [16, 32, 48, 64, 128, 256]
images = []

for size in sizes:
    # 背景：ダークブルー
    img = Image.new('RGBA', (size, size), (26, 58, 74, 255))
    draw = ImageDraw.Draw(img)

    # アンカーの形状を描画
    # 中心座標
    cx, cy = size // 2, size // 2

    # サイズに応じたスケール
    scale = size / 64

    # アンカーのメインボディ（縦棒）
    body_width = max(int(4 * scale), 2)
    body_height = int(28 * scale)
    draw.rectangle(
        [cx - body_width // 2, cy - body_height // 2,
         cx + body_width // 2, cy + body_height // 2],
        fill=(255, 107, 53, 255)  # オレンジ
    )

    # 上部のリング
    ring_radius = int(6 * scale)
    draw.ellipse(
        [cx - ring_radius, cy - body_height // 2 - ring_radius * 2,
         cx + ring_radius, cy - body_height // 2],
        fill=(26, 58, 74, 255),  # 背景色（穴を開ける）
        outline=(255, 107, 53, 255),
        width=max(int(2 * scale), 1)
    )

    # 下部の横棒（アンカーの腕）
    arm_width = int(24 * scale)
    arm_height = max(int(3 * scale), 2)
    draw.rectangle(
        [cx - arm_width // 2, cy + body_height // 2 - arm_height,
         cx + arm_width // 2, cy + body_height // 2],
        fill=(255, 107, 53, 255)
    )

    # 左右のフック
    hook_size = int(8 * scale)
    # 左フック
    draw.polygon(
        [
            (cx - arm_width // 2, cy + body_height // 2 - arm_height),
            (cx - arm_width // 2 - hook_size // 2, cy + body_height // 2 + hook_size // 2),
            (cx - arm_width // 2, cy + body_height // 2)
        ],
        fill=(255, 107, 53, 255)
    )
    # 右フック
    draw.polygon(
        [
            (cx + arm_width // 2, cy + body_height // 2 - arm_height),
            (cx + arm_width // 2 + hook_size // 2, cy + body_height // 2 + hook_size // 2),
            (cx + arm_width // 2, cy + body_height // 2)
        ],
        fill=(255, 107, 53, 255)
    )

    images.append(img)

# .icoファイルとして保存
images[0].save('icon.ico', format='ICO', sizes=[(img.width, img.height) for img in images], append_images=images[1:])
print("Icon created: icon.ico")
