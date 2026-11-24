#!/bin/bash
set -eo pipefail

python3 "${GITHUB_WORKSPACE}/ci/resolve_conflicts.py"
exit 0
