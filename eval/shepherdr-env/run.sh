#!/bin/sh
# Isolated Shepherdr environment. Usage:
#   run.sh build TAG        build image shepherdr-env:TAG (TAG = v3.1.26 | v3.2.19)
#   run.sh shell TAG [CMD]  run CMD (default bash) in a fresh, throwaway container
# No host path is mounted except the read-only evidence output dir given by OUT=DIR.
set -eu
cmd=$1; tag=$2; shift 2
here=$(cd "$(dirname "$0")" && pwd)
case "$cmd" in
  build)
    ctx=$(mktemp -d); trap 'rm -rf "$ctx"' EXIT
    cp "$here/Dockerfile" "$ctx/"; cp -r "$here/stubs" "$ctx/"; chmod +x "$ctx/stubs/"*
    cp "$(readlink -f "$(command -v herdr-core)")" "$ctx/hc"
    docker build -q --build-arg TAG="$tag" -t "shepherdr-env:$tag" "$ctx" ;;
  shell)
    mnt=""; [ -n "${OUT:-}" ] && mnt="-v $OUT:/out"
    docker run --rm -i --network bridge $mnt "shepherdr-env:$tag" "${@:-bash}" ;;
  *) echo "usage: run.sh build|shell TAG" >&2; exit 2 ;;
esac
