<p align="center">
  <img src="https://raw.githubusercontent.com/crywolf203/unraid-templates/main/lrcget-icon.png" alt="LRCGET for Unraid icon" width="180">
</p>

<h1 align="center">LRCGET for Unraid</h1>

<p align="center">
  <strong>Unofficial browser-based Docker container for running LRCGET on Unraid.</strong>
</p>

<p align="center">
  <a href="https://github.com/tranxuanthang/lrcget">
    <img alt="Upstream LRCGET" src="https://img.shields.io/badge/Upstream-LRCGET-orange?style=for-the-badge">
  </a>
  <a href="https://github.com/crywolf203/lrcget-unraid/pkgs/container/lrcget-unraid">
    <img alt="GHCR Package" src="https://img.shields.io/badge/Image-GHCR-24292f?style=for-the-badge&logo=github">
  </a>
  <a href="https://github.com/crywolf203/lrcget-unraid/blob/main/LICENSE">
    <img alt="License" src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge">
  </a>
</p>

---

## Overview

**LRCGET for Unraid** packages the upstream [LRCGET](https://github.com/tranxuanthang/lrcget) desktop application into a Docker container that can be opened from a web browser on Unraid.

LRCGET itself is developed by [`tranxuanthang`](https://github.com/tranxuanthang/lrcget). This repository is **not** the upstream LRCGET project and is **not** an official LRCGET release channel. It is an unofficial Unraid-friendly container wrapper that installs the upstream Linux build and exposes it through a browser-based desktop session.

```text
Upstream LRCGET app
        │
        │ Linux .deb release
        ▼
lrcget-unraid Docker image
        │
        │ Browser GUI on port 5800
        ▼
Unraid Community Applications
```

---

## What is LRCGET?

[LRCGET](https://github.com/tranxuanthang/lrcget) is a utility for mass-downloading synced `.lrc` lyrics for offline music libraries. It can scan a music directory, match tracks, and download synced lyrics using LRCLIB.

This container simply makes that desktop app easier to run on Unraid.

---

## Docker image

```text
ghcr.io/crywolf203/lrcget-unraid:latest
```

Versioned tags may also be available:

```text
ghcr.io/crywolf203/lrcget-unraid:2.1.0
```

---

## Why this container exists

LRCGET is a desktop/Tauri application. Unraid servers normally do not run desktop applications directly. This container uses a browser-accessible GUI base image so LRCGET can run on your server and be controlled through a web browser.

Open the app at:

```text
http://YOUR-UNRAID-IP:5800
```

---

## Features

- Browser-based LRCGET desktop interface
- Designed for Unraid Community Applications
- Uses the upstream LRCGET Linux `.deb` build
- Persistent app data through `/config`
- Music library mapping through `/music`
- Web UI on port `5800`
- Software-rendering variables included to help avoid black screen issues
- Works well for large music libraries
- Automated GitHub Actions builds for new upstream LRCGET releases

---

## Recommended Unraid install

Install from **Unraid Community Applications** when available.

Search for:

```text
LRCGET
```

Manual repository value:

```text
ghcr.io/crywolf203/lrcget-unraid:latest
```

Recommended WebUI:

```text
http://[IP]:[PORT:5800]
```

Recommended extra parameters:

```text
--shm-size=8g --cap-add=SYS_NICE --tmpfs /tmp:rw,size=8g
```

For smaller systems, reduce `8g` to `2g` or `4g`.

---

## Required paths

| Container Path | Example Host Path | Access | Purpose |
|---|---|---|---|
| `/config` | `/mnt/user/appdata/lrcget` | Read/Write | Stores LRCGET settings, database, cache, and app state |
| `/music` | `/mnt/user/media/music` | Read/Write recommended | Your music library inside the container |

### `/config`

This should point to persistent appdata.

Recommended:

```text
/mnt/user/appdata/lrcget
```

Cache path example:

```text
/mnt/cache/appdata/lrcget
```

### `/music`

This should point to your actual music library.

Example:

```text
/mnt/user/media/music
```

Inside LRCGET, select:

```text
/music
```

as the library folder.

Use Read/Write access if you want LRCGET to export `.lrc` sidecar files beside your music.

---

## Ports

| Container Port | Host Port | Required | Purpose |
|---:|---:|:---:|---|
| `5800` | `5800` | Yes | Browser-based LRCGET GUI |
| `5900` | Optional | No | Direct VNC access, usually not needed |

Most Unraid users only need:

```text
5800:5800
```

---

## Environment variables

### User and permission variables

| Variable | Recommended | Description |
|---|---:|---|
| `USER_ID` | `99` | Runs the app as the Unraid `nobody` user. |
| `GROUP_ID` | `100` | Runs the app as the Unraid `users` group. |
| `UMASK` | `000` | Helps avoid permission issues when writing `.lrc` files to shared media folders. |
| `TZ` | `America/New_York` | Sets the container timezone. Change this to your timezone. |

### GUI variables

| Variable | Recommended | Description |
|---|---:|---|
| `KEEP_APP_RUNNING` | `1` | Restarts the GUI app if it exits. |
| `DISPLAY_WIDTH` | `1920` | Virtual desktop width. |
| `DISPLAY_HEIGHT` | `1080` | Virtual desktop height. |
| `ENABLE_CJK_FONT` | `1` | Enables better Chinese/Japanese/Korean character support. |
| `APP_NICENESS` | `-10` | Raises app priority. Requires `--cap-add=SYS_NICE`. |

### Rendering compatibility variables

These are included because LRCGET is a WebKit/Tauri desktop app running inside a containerized GUI session.

| Variable | Recommended | Description |
|---|---:|---|
| `GDK_BACKEND` | `x11` | Forces GTK to use X11 inside the container. |
| `LIBGL_ALWAYS_SOFTWARE` | `1` | Uses software rendering instead of relying on host GPU acceleration. |
| `WEBKIT_DISABLE_DMABUF_RENDERER` | `1` | Helps avoid WebKit blank/black screen issues in containers. |
| `WEBKIT_DISABLE_COMPOSITING_MODE` | `1` | Disables WebKit compositing mode for better compatibility. |
| `NO_AT_BRIDGE` | `1` | Disables accessibility bridge warnings/noise in GTK environments. |

---

## Extra parameters explained

Recommended:

```text
--shm-size=8g --cap-add=SYS_NICE --tmpfs /tmp:rw,size=8g
```

| Parameter | Description |
|---|---|
| `--shm-size=8g` | Gives the browser-based GUI more shared memory. |
| `--cap-add=SYS_NICE` | Required when using negative `APP_NICENESS` values. |
| `--tmpfs /tmp:rw,size=8g` | Places temporary files in RAM-backed storage for better responsiveness. |

---

## Basic usage

1. Open the Web UI:

   ```text
   http://YOUR-UNRAID-IP:5800
   ```

2. In LRCGET, choose your mapped music folder:

   ```text
   /music
   ```

3. Scan your library.

4. Download lyrics.

5. Export lyrics when you want `.lrc` files written beside your tracks.

LRCGET 2.x stores lyrics internally first. Use the export feature when you want sidecar `.lrc` files created in your music folders.

---

## Docker Compose example

```yaml
services:
  lrcget:
    image: ghcr.io/crywolf203/lrcget-unraid:latest
    container_name: lrcget
    restart: unless-stopped
    ports:
      - "5800:5800"
    environment:
      USER_ID: "99"
      GROUP_ID: "100"
      UMASK: "000"
      TZ: "America/New_York"
      KEEP_APP_RUNNING: "1"
      DISPLAY_WIDTH: "1920"
      DISPLAY_HEIGHT: "1080"
      ENABLE_CJK_FONT: "1"
      APP_NICENESS: "-10"
      GDK_BACKEND: "x11"
      LIBGL_ALWAYS_SOFTWARE: "1"
      WEBKIT_DISABLE_DMABUF_RENDERER: "1"
      WEBKIT_DISABLE_COMPOSITING_MODE: "1"
      NO_AT_BRIDGE: "1"
    volumes:
      - /mnt/user/appdata/lrcget:/config
      - /mnt/user/media/music:/music
    shm_size: "8gb"
    cap_add:
      - SYS_NICE
    tmpfs:
      - /tmp:rw,size=8g
```

---

## Docker CLI example

```bash
docker run -d \
  --name lrcget \
  --restart unless-stopped \
  -p 5800:5800 \
  -e USER_ID=99 \
  -e GROUP_ID=100 \
  -e UMASK=000 \
  -e TZ=America/New_York \
  -e KEEP_APP_RUNNING=1 \
  -e DISPLAY_WIDTH=1920 \
  -e DISPLAY_HEIGHT=1080 \
  -e ENABLE_CJK_FONT=1 \
  -e APP_NICENESS=-10 \
  -e GDK_BACKEND=x11 \
  -e LIBGL_ALWAYS_SOFTWARE=1 \
  -e WEBKIT_DISABLE_DMABUF_RENDERER=1 \
  -e WEBKIT_DISABLE_COMPOSITING_MODE=1 \
  -e NO_AT_BRIDGE=1 \
  -v /mnt/user/appdata/lrcget:/config \
  -v /mnt/user/media/music:/music \
  --shm-size=8g \
  --cap-add=SYS_NICE \
  --tmpfs /tmp:rw,size=8g \
  ghcr.io/crywolf203/lrcget-unraid:latest
```

---

## Updating

The image is built through GitHub Actions.

The workflow checks the latest upstream LRCGET release and builds the Docker image using that version. Unraid users using the `latest` tag should receive updates through the normal Docker update flow when a new image is published.

---

## Troubleshooting

### The Web UI opens but the screen is black

Make sure these variables are present:

```text
GDK_BACKEND=x11
LIBGL_ALWAYS_SOFTWARE=1
WEBKIT_DISABLE_DMABUF_RENDERER=1
WEBKIT_DISABLE_COMPOSITING_MODE=1
NO_AT_BRIDGE=1
```

This image uses the upstream Linux `.deb` package rather than the AppImage because the `.deb` build has worked better in this browser-based Unraid container setup.

### The container fails when using `APP_NICENESS=-10`

Make sure this is included in Extra Parameters:

```text
--cap-add=SYS_NICE
```

Or set:

```text
APP_NICENESS=0
```

### Port `5900` is already in use

Port `5900` is optional. Remove it unless you specifically want direct VNC access.

The browser GUI uses:

```text
5800
```

### Lyrics download but no `.lrc` files appear

Use LRCGET's export feature. LRCGET 2.x stores lyrics internally first and exports sidecar `.lrc` files when requested.

### Permission issues writing `.lrc` files

Check:

```text
USER_ID=99
GROUP_ID=100
UMASK=000
```

Also confirm that your `/music` mapping is Read/Write.

---

## Related projects

| Project | Link |
|---|---|
| Upstream LRCGET | https://github.com/tranxuanthang/lrcget |
| LRCLIB | https://lrclib.net |
| This Docker image | https://github.com/crywolf203/lrcget-unraid |
| GHCR package | https://github.com/crywolf203/lrcget-unraid/pkgs/container/lrcget-unraid |
| Unraid template repo | https://github.com/crywolf203/unraid-templates |
| GUI base image | https://github.com/jlesage/docker-baseimage-gui |

---

## Credits

All credit for the LRCGET application goes to the upstream LRCGET project and its developer.

This repository only provides an Unraid-friendly Docker image and template experience around the upstream app.

---

## Disclaimer

This is an **unofficial** Docker container for LRCGET.

For issues with this Docker image, Unraid template, paths, permissions, or the browser GUI container, open an issue here:

```text
https://github.com/crywolf203/lrcget-unraid/issues
```

For issues with the LRCGET application itself, use the upstream repository:

```text
https://github.com/tranxuanthang/lrcget
```

---

## License

This container repository is licensed under the MIT License.

LRCGET itself is licensed and maintained by the upstream LRCGET project. See the upstream repository for its license and source code.
