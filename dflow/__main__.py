"""Print one result envelope for the optional command."""
import json
import sys

from .telemetry import run

if __name__ == "__main__":
    result, code = run(sys.argv[1:])
    print(json.dumps(result, separators=(",", ":"), allow_nan=False))
    raise SystemExit(code)
