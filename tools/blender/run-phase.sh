#!/usr/bin/env bash
# Run a Blender world-build phase script headless and stream all output to
# the terminal. Avoids the "open Blender, Text Editor, Alt+P, hunt the Info
# Editor for output" loop.
#
# Usage:
#   ./tools/blender/run-phase.sh 13
#   ./tools/blender/run-phase.sh 12
#
# Exits non-zero if Blender exits non-zero (e.g. RuntimeError from the
# phase script). All print() output from the script is visible in the
# terminal, including assertion failure lists.
#
# Override the Blender binary with BLENDER=/path/to/blender.
set -euo pipefail

PHASE="${1:-}"
if [[ -z "$PHASE" ]]; then
  echo "usage: $0 <phase-number>   (e.g. $0 13)" >&2
  exit 2
fi

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BLEND="$HERE/world.blend"

PADDED=$(printf '%02d' "$PHASE")
SCRIPT=$(ls "$HERE/scripts/phase-${PADDED}-"*.py 2>/dev/null | head -n1 || true)
if [[ -z "$SCRIPT" || ! -f "$SCRIPT" ]]; then
  echo "no script found matching $HERE/scripts/phase-${PADDED}-*.py" >&2
  exit 2
fi

BLENDER_BIN="${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}"
if [[ ! -x "$BLENDER_BIN" ]]; then
  ALT=$(command -v blender 2>/dev/null || true)
  if [[ -n "$ALT" && -x "$ALT" ]]; then
    BLENDER_BIN="$ALT"
  else
    echo "Blender binary not found. Tried: $BLENDER_BIN" >&2
    echo "Override with BLENDER=/path/to/blender $0 $PHASE" >&2
    exit 2
  fi
fi

echo "[run-phase] blender:  $BLENDER_BIN"
echo "[run-phase] blend:    $BLEND"
echo "[run-phase] script:   $SCRIPT"
echo "[run-phase] -----"

exec "$BLENDER_BIN" --background "$BLEND" --python "$SCRIPT"
