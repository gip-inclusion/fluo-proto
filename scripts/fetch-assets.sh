#!/bin/bash
# Refresh static assets from a local les-emplois checkout.
# Usage: ./scripts/fetch-assets.sh /path/to/les-emplois
set -euo pipefail

LES_EMPLOIS="${1:?Usage: $0 /path/to/les-emplois}"
STATIC="$(dirname "$0")/../_template/web/static"

# theme-inclusion (CSS, fonts, images, JS)
rm -rf "$STATIC/vendor/theme-inclusion"
cp -r "$LES_EMPLOIS/itou/static/vendor/theme-inclusion" "$STATIC/vendor/theme-inclusion"

# Trim remixicon bloat — keep only woff/woff2
cd "$STATIC/vendor/theme-inclusion/fonts/remixicon"
rm -f remixicon.glyph.json remixicon.svg remixicon.symbol.svg \
      remixicon.ttf remixicon.eot remixicon.scss
cd -

# Remove unused images
rm -rf "$STATIC/vendor/theme-inclusion/images/home" \
       "$STATIC/vendor/theme-inclusion/images/nexus" \
       "$STATIC/vendor/theme-inclusion/images/remixicon.symbol.svg" \
       "$STATIC/vendor/theme-inclusion/files"

# Bootstrap JS + Popper
mkdir -p "$STATIC/vendor/bootstrap"
cp "$LES_EMPLOIS/node_modules/bootstrap/dist/js/bootstrap.min.js" "$STATIC/vendor/bootstrap/"
cp "$LES_EMPLOIS/node_modules/bootstrap/dist/js/bootstrap.min.js.map" "$STATIC/vendor/bootstrap/"
cp "$LES_EMPLOIS/node_modules/@popperjs/core/dist/umd/popper.min.js" "$STATIC/vendor/bootstrap/"
cp "$LES_EMPLOIS/node_modules/@popperjs/core/dist/umd/popper.min.js.map" "$STATIC/vendor/bootstrap/"

# jQuery
mkdir -p "$STATIC/vendor/jquery"
cp "$LES_EMPLOIS/itou/static/vendor/jquery/jquery.min.js" "$STATIC/vendor/jquery/"

# itou.css
mkdir -p "$STATIC/css"
cp "$LES_EMPLOIS/itou/static/css/itou.css" "$STATIC/css/"

echo "Assets refreshed. Total size:"
du -sh "$STATIC"
