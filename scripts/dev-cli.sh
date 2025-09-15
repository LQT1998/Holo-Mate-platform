#!/usr/bin/env bash
set -euo pipefail

# dev-cli: Unified runner for backend service CLIs
# - Activates venv if available
# - Sets PYTHONPATH so imports from shared/ work
# - Provides friendly routing to each service's CLI module

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"

usage() {
  cat <<'USAGE'
Usage:
  scripts/dev-cli.sh <service> [group] <command> [args...]

Services and groups:
  auth                                 → auth_service/src/cli/user_commands.py
  ai                                   → ai_service/src/cli/app.py (sub: companion|conversation)
  stream                               → streaming_service/src/cli/app.py (sub: device|session)

Examples:
  scripts/dev-cli.sh auth create-user --email test@example.com --password secret
  scripts/dev-cli.sh ai companion create --name Luna
  scripts/dev-cli.sh ai conversation start --companion-id 123 --title "Hello"
  scripts/dev-cli.sh stream device register --serial DEV-001
  scripts/dev-cli.sh stream session start --user-id 123
USAGE
}

# Activate the first available virtual environment
activate_venv() {
  local candidates=(
    "$ROOT_DIR/.venv/bin/activate"
    "$ROOT_DIR/backend/.venv/bin/activate"
    "$ROOT_DIR/venv/bin/activate"
    "$ROOT_DIR/backend/venv/bin/activate"
  )
  for act in "${candidates[@]}"; do
    if [[ -f "$act" ]]; then
      # shellcheck disable=SC1090
      source "$act"
      return 0
    fi
  done
  return 1
}

activate_venv || true

# Ensure PYTHONPATH includes backend
if [[ -z "${PYTHONPATH:-}" ]]; then
  export PYTHONPATH="$ROOT_DIR/backend"
elif [[ ":$PYTHONPATH:" != *":$ROOT_DIR/backend:"* ]]; then
  export PYTHONPATH="$ROOT_DIR/backend:$PYTHONPATH"
fi

if [[ "$#" -lt 1 ]]; then
  usage
  exit 2
fi

service="$1"; shift || true
module=""

case "$service" in
  auth)
    module="auth_service.src.cli.user_commands"
    ;;
  ai)
    module="ai_service.src.cli.app"
    ;;
  stream|streaming)
    module="streaming_service.src.cli.app"
    ;;
  -h|--help|help)
    usage; exit 0 ;;
  *)
    echo "[error] Unknown service: $service" >&2
    usage; exit 2 ;;
esac

exec python -m "$module" "$@"


