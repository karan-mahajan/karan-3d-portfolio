"""
Phase 1: Bake the locked 25-color palette to static/textures/palette.png.

What this produces (after running):
- A 128x4 sRGB RGBA PNG at static/textures/palette.png.
- 25 cells, each 5 px wide x 4 px tall, packed left-to-right (x=0..124).
- Right-edge padding (x=125..127, 12 px) filled with mist_horizon so any
  UV that strays into it reads as fog tan, not a wrong palette color.
- Embedded sRGB chunk (rendering intent 0) so viewers + the runtime
  texture loader treat the bytes as sRGB-encoded, not linear.

The runtime palette material samples this with NearestFilter; each material
picks its color by setting UV to the cell center returned by
_palette.cell_uv(index).

Does NOT touch tools/blender/world.blend. The palette is a runtime asset,
not authored in Blender.

How to run:
  From the repo root, in a normal terminal (no Blender needed):
    python3 tools/blender/scripts/phase-01-palette-texture.py

  The same file also runs fine pasted into Blender's Text Editor (Alt+P),
  but stdlib alone is sufficient — no Pillow, no numpy.
"""

import os
import struct
import sys
import zlib


# tools/blender/scripts/ is on sys.path so _palette imports cleanly even
# when CWD is elsewhere. Same dance as phase-00-setup.py because Blender's
# Text Editor sets __file__ to the buffer name, not the disk path.
def _script_dir():
    candidates = []
    try:
        if __file__ and os.path.isabs(__file__):
            candidates.append(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        pass

    try:
        import bpy  # type: ignore
        space = getattr(bpy.context, "space_data", None)
        text = getattr(space, "text", None) if space else None
        if text and text.filepath:
            candidates.append(
                os.path.dirname(os.path.abspath(bpy.path.abspath(text.filepath)))
            )
    except ImportError:
        pass

    candidates.append(
        os.path.expanduser(
            "~/Documents/Projects/karan-portfolio/tools/blender/scripts"
        )
    )

    for path in candidates:
        if os.path.isfile(os.path.join(path, "_palette.py")):
            return path

    raise RuntimeError(
        "Could not locate _palette.py - tried: " + ", ".join(candidates)
    )


SCRIPT_DIR = _script_dir()
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import _palette  # noqa: E402


# _lib imports bpy at module load time, which fails outside Blender. The
# LOG_PREFIX value is the only thing Phase 1 needs from it, so fall back
# to the same literal when bpy isn't available. Keeps prefixes uniform
# across phases without forcing Blender as a dependency.
try:
    import _lib  # noqa: E402
    _LOG_PREFIX = _lib.LOG_PREFIX
except ImportError:
    _LOG_PREFIX = "[blender-build]"


_CELL_WIDTH_PX = 5
_IMAGE_WIDTH = 128
_IMAGE_HEIGHT = 4
_PADDING_COLOR_KEY = "mist_horizon"


def _output_path():
    return os.path.abspath(
        os.path.join(SCRIPT_DIR, "..", "..", "..", "static", "textures", "palette.png")
    )


def _hex_to_rgb_bytes(hex_str):
    r, g, b = _palette.hex_to_rgb_floats(hex_str)
    return (round(r * 255.0), round(g * 255.0), round(b * 255.0))


def _build_pixel_rows():
    """
    Build the raw RGBA pixel buffer for the 128x4 image as a list of
    bytearray rows (one row = 128 * 4 bytes).
    """
    padding_rgb = _hex_to_rgb_bytes(_palette.PALETTE_COLORS[_PADDING_COLOR_KEY])

    cell_rgb = []
    for key, hex_str in _palette.PALETTE_COLORS.items():
        cell_rgb.append(_hex_to_rgb_bytes(hex_str))

    if len(cell_rgb) != 25:
        raise RuntimeError(
            f"expected 25 palette colors, got {len(cell_rgb)} - "
            f"_palette.PALETTE_COLORS must define exactly 25 entries"
        )

    row = bytearray(_IMAGE_WIDTH * 4)
    for x in range(_IMAGE_WIDTH):
        cell_index = x // _CELL_WIDTH_PX
        if cell_index < len(cell_rgb):
            r, g, b = cell_rgb[cell_index]
        else:
            r, g, b = padding_rgb
        i = x * 4
        row[i] = r
        row[i + 1] = g
        row[i + 2] = b
        row[i + 3] = 255

    return [bytes(row) for _ in range(_IMAGE_HEIGHT)]


def _chunk(type_bytes, data):
    """Assemble one PNG chunk: length || type || data || crc32(type+data)."""
    crc = zlib.crc32(type_bytes + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + type_bytes + data + struct.pack(">I", crc)


def _encode_png(rows):
    """
    Encode an RGBA 8-bit PNG from a list of pre-flattened row bytes.
    Each row is prefixed with filter byte 0x00 ("None") before zlib
    compression at level 9 for deterministic output.
    """
    signature = b"\x89PNG\r\n\x1a\n"

    ihdr = struct.pack(
        ">IIBBBBB",
        _IMAGE_WIDTH,
        _IMAGE_HEIGHT,
        8,    # bit depth
        6,    # color type: RGBA
        0,    # compression: deflate
        0,    # filter: adaptive (we use filter type 0 = None per row)
        0,    # interlace: none
    )

    # sRGB chunk: payload is one byte = rendering intent. 0 = perceptual.
    # Without this, some viewers (and the GLTF loader's auto-color-space
    # detection) treat the bytes as linear and the colors render washed
    # out. The palette is authored in sRGB hex codes, so flag it sRGB.
    srgb = b"\x00"

    filtered = bytearray()
    for row in rows:
        filtered.append(0x00)  # filter type "None" per scanline
        filtered.extend(row)
    idat = zlib.compress(bytes(filtered), 9)

    return (
        signature
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"sRGB", srgb)
        + _chunk(b"IDAT", idat)
        + _chunk(b"IEND", b"")
    )


def _write_palette_png(path):
    rows = _build_pixel_rows()
    png_bytes = _encode_png(rows)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(png_bytes)
    return len(png_bytes)


def _verify_png(path):
    """
    Re-open the freshly written PNG and validate header + a few known
    pixel values. Raises AssertionError on any drift so a broken bake
    fails loud instead of leaving a corrupt asset behind.
    """
    with open(path, "rb") as f:
        data = f.read()

    assert data[:8] == b"\x89PNG\r\n\x1a\n", "PNG signature missing"

    # IHDR is always the first chunk, starting at byte 8.
    ihdr_len = struct.unpack(">I", data[8:12])[0]
    assert data[12:16] == b"IHDR", "first chunk is not IHDR"
    width, height, bit_depth, color_type = struct.unpack(
        ">IIBB", data[16:16 + 10]
    )
    assert width == _IMAGE_WIDTH, f"width {width} != {_IMAGE_WIDTH}"
    assert height == _IMAGE_HEIGHT, f"height {height} != {_IMAGE_HEIGHT}"
    assert bit_depth == 8, f"bit depth {bit_depth} != 8"
    assert color_type == 6, f"color type {color_type} != 6 (RGBA)"
    assert ihdr_len == 13, f"IHDR length {ihdr_len} != 13"

    size = len(data)
    assert 200 <= size <= 1000, (
        f"PNG size {size} bytes is outside expected 200..1000 - "
        f"compression may have regressed or content drifted"
    )

    # Walk chunks to find every IDAT (PNG allows multiple; we emit one).
    idat = bytearray()
    pos = 8
    while pos < len(data):
        chunk_len = struct.unpack(">I", data[pos:pos + 4])[0]
        chunk_type = data[pos + 4:pos + 8]
        chunk_data = data[pos + 8:pos + 8 + chunk_len]
        if chunk_type == b"IDAT":
            idat.extend(chunk_data)
        pos += 8 + chunk_len + 4  # length + type + data + crc

    raw = zlib.decompress(bytes(idat))
    stride = _IMAGE_WIDTH * 4
    # Each row is filter_byte (1) + stride RGBA bytes.
    pixels = bytearray()
    for y in range(_IMAGE_HEIGHT):
        row_start = y * (stride + 1)
        filter_byte = raw[row_start]
        assert filter_byte == 0, f"row {y} filter {filter_byte} != 0"
        pixels.extend(raw[row_start + 1:row_start + 1 + stride])

    def px(x, y):
        i = (y * _IMAGE_WIDTH + x) * 4
        return (pixels[i], pixels[i + 1], pixels[i + 2], pixels[i + 3])

    # Spot-check 3 cell centers + 1 padding pixel. Cell indices are derived
    # from _palette.PALETTE_COLORS insertion order; pine_canopy is at
    # index 13 (not 12 as an early spec draft suggested) so its centre is
    # at x = 13*5 + 2 = 67.
    pine_idx = list(_palette.PALETTE_COLORS).index("pine_canopy")
    pine_x = pine_idx * _CELL_WIDTH_PX + _CELL_WIDTH_PX // 2
    expected = [
        ((2, 2),     (198, 195, 188, 255), "cell 0 sky_high #c6c3bc"),
        ((pine_x, 2), (58, 85, 54, 255),   f"cell {pine_idx} pine_canopy #3a5536"),
        ((122, 2),   (176, 151, 120, 255), "cell 24 sand_gravel #b09778"),
        ((126, 2),   (224, 212, 192, 255), "padding mist_horizon #e0d4c0"),
    ]
    for (x, y), want, label in expected:
        got = px(x, y)
        assert got == want, f"{label} at ({x},{y}): got {got}, want {want}"


def main():
    path = _output_path()
    size = _write_palette_png(path)
    _verify_png(path)
    print(
        f"{_LOG_PREFIX}[phase-01] OK - wrote {path} "
        f"({size} bytes, 128x4, 25 cells)"
    )


if __name__ == "__main__":
    main()
