#!/usr/bin/env sh
set -e

export HOME=/config
export XDG_CONFIG_HOME=/config/xdg/config
export XDG_DATA_HOME=/config/xdg/data
export XDG_CACHE_HOME=/config/xdg/cache
export XDG_STATE_HOME=/config/xdg/state

export GDK_BACKEND=x11
export LIBGL_ALWAYS_SOFTWARE=1
export WEBKIT_DISABLE_DMABUF_RENDERER=1
export WEBKIT_DISABLE_COMPOSITING_MODE=1
export NO_AT_BRIDGE=1

mkdir -p "$XDG_CONFIG_HOME" "$XDG_DATA_HOME" "$XDG_CACHE_HOME" "$XDG_STATE_HOME"

exec dbus-launch --exit-with-session /usr/local/bin/lrcget
