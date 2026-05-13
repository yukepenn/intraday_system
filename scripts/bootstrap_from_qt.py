"""bootstrap_from_qt.py

Intentional placeholder. QT is a read-only reference repository; this project
deliberately does NOT bootstrap by copying QT structure or code. See
``docs/QT_REFERENCE_POLICY.md`` for the policy.

If you find yourself wanting to ``cp`` from QT into ``src/`` — stop. Re-implement
cleanly from concepts and add a regression test in ``tests/regression/`` instead.
"""

from __future__ import annotations

import sys


def main() -> int:
    print(
        "bootstrap_from_qt.py is intentionally not implemented.\n"
        "See docs/QT_REFERENCE_POLICY.md.\n"
        "QT is a read-only reference; this repo does not auto-port QT code."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
