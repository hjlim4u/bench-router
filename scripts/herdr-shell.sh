#!/bin/sh
# Restore the app/core environment in ordinary TUI shell panes.
set -eu
export XDG_CONFIG_HOME="$BENCH_ROUTER_CORE_CONFIG_HOME"
export XDG_STATE_HOME="$BENCH_ROUTER_CORE_STATE_HOME"
export SHELL="$BENCH_ROUTER_LOGIN_SHELL"
exec "$SHELL" "$@"
