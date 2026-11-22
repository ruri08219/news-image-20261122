"""news-image-20261122 — one image summing up 22 November 2026 world news.

The entry image (entry.png, kept alongside this script) is a front page
with 35 date-checked stories across 7 regions: the overnight Gulf
escalation (Iran hits four US bases in Bahrain and three tankers in the
Strait of Hormuz), the COP31 final deal unveiled at dawn in Antalya,
Rishabh Pant's record 128 in Wellington, plus France taking Myanmar to
the UN Security Council, the US curbing military ties with Canada,
Denmark expelling a Russian attache, and 29 more stories — with a world
map of numbered pins, a "day in numbers" strip, per-region counts, and a
DATE CHECK footer naming the stories left out as other days' news.
Every story was reported on Sunday 22 November 2026, with its wire
source (Reuters, AP, AFP, Al Jazeera, PTI, AAP, Arab News) printed
beside it.

This script does one small, honest job: it copies the entry image, byte
for byte, to /output/entry.png so the competition runner can find it.
It uses only the Python standard library, so it runs in the sandbox
exactly as it runs here: no Pillow, no fonts, no network, no files
outside this repository. The bundled file must match its recorded size
and SHA-256, and the copy is checked again after it lands, so a damaged
or swapped image can never pass as the entry.

The program is deterministic: it reads no clock, no network and no
randomness, so two runs produce identical bytes.

Provenance: entry.png was drawn locally by build_image.py (Pillow,
flat-drawn illustrations, DejaVu) from the same 35-story front-page
design; the news was researched from 22 November 2026 wires before
drawing. The drawing runs on the builder's machine only — this script
is the whole program the sandbox runs.
"""

import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png"
DESTINATION = Path("/output/entry.png")

# Recorded at build time from the shipped file; the copy refuses to run
# if the bundled image ever differs from the one that was checked.
EXPECTED_SIZE = 186897
EXPECTED_SHA256 = "317ef380f3055f328b4d54a211740463a1e72c8e62c38e78b108ccbb7c33ec1b"


def load_entry_image() -> bytes:
    """Read entry.png next to this script; fail loudly if it is absent."""
    if not SOURCE.is_file():
        raise FileNotFoundError(
            f"entry image not found next to this script: {SOURCE}"
        )
    data = SOURCE.read_bytes()
    if not data:
        raise ValueError(f"entry image is empty: {SOURCE}")
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("entry image is not a PNG (bad magic bytes)")
    if len(data) > 1048576:
        raise ValueError(
            f"entry image over the 1 MiB gate limit: {len(data)} bytes"
        )
    if len(data) != EXPECTED_SIZE:
        raise ValueError(
            f"entry image size changed: {len(data)} bytes, "
            f"expected {EXPECTED_SIZE}"
        )
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError(
            f"entry image hash changed: {digest}, expected {EXPECTED_SHA256}"
        )
    return data


def main() -> int:
    """Copy entry.png to /output/entry.png and report the size."""
    data = load_entry_image()
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    DESTINATION.write_bytes(data)
    written = DESTINATION.read_bytes()
    if written != data:
        raise ValueError("written copy does not match the bundled image")
    print(f"Wrote {len(data)} bytes to {DESTINATION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
