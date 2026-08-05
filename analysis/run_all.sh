#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

"$SCRIPT_DIR/run_section5_1.sh"
"$SCRIPT_DIR/run_section5_2.sh"
"$SCRIPT_DIR/run_section5_3.sh"
"$SCRIPT_DIR/run_section5_4.sh"
"$SCRIPT_DIR/run_section5_5.sh"
"$SCRIPT_DIR/run_section5_6.sh"
"$SCRIPT_DIR/run_section5_7.sh"
