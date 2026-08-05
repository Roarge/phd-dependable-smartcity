#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ -f "$HOME/.elan/env" ]; then
  # shellcheck disable=SC1090
  source "$HOME/.elan/env"
fi

if ! command -v lake >/dev/null 2>&1; then
  echo "lake is required. Install Lean using elan first." >&2
  exit 1
fi

(
  cd analysis/section5_1/setup/lean
  lake env lean "$ROOT_DIR/analysis/section5_6/setup/proofs/Section5_6.lean"
)

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate
export PYTHONHASHSEED=0

python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r analysis/requirements.txt

python analysis/section5_6/setup/scripts/generate_section5_6.py
