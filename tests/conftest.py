"""Shared pytest configuration."""

import sys
from pathlib import Path

# Make `src/...` imports work without packaging the project.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
