#!/bin/sh
# App owns coding tasks; the isolated TUI is a shell and hc viewer.
set -eu
project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
case "${1:-}" in
  app)
    shift
    unset HC_SESSION
    exec herdr-app "$@"
    ;;
  tui)
    shift
    export BENCH_ROUTER_CORE_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
    export BENCH_ROUTER_CORE_STATE_HOME="${XDG_STATE_HOME:-$HOME/.local/state}"
    export BENCH_ROUTER_LOGIN_SHELL="${SHELL:-/bin/sh}"
    export SHELL="$project_dir/scripts/herdr-shell.sh"
    export XDG_CONFIG_HOME="$project_dir/.bench-router/tui/config"
    export XDG_STATE_HOME="$project_dir/.bench-router/tui/state"
    export HERDR_CONFIG_PATH="$project_dir/examples/herdr-tui.toml"
    unset HERDR_SOCKET_PATH HERDR_SESSION HERDR_ENV HERDR_PANE_ID HC_SESSION HC_TERMINAL_ID
    mkdir -p "$XDG_CONFIG_HOME/herdr" "$XDG_STATE_HOME/herdr"
    exec herdr --session app-companion "$@"
    ;;
  *)
    echo "Usage: $0 app|tui [arguments...]" >&2
    exit 2
    ;;
esac
