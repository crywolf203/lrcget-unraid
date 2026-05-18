FROM jlesage/baseimage-gui:ubuntu-24.04-v4.10.7

ARG LRCGET_VERSION=2.1.0
ARG IMAGE_VERSION=1.0.0

LABEL org.opencontainers.image.source="https://github.com/crywolf203/lrcget-unraid"
LABEL org.opencontainers.image.description="Unofficial browser-based Docker container for LRCGET on Unraid."
LABEL org.opencontainers.image.licenses="MIT"

ENV DISPLAY_WIDTH=1920 \
    DISPLAY_HEIGHT=1080 \
    KEEP_APP_RUNNING=1 \
    WEB_AUDIO=1 \
    GDK_BACKEND=x11 \
    LIBGL_ALWAYS_SOFTWARE=1 \
    WEBKIT_DISABLE_DMABUF_RENDERER=1 \
    WEBKIT_DISABLE_COMPOSITING_MODE=1 \
    NO_AT_BRIDGE=1

RUN set-cont-env APP_NAME "LRCGET" && \
    set-cont-env APP_VERSION "${LRCGET_VERSION}" && \
    set-cont-env DOCKER_IMAGE_VERSION "${IMAGE_VERSION}"
    

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
      ca-certificates \
      wget \
      dbus-x11 \
      xdg-utils \
      libgtk-3-0 \
      libwebkit2gtk-4.1-0 \
      libayatana-appindicator3-1 \
      libgstreamer1.0-0 \
      libgstreamer-plugins-base1.0-0 \
      gstreamer1.0-plugins-good \
      gstreamer1.0-plugins-bad \
      gstreamer1.0-plugins-ugly \
      gstreamer1.0-libav \
      gstreamer1.0-alsa \
      pulseaudio \
      libpulse0 \
      libgl1 \
      libegl1 \
      mesa-utils \
      openbox; \
    wget -q --show-progress \
      "https://github.com/tranxuanthang/lrcget/releases/download/${LRCGET_VERSION}/LRCGET_${LRCGET_VERSION}_amd64.deb" \
      -O /tmp/lrcget.deb; \
    apt-get install -y /tmp/lrcget.deb; \
    rm -f /tmp/lrcget.deb; \
    if command -v lrcget >/dev/null 2>&1; then \
      ln -sf "$(command -v lrcget)" /usr/local/bin/lrcget; \
    elif command -v LRCGET >/dev/null 2>&1; then \
      ln -sf "$(command -v LRCGET)" /usr/local/bin/lrcget; \
    else \
      find /usr -iname '*lrcget*' -type f -perm -111 -print; \
      exit 1; \
    fi; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY startapp.sh /startapp.sh
RUN chmod +x /startapp.sh

VOLUME ["/config", "/music"]

EXPOSE 5800
