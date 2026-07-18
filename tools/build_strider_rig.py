"""Build a stable sprite atlas by rigging one Chrome Strider painting in layers."""

import math
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools/art/chrome_strider_isolated_v1.png"
OUTPUT = ROOT / "src/assets/chrome_strider_rigged_sheet_v1.png"
FRAME = (240, 170)
CENTER = (120, 82)


def fit_source():
    image = Image.open(SOURCE).convert("RGBA")
    box = image.getchannel("A").getbbox()
    image = image.crop(box)
    image.thumbnail((208, 146), Image.Resampling.NEAREST)
    layer = Image.new("RGBA", FRAME)
    layer.alpha_composite(image, ((FRAME[0] - image.width) // 2, 5))
    return layer


def background():
    return Image.new("RGBA", FRAME, (0, 0, 0, 0))


def split_layers(source):
    core = Image.new("RGBA", FRAME)
    cage_pixels = Image.new("RGBA", FRAME)
    pixels = source.load()
    for y in range(FRAME[1]):
        for x in range(FRAME[0]):
            r, g, b, a = pixels[x, y]
            if a < 12:
                continue
            if r > 62 and r > g * 1.38 and r > b * 1.18 and 70 < x < 175 and 43 < y < 132:
                core.putpixel((x, y), (r, g, b, a))
            else:
                cage_pixels.putpixel((x, y), (r, g, b, a))
    # Split only along real transparent gaps. Angular wedges cut visible metal and
    # exposed black seams as the limbs moved.
    alpha = cage_pixels.getchannel("A")
    seen = set()
    cage = []
    for y in range(FRAME[1]):
        for x in range(FRAME[0]):
            if (x, y) in seen or alpha.getpixel((x, y)) < 18:
                continue
            stack = [(x, y)]
            seen.add((x, y))
            component = []
            while stack:
                px, py = stack.pop()
                component.append((px, py))
                for nx in range(max(0, px - 1), min(FRAME[0], px + 2)):
                    for ny in range(max(0, py - 1), min(FRAME[1], py + 2)):
                        if (nx, ny) not in seen and alpha.getpixel((nx, ny)) >= 18:
                            seen.add((nx, ny))
                            stack.append((nx, ny))
            if len(component) < 3:
                continue
            layer = Image.new("RGBA", FRAME)
            for px, py in component:
                layer.putpixel((px, py), cage_pixels.getpixel((px, py)))
            cx = sum(point[0] for point in component) / len(component)
            cy = sum(point[1] for point in component) / len(component)
            cage.append((layer, cx, cy))
    return core, cage


def move(layer, angle=0, scale=1, dx=0, dy=0):
    transformed = layer.rotate(angle, center=CENTER, resample=Image.Resampling.NEAREST)
    if scale != 1:
        w, h = round(FRAME[0] * scale), round(FRAME[1] * scale)
        transformed = transformed.resize((w, h), Image.Resampling.NEAREST)
        canvas = Image.new("RGBA", FRAME)
        canvas.alpha_composite(transformed, (CENTER[0] - round(CENTER[0] * scale),
                                             CENTER[1] - round(CENTER[1] * scale)))
        transformed = canvas
    shifted = Image.new("RGBA", FRAME)
    shifted.alpha_composite(transformed, (round(dx), round(dy)))
    return shifted


def render_frame(core, cage, state, step):
    image = background()
    phase = step / 8 * math.tau
    for index, (limb, cx, cy) in enumerate(cage):
        angle = math.sin(phase + index * .73) * .75
        reach = math.sin(phase + index * .61) * .45
        radial = math.atan2(cy - CENTER[1], cx - CENTER[0])
        scale = 1
        if state == 1:
            attack = (0, -.5, -1.4, -2.4, -1.2, 2.8, 4.3, .8)[step]
            angle += attack * (1 if index % 2 else -1)
            reach += (0, 0, -1, -2, -1, 3, 5, 1)[step]
        elif state == 2:
            angle += (0, 7, -5, 3, -2, 1, 0, 0)[step] * (1 if index % 2 else -1)
            reach += (0, 4, 2, -2, 1, 0, 0, 0)[step]
        elif state == 3:
            reach += step * 3.2
            angle += (index - 2.5) * step * 1.8
            scale = max(.32, 1 - step * .075)
        image.alpha_composite(move(limb, angle, scale,
                                   math.cos(radial) * reach,
                                   math.sin(radial) * reach))
    pulse = 1 + math.sin(phase) * .025
    if state == 1:
        pulse *= (1, .98, .94, .9, .95, 1.08, 1.14, 1.02)[step]
    elif state == 2:
        pulse *= (1, .88, .96, 1.04, .98, 1, 1, 1)[step]
    elif state == 3:
        pulse *= max(.12, 1 - step * .12)
    image.alpha_composite(move(core, step * .3, pulse, 0, step * 1.4 if state == 3 else 0))
    return image


def main():
    source = fit_source()
    core, cage = split_layers(source)
    atlas = Image.new("RGBA", (FRAME[0] * 8, FRAME[1] * 4), (0, 0, 0, 0))
    for state in range(4):
        for step in range(8):
            frame = render_frame(core, cage, state, step)
            atlas.paste(frame, (step * FRAME[0], state * FRAME[1]), frame)
    atlas.save(OUTPUT, optimize=True)
    print(OUTPUT)


if __name__ == "__main__":
    main()
