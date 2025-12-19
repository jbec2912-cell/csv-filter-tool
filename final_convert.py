#!/usr/bin/env python3
"""Wrapper that delegates to the shared converter."""

import sys
from pathlib import Path

from convert_appointment import OUTPUT_NAME, convert_content


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python final_convert.py /path/to/source.csv")
        sys.exit(1)

    src_path = Path(sys.argv[1]).expanduser()
    if not src_path.is_file():
        print(f"Source file not found: {src_path}")
        sys.exit(1)

    content = src_path.read_text(encoding="utf-8-sig")

    try:
        converted_csv, row_count = convert_content(content)
    except Exception as exc:  # noqa: BLE001
        print(f"Conversion failed: {exc}")
        sys.exit(1)

    out_path = src_path.with_name(OUTPUT_NAME)
    out_path.write_text(converted_csv, encoding="utf-8")
    print(f"✓ Wrote {row_count} rows to {out_path}")


if __name__ == "__main__":
    main()
