#!/usr/bin/env python3
from pathlib import Path
import subprocess, sys
ROOT = Path(__file__).resolve().parents[2]
raise SystemExit(subprocess.run([sys.executable, str(ROOT / "scripts/validate_domain_maturity.py"), *sys.argv[1:], "advertising-analysis-measurement-optimization"]).returncode)
