# Open Terminal (`saud-open-terminal`) for umbrelOS

[Open Terminal](https://github.com/open-webui/open-terminal) (`v0.16.6`) is Open WebUI's sandboxed computer environment ("a computer you can curl") that gives AI agents a dedicated Linux container to run shell commands, manage files, execute Python/Node.js code, run Jupyter notebooks, and use a headless browser or virtual desktop over REST and WebSocket APIs.

## Package Summary

| Setting | Value |
|---|---|
| **App ID** | `saud-open-terminal` |
| **Version** | `0.16.6` (pinned to `ghcr.io/open-webui/open-terminal:0.16.6@sha256:9d2ce201c46da381449dab90e0c3b0fe83bd56263ea3c31631820736971a2089`) |
| **Umbrel UI Port** | `5450` (opens `/docs` interactive Swagger UI behind Umbrel login) |
| **Internal Container URL** | `http://saud-open-terminal_server_1:8000` |
| **API Key** | `${APP_PASSWORD}` (shown in Umbrel under **Show default credentials**) |
| **Persistent Workspace** | `${APP_DATA_DIR}/data/workspace` → `/home/user` |

## Adding to Your Community Store

1. Unzip `saud-open-terminal.zip` and copy the `saud-open-terminal` folder into the root of your store repository (`saud-umbrel-store/`), right next to `umbrel-app-store.yml` and your other `saud-*` folders.
2. Commit and push to `main`:
   ```bash
   git add saud-open-terminal
   git commit -m "Add Open Terminal 0.16.6"
   git push
   ```
3. In umbrelOS, open **App Store → Community App Stores**, refresh your store (or wait up to 5 minutes for auto-sync), and install **Open Terminal**.
   - Note: The full image is ~4 GB because it bundles Python data-science libraries, Node.js 22, LibreOffice, LaTeX, ffmpeg, Chromium, and XFCE desktop tools, so the initial download takes several minutes.

## Connecting to Open WebUI on Umbrel

1. On your Umbrel dashboard, right-click the **Open Terminal** icon (or click `⋯` on its app page) and select **Show default credentials** to copy the generated **Password**.
2. Open **Open WebUI** on your Umbrel.
3. Go to **Settings → Admin → Integrations** (under the *Tools* group, not *Personal*).
4. Scroll to the dedicated **Open Terminal** section (do **not** add it under External Tools / Tool Servers).
5. Click **`+`** and enter:
   - **URL:** `http://saud-open-terminal_server_1:8000`
   - **API Key:** *(paste the Umbrel app password)*
   - **Auth Type:** `Bearer`
6. Click **Save** and ensure the toggle switch is **On**.
7. In any chat, click the **Terminal (cloud ☁)** icon in the message bar and select **Open Terminal** under *System*.

## Optional Customizations

- **Lightweight (`slim`) variant (~430 MB):** If you only want shell/git/curl/jq without Python data science, Node.js, LibreOffice, or desktop/browser tools, change the image in `docker-compose.yml` to `ghcr.io/open-webui/open-terminal:0.16.6-slim`.
- **Extra Startup Packages:** Uncomment `OPEN_TERMINAL_PACKAGES`, `OPEN_TERMINAL_PIP_PACKAGES`, or `OPEN_TERMINAL_NPM_PACKAGES` in `docker-compose.yml` to auto-install additional `apt`, `pip`, or `npm` packages when the container starts.
- **Direct LAN API Access (outside Docker):** By default, port `5450` is protected by Umbrel's authentication proxy, while containers on `umbrel_main_network` (like Open WebUI) reach port `8000` directly using the Bearer API key. If you also need external clients on your LAN to call the API via port `5450` using only the Bearer key, add `PROXY_AUTH_WHITELIST: "/*"` under `app_proxy.environment` in `docker-compose.yml`.

## Quick Verification over SSH

```bash
# Check container health and logs
sudo docker ps --filter name=saud-open-terminal
sudo docker logs --tail 50 saud-open-terminal_server_1

# Test health endpoint from inside the container
sudo docker exec saud-open-terminal_server_1 curl -s http://localhost:8000/health
```
