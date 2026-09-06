#!/bin/sh
# Start the Hugo dev server for this site.
#
# Wrapped in a script rather than inlined into .claude/launch.json or a VS Code
# task because Hugo needs BOTH binaries on PATH and GUI-launched processes do not
# inherit a login shell's PATH:
#   * hugo -- must be the PINNED 0.152.1 extended build in ~/.local/bin, not
#     Homebrew's newer one (which cannot run this theme: it requires the
#     tailwindcss binary be a Node.js script, but pnpm installs a shell shim)
#   * go   -- Hugo resolves the theme as a Go module
set -e
PATH="$HOME/.local/bin:/opt/homebrew/bin:$PATH"
export PATH

for bin in hugo go; do
  command -v "$bin" >/dev/null 2>&1 || { echo "ERROR: '$bin' not on PATH ($PATH)" >&2; exit 1; }
done

case "$(hugo version)" in
  *0.152.1*) : ;;
  *) echo "WARNING: expected Hugo 0.152.1, got: $(hugo version)" >&2 ;;
esac

cd "$(dirname "$0")/.."
# --renderToMemory keeps the server off the on-disk public/ directory. Without
# it, running `hugo --cleanDestinationDir` in another shell deletes files out
# from under the running server and its incremental rebuilds start failing with
# "renderDeferred: open .../public/...: no such file or directory".
exec hugo server --disableFastRender --renderToMemory --bind 127.0.0.1 --port "${PORT:-1313}" "$@"
