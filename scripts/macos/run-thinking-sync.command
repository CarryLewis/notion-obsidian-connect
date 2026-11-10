#!/bin/bash
# Double-clickable / Shortcuts-friendly wrapper for Notion → Obsidian sync.
set -euo pipefail
repo="${RESEARCH_BRIEF_REPO:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd -P)}"
exec /bin/bash "$repo/scripts/sync-to-local-obsidian.sh"
