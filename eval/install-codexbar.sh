#!/bin/sh
# Official release, pinned with checksum validation. No Swift/Homebrew/desktop required.
set -eu
version=0.84.0
case "$(uname -sm)" in
    'Linux x86_64') platform=linux-x86_64 ;;
    'Linux aarch64') platform=linux-aarch64 ;;
    *) echo 'Install CodexBar using the official release for your platform.' >&2; exit 1 ;;
esac
destination="${XDG_DATA_HOME:-$HOME/.local/share}/bench-router/codexbar/$version"
link="$HOME/.local/bin/codexbar"
if { [ -e "$link" ] || [ -L "$link" ]; } && [ "$(readlink "$link" || true)" != "$destination/codexbar" ]; then
    echo "Preserving existing $link; use BENCH_ROUTER_CODEXBAR to select another installation." >&2
    exit 1
fi
if [ ! -x "$destination/CodexBarCLI" ]; then
    temp=$(mktemp -d)
    trap 'rm -rf "$temp"' EXIT HUP INT TERM
    archive="CodexBarCLI-v$version-$platform.tar.gz"
    url="https://github.com/steipete/CodexBar/releases/download/v$version/$archive"
    curl -fsSL --retry 2 "$url" -o "$temp/$archive"
    curl -fsSL --retry 2 "$url.sha256" -o "$temp/$archive.sha256"
    (cd "$temp" && sha256sum -c "$archive.sha256")
    mkdir "$temp/install"
    tar -xzf "$temp/$archive" --no-same-owner -C "$temp/install"
    "$temp/install/CodexBarCLI" --version
    mkdir -p "$(dirname "$destination")"
    mv "$temp/install" "$destination"
fi
mkdir -p "$(dirname "$link")"
ln -sfn "$destination/codexbar" "$link"
"$link" --version
