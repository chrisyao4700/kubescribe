#!/usr/bin/env bash
set -euo pipefail
python -m venv .venv && source .venv/bin/activate
pip install -U pip && pip install -e .
python -m kubescribe_core_runner.main
