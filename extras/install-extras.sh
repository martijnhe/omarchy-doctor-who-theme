#!/bin/bash

# Install the Doctor Who extras that live outside Omarchy's theme system.
#
#   bash install-extras.sh              fastfetch and Spicetify
#   bash install-extras.sh fastfetch    only fastfetch
#   bash install-extras.sh spicetify    only Spicetify
#
# Your current fastfetch config is kept as config.jsonc.bak (or a dated copy
# if that already exists), so you can always go back.

set -euo pipefail

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}"

install_fastfetch() {
  local dir="$CONFIG/fastfetch" backup
  mkdir -p "$dir"

  if [[ -f $dir/config.jsonc ]] && ! cmp -s "$dir/config.jsonc" "$HERE/fastfetch/config.jsonc"; then
    backup="$dir/config.jsonc.bak"
    [[ -e $backup ]] && backup="$dir/config.jsonc.bak.$(date +%Y%m%d-%H%M%S)"
    cp "$dir/config.jsonc" "$backup"
    echo "Saved your old fastfetch config as $backup"
  fi

  cp "$HERE/fastfetch/config.jsonc" "$HERE/fastfetch/tardis.txt" "$dir/"
  echo "Fastfetch: installed. Run fastfetch to see it."
}

install_spicetify() {
  local dir="$CONFIG/spicetify/Themes/tardis"
  mkdir -p "$dir"
  cp "$HERE/spicetify/tardis/color.ini" "$HERE/spicetify/tardis/user.css" "$dir/"
  echo "Spicetify: theme copied to $dir"

  if ! command -v spicetify >/dev/null; then
    echo "Spicetify isn't installed. Install it, then run this again to switch Spotify over."
    return
  fi

  spicetify config current_theme tardis color_scheme tardis >/dev/null
  if spicetify apply || spicetify backup apply; then
    echo "Spicetify: Spotify is now using the TARDIS theme."
  else
    cat <<'EOF'
Spicetify couldn't patch Spotify. If Spotify lives in /opt/spotify, give
Spicetify write access and try again:

  sudo chmod a+wr /opt/spotify /opt/spotify/Apps -R
  spicetify config spotify_path /opt/spotify
  spicetify backup apply
EOF
    return 1
  fi
}

case "${1:-all}" in
  fastfetch) install_fastfetch ;;
  spicetify) install_spicetify ;;
  all) install_fastfetch; install_spicetify ;;
  *) echo "Usage: bash install-extras.sh [fastfetch|spicetify|all]" >&2; exit 1 ;;
esac
