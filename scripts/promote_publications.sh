#!/bin/sh
# Copy reviewed bundles from build/pub-staging/ into content/publications/.
# Separate from generation so nothing writes to content/ unreviewed.
#
# NOTE: uses `cp -R "$src" "$dest/"` with NO trailing slash on $src. With a
# trailing slash, macOS cp copies the directory's *contents* rather than the
# directory, which silently collapses every bundle into one and lets the
# index.md files overwrite each other.
set -e
[ -d build/pub-staging ] || { echo "nothing staged"; exit 1; }
mkdir -p content/publication
n=0
for d in build/pub-staging/*/; do
  src="${d%/}"                       # strip the trailing slash
  cp -R "$src" content/publications/
  n=$((n+1))
done
echo "promoted $n bundles"
