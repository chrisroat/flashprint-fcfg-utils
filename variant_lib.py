import codecs
import struct


def decode_variant(s: str) -> bytes:
    """Decode the inner text of @Variant(...) into raw bytes.

    The file stores C-style escapes (e.g. \0, \x87). We decode using
    the 'unicode_escape' codec then encode to latin-1 to obtain the
    original byte values.
    """
    # first decode escape sequences into python str with the intended codepoints
    decoded = codecs.decode(s, "unicode_escape")
    # then map those codepoints 0-255 back to raw bytes
    result_bytes = decoded.encode("latin-1")

    # First four bytes are likely a length prefix; should be 0x00000087
    assert result_bytes[:4] == b"\x00\x00\x00\x87"

    # Second four bytes are a big-endian float
    return struct.unpack(">f", result_bytes[4:])[0]


def encode_variant(value: float) -> str:
    r"""Encode a float value into the inner-text used by @Variant(...).

    The original format stores raw bytes with C-style escapes (e.g. \x00\x87).
    We create the 8-byte blob: 4-byte prefix (0x00000087) + big-endian float32,
    then return a string of \xNN escapes suitable for placing directly inside
    @Variant(...).
    """
    prefix = b"\x00\x00\x00\x87"
    packed = struct.pack(">f", float(value))
    blob = prefix + packed

    # Empirical policy derived from existing files.
    # Note: 51 seems to be escaped occassionally, but mostly not, so we leave it unescaped.
    ALWAYS_ESCAPED = {52, 65, 66, 67, 69, 70, 102}

    out_parts = []
    for b in blob:
        if b == 0:
            out_parts.append("\\0")
        elif b == 12:
            out_parts.append("\\f")
        elif b in ALWAYS_ESCAPED:
            out_parts.append(f"\\x{b:02x}")
        else:
            # fallback: use unicode_escape for sensible escapes for non-printables
            ch = bytes([b]).decode("latin-1")
            esc = ch.encode("unicode_escape").decode("ascii")
            out_parts.append(esc)

    return "".join(out_parts)
