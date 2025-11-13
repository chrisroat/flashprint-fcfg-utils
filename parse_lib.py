import ast
import re

from variant_lib import decode_variant, encode_variant

KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=(\s*(.+))?$")


def fcfg_to_value(line: str):
    """Parse a single config line into (key, value).

    Supported value types:
    - @Variant(...): returns bytes (the decoded inner contents)
    - []: returns a list (possibly nested)
    - true/false: returns bool
    - int: returns int
    Any surrounding single/double quotes around the RHS are removed.
    """
    m = KEY_RE.match(line)
    if not m:
        raise ValueError(f"Invalid line in config: {line}")
    key, raw_val = m.group(1), m.group(2)
    if raw_val is None:
        return key, raw_val

    # strip surrounding quotes if present
    if (raw_val.startswith('"') and raw_val.endswith('"')) or (
        raw_val.startswith("'") and raw_val.endswith("'")
    ):
        raw_val = raw_val[1:-1]

    # Variant
    if raw_val.startswith("@Variant(") and raw_val.endswith(")"):
        inner = raw_val[len("@Variant(") : -1]
        return key, decode_variant(inner)

    # bracketed lists (could be quoted in the file)
    # Accepts: [], [1,4], [[1,1,20],[2,4,90]]
    if raw_val.startswith("[") and raw_val.endswith("]"):
        try:
            value = ast.literal_eval(raw_val)
        except Exception:
            raise ValueError(f"Invalid list syntax for key {key}: {raw_val}")
        return key, value

    # booleans
    if raw_val == "true":
        return key, True
    if raw_val == "false":
        return key, False

    # integer
    if re.fullmatch(r"-?\d+", raw_val):
        return key, int(raw_val)

    # fallback: return raw string
    return key, raw_val


def value_to_fcfg(value):
    """Convert a Python value back to an .fcfg RHS string (without key=).

    Rules:
    - floats that were variants should be encoded with @Variant(...)
      (we detect float inside a special wrapper elsewhere; here we only
      support encoding plain floats as numeric literals)
    - lists and nested lists are rendered using Python-style brackets
    - booleans as 'true'/'false'
    - ints as decimal literals
    - strings are returned as-is (caller should quote if needed)
    """
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        # encode as @Variant(...) to match original storage
        inner = encode_variant(value)
        if inner.find("=") != -1:
            return f'"@Variant({inner})"'
        return f"@Variant({inner})"
    if isinstance(value, (list, tuple)):
        return repr(value)
    # fallback for strings
    return value
