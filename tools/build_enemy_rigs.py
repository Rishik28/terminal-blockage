"""Build stable four-state atlases from isolated enemy paintings."""

import math
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
FRAME = (240, 170)
CENTER = (120, 82)
ENEMIES = {
    "memory_pool": ("tools/art/memory_pool_isolated_v1.png", (2, 5, 13), (5, 70, 78), (0, 185, 190)),
    "chaos_jester": ("tools/art/chaos_jester_isolated_v1.png", (3, 3, 13), (55, 12, 68), (255, 75, 115)),
    "monument": ("tools/art/monument_isolated_v1.png", (3, 5, 13), (15, 68, 78), (255, 105, 115)),
    "silicon_cortex": ("tools/art/silicon_cortex_isolated_v1.png", (3, 4, 13), (28, 55, 74), (0, 185, 190)),
}


def fit(path):
    source = Image.open(ROOT / path).convert("RGBA")
    source = source.crop(source.getchannel("A").getbbox())
    source.thumbnail((214, 151), Image.Resampling.NEAREST)
    image = Image.new("RGBA", FRAME)
    image.alpha_composite(source, ((240 - source.width) // 2, (164 - source.height) // 2))
    return image


def backdrop(colors):
    return Image.new("RGBA", FRAME, (0, 0, 0, 0))


def components(image):
    alpha = image.getchannel("A")
    seen = set()
    result = []
    for y in range(170):
        for x in range(240):
            if (x, y) in seen or alpha.getpixel((x, y)) < 18:
                continue
            queue = deque([(x, y)])
            seen.add((x, y))
            points = []
            while queue:
                px, py = queue.popleft()
                points.append((px, py))
                for nx in range(max(0, px - 1), min(240, px + 2)):
                    for ny in range(max(0, py - 1), min(170, py + 2)):
                        if (nx, ny) not in seen and alpha.getpixel((nx, ny)) >= 18:
                            seen.add((nx, ny))
                            queue.append((nx, ny))
            if len(points) < 4:
                continue
            layer = Image.new("RGBA", FRAME)
            for point in points:
                layer.putpixel(point, image.getpixel(point))
            result.append((layer, sum(x for x, _ in points) / len(points),
                           sum(y for _, y in points) / len(points), len(points)))
    return sorted(result, key=lambda item: item[3], reverse=True)


def move(layer, angle=0, scale=1, dx=0, dy=0):
    item = layer.rotate(angle, center=CENTER, resample=Image.Resampling.NEAREST)
    if scale != 1:
        size = (round(240 * scale), round(170 * scale))
        item = item.resize(size, Image.Resampling.NEAREST)
        canvas = Image.new("RGBA", FRAME)
        canvas.alpha_composite(item, (120 - round(120 * scale), 82 - round(82 * scale)))
        item = canvas
    canvas = Image.new("RGBA", FRAME)
    canvas.alpha_composite(item, (round(dx), round(dy)))
    return canvas


def motion(kind, index, cx, cy, state, step):
    phase = step / 8 * math.tau
    radial = math.atan2(cy - CENTER[1], cx - CENTER[0])
    main = index == 0
    angle = dx = dy = 0
    scale = 1
    if state == 0:
        if kind == "memory_pool":
            dy = math.sin(phase + index * .7) * (1 if main else 2.4)
            dx = math.cos(phase + index) * (.25 if main else .8)
        elif kind == "chaos_jester":
            angle = math.sin(phase + index * .9) * (1.1 if main else 2.4)
            dy = math.sin(phase + index * .63) * (1 if main else 1.8)
        elif kind == "monument":
            dy = math.sin(phase) * .65 if main else math.sin(phase + index) * 1.7
            angle = 0 if main else math.sin(phase + index) * 1.8
        else:
            dx = math.sin(phase + index * .4) * (.35 if main else 1.2)
            dy = math.cos(phase + index * .8) * (.45 if main else 1.7)
            angle = math.sin(phase + index) * (.35 if main else 1.5)
    elif state == 1:
        force = (0, .5, 1.2, 2.2, 1.2, -2.8, -4.2, -.7)[step]
        if kind == "memory_pool":
            dy = force * (-1 if main else 1.7)
            scale = 1 + (0 if main else abs(force) * .008)
        elif kind == "chaos_jester":
            angle = force * (-1 if index % 2 else 1)
            dx = math.cos(radial) * abs(force) * .7
            dy = math.sin(radial) * abs(force) * .7
        elif kind == "monument":
            dx = force * (-.35 if main else math.cos(radial))
            dy = force * (-.2 if main else math.sin(radial))
            scale = 1 + (max(0, -force) * .012 if main else 0)
        else:
            dx = force * (-.25 if main else math.cos(radial) * .75)
            dy = force * (.18 if main else math.sin(radial) * .75)
            angle = force * (-.3 if index % 2 else .3)
            scale = 1 + abs(force) * (.006 if main else .012)
    elif state == 2:
        shake = (0, 5, -4, 3, -2, 1, 0, 0)[step]
        dx = shake * (1 if main else .7)
        angle = shake * (.3 if main else .8) * (-1 if index % 2 else 1)
    else:
        distance = step * (2.4 if main else 4.2)
        dx = math.cos(radial) * distance
        dy = math.sin(radial) * distance + step * .7
        angle = (index - 2) * step * 1.4
        scale = max(.15, 1 - step * (.1 if main else .075))
    return angle, scale, dx, dy


def build(kind, spec):
    source = fit(spec[0])
    if kind == "silicon_cortex":
        source.save(ROOT / "src/assets/enemy_silicon_cortex_v1.png", optimize=True)
    pieces = components(source)
    atlas = Image.new("RGBA", (1920, 680), (0, 0, 0, 0))
    for state in range(4):
        for step in range(8):
            frame = backdrop(spec[1:])
            for index, (layer, cx, cy, _) in enumerate(pieces):
                frame.alpha_composite(move(layer, *motion(kind, index, cx, cy, state, step)))
            atlas.paste(frame, (step * 240, state * 170), frame)
    output = ROOT / f"src/assets/{kind}_rigged_sheet_v1.png"
    atlas.save(output, optimize=True)
    print(output)


for enemy, enemy_spec in ENEMIES.items():
    build(enemy, enemy_spec)
