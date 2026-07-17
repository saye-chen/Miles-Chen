#!/usr/bin/env python3
"""Validate CIG and cross-domain output contracts through the shared kernel."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).resolve().parents[2] / "scripts/validate_decision_contract.py"), run_name="__main__")
