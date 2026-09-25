#!/usr/bin/env python3
"""
audit_umbrel_store.py - Pre-flight audit for umbrelOS community app stores.

Checks a local checkout of a community app store repository against the
behaviour of umbreld (umbrelOS 2.0.0 source, getumbrel/umbrel @ 11e7f5b) so
that problems are caught BEFORE you add the store URL to your Umbrel and
click Install.

Three audit areas:
  1. Installation reliability  - store layout, manifest, docker-compose
  2. Icon / gallery metadata    - icon URL resolution, reachability, caching
  3. Repository sync behaviour  - what umbreld will actually clone and when

Usage:
  python3 audit_umbrel_store.py /path/to/store-repo
  python3 audit_umbrel_store.py /path/to/store-repo --online
  python3 audit_umbrel_store.py /path/to/store-repo --online \
      --remote https://github.com/you/your-store --format md > report.md

Exit code: 1 if any ERROR, else 0.
Requires: Python 3.9+, PyYAML (pip install pyyaml). Optional: git, docker.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import copy, os
import re
import shutil
import stat
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is required: pip install pyyaml")

HERE = Path(__file__).resolve().parent

# ---- Constants mirrored from umbreld 2.0.0 -------------------------------
STORE_ID_RE = re.compile(r"^[a-z-]+$")            # umbrel-app-store.yml comment
APP_ID_RE = re.compile(r"^[a-zA-Z0-9-_]+$")       # App constructor / getAppTemplateFilePath
OFFICIAL_GALLERY = "https://getumbrel.github.io/umbrel-apps-gallery"
RESERVED_PORTS = {80: "dashboard HTTP", 443: "dashboard HTTPS", 2000: "app auth"}
MACHINES_PORT_RANGE = (40000, 49999)              # machines.ts MACHINES_PORT_MIN/MAX
# app-script: only these are re-copied from the repo on an app UPDATE
UPDATE_WHITELIST = ["docker-compose.yml", "*.template", "exports.sh", "torrc", "hooks", "umbrel-app.yml"]
VALID_HOOKS = {"pre-install", "post-install", "pre-start", "post-start",
               "pre-stop", "post-stop", "pre-update", "post-update"}
# Fields umbreld/UI read directly (AppManifestSchema non-optional fields)
REQUIRED_FIELDS = ["manifestVersion", "id", "name", "tagline", "category", "version",
                   "port", "description", "website", "support", "gallery"]
RECOMMENDED_FIELDS = ["icon", "developer", "repo", "releaseNotes", "dependencies", "path"]
# Env vars exported by app-script before `docker compose` runs
UMBREL_ENV = {"APP_DATA_DIR", "APP_DATA_ROOT", "APP_ID", "APP_MANIFEST_FILE", "APP_VERSION",
              "APP_PROXY_PORT", "APP_DOMAIN", "APP_HIDDEN_SERVICE", "APP_SEED", "APP_PASSWORD",
              "DEVICE_HOSTNAME", "DEVICE_DOMAIN_NAME", "NETWORK_IP", "GATEWAY_IP", "UMBREL_ROOT",
              "TOR_DATA_DIR", "TOR_ENTRYPOINT_SCRIPT", "TOR_HS_APP_DIR", "TOR_HS_PORTS",
              "TOR_PROXY_IP", "TOR_PROXY_PORT"}
MUTABLE_ICON_HOST_PATTERNS = [
    (re.compile(r"raw\.githubusercontent\.com/[^/]+/[^/]+/(main|master|HEAD)/"), "branch ref on raw.githubusercontent.com (cache max-age=300)"),
    (re.compile(r"cdn\.jsdelivr\.net/gh/[^@/]+/[^@/]+(@(main|master|latest))?/"), "jsDelivr branch/latest ref (edge-cached up to 7 days)"),
    (re.compile(r"\.github\.io/"), "GitHub Pages (cache max-age=600, content changes in place)"),
]
DEAD_HOSTS = {"svgur.com": "svgur.com no longer serves images (template icon returns 404)"}


@dataclass
class Issue:
    severity: str   # ERROR | WARNING | INFO
    area: str       # install | icon | sync
    rule: str
    where: str
    message: str


@dataclass
class Report:
    issues: list[Issue] = field(default_factory=list)
    apps_seen: int = 0
    apps_visible: int = 0

    def add(self, sev, area, rule, where, msg):
        self.issues.append(Issue(sev, area, rule, where, msg))


# ---- helpers ---------------------------------------------------------------
def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def raw_scalar(text: str, key: str):
    """Return the raw (unparsed) scalar for a top-level key, to detect YAML number coercion."""
    m = re.search(rf"^{re.escape(key)}:\s*(.+?)\s*(#.*)?$", text, re.M)
    return m.group(1) if m else None


def is_abs_url(v: str) -> bool:
    try:
        p = urllib.parse.urlparse(v)
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False


def semver_norm(v) -> str | None:
    if isinstance(v, (int, float)):
        v = str(v)
    if not isinstance(v, str):
        return None
    m = re.match(r"^v?(\d+)(?:\.(\d+))?(?:\.(\d+))?", v.strip())
    if not m:
        return None
    return ".".join(x or "0" for x in m.groups())


def ver_tuple(v: str):
    return tuple(int(x) for x in v.split("."))


def http_probe(url: str, timeout=15):
    """HEAD then GET fallback. Returns (status, content_type, cache_control, length, error)."""
    headers = {"User-Agent": "umbrel-store-audit/1.0"}
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return (r.status, r.headers.get("Content-Type", ""), r.headers.get("Cache-Control", ""),
                        r.headers.get("Content-Length"), None)
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (403, 405):
                continue
            return (e.code, e.headers.get("Content-Type", "") if e.headers else "", "", None, None)
        except Exception as e:  # DNS, TLS, timeout
            if method == "HEAD":
                continue
            return (None, "", "", None, str(e))
    return (None, "", "", None, "unreachable")


def env_refs(obj):
    """Yield ${VAR} / $VAR references inside a compose structure."""
    if isinstance(obj, str):
        for m in re.finditer(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?:[:?-][^}]*)?\}|\$([A-Za-z_][A-Za-z0-9_]*)", obj.replace("$$", "")):
            yield m.group(1) or m.group(2)
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from env_refs(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from env_refs(v)


def exported_vars(exports: Path) -> set[str]:
    if not exports.exists():
        return set()
    return set(re.findall(r"^\s*export\s+([A-Za-z_][A-Za-z0-9_]*)=", exports.read_text(errors="ignore"), re.M))


# ---- store-level checks ------------------------------------------------------
def audit_store(root: Path, rep: Report, official_ports: dict, os_version: str, online: bool, remote: str | None):
    meta_path = root / "umbrel-app-store.yml"
    store_id = None
    if not meta_path.exists():
        rep.add("ERROR", "install", "store.meta.missing", "umbrel-app-store.yml",
                "Missing at repo root. readRegistry() throws, so the ENTIRE store is dropped from the App Store UI.")
    else:
        try:
            meta = load_yaml(meta_path) or {}
            store_id = meta.get("id")
            if not isinstance(store_id, str) or not STORE_ID_RE.match(store_id):
                rep.add("ERROR", "install", "store.meta.id", "umbrel-app-store.yml",
                        f"Store id {store_id!r} must be lowercase letters and dashes only (a-z, -).")
            if not meta.get("name"):
                rep.add("ERROR", "install", "store.meta.name", "umbrel-app-store.yml",
                        "Missing `name`; UI shows '<name> App Store'.")
        except Exception as e:
            rep.add("ERROR", "install", "store.meta.parse", "umbrel-app-store.yml", f"YAML parse failed: {e}")

    # umbreld only globs `${repo}/*/umbrel-app.yml` (one level deep)
    top = sorted(p.parent for p in root.glob("*/umbrel-app.yml"))
    nested = sorted(p for p in root.glob("*/*/**/umbrel-app.yml") if p.parent.parent != root)
    if nested:
        sample = ", ".join(str(p.relative_to(root)) for p in nested[:3])
        rep.add("ERROR", "install", "store.layout.nested", str(nested[0].parent.parent.relative_to(root)) + "/",
                f"{len(nested)} manifest(s) are nested deeper than <repo>/<app-id>/umbrel-app.yml (e.g. {sample}). "
                "umbreld globs only '*/umbrel-app.yml', so these apps are invisible. Move app folders to the repo root.")
    if not top and not nested:
        rep.add("ERROR", "install", "store.layout.empty", ".", "No app folders with umbrel-app.yml found.")

    ids_seen: dict[str, str] = {}
    ports_seen: dict[int, str] = {}
    all_ids = set(official_ports)
    manifests = {}
    for d in top:
        try:
            manifests[d.name] = load_yaml(d / "umbrel-app.yml")
        except Exception:
            manifests[d.name] = None
        if isinstance(manifests[d.name], dict) and manifests[d.name].get("id"):
            all_ids.add(str(manifests[d.name]["id"]))

    for d in top:
        rep.apps_seen += 1
        visible = audit_app(root, d, manifests[d.name], store_id, rep, official_ports, ids_seen, ports_seen,
                            all_ids, os_version, online)
        rep.apps_visible += int(visible)

    audit_sync(root, rep, online, remote)


# ---- app-level checks --------------------------------------------------------
def audit_app(root, d: Path, m, store_id, rep: Report, official_ports, ids_seen, ports_seen, all_ids,
              os_version, online) -> bool:
    rel = d.name
    mf = f"{rel}/umbrel-app.yml"
    text = (d / "umbrel-app.yml").read_text(encoding="utf-8", errors="ignore")
    visible = True

    if not isinstance(m, dict):
        rep.add("ERROR", "install", "manifest.parse", mf,
                "YAML did not parse to a mapping. umbreld logs the error and silently drops the app.")
        return False

    app_id = m.get("id")
    if not isinstance(app_id, str) or not app_id:
        rep.add("ERROR", "install", "manifest.id.missing", mf, "Missing `id`.")
        return False

    # --- identity -----------------------------------------------------------
    if store_id and not app_id.startswith(store_id):
        rep.add("ERROR", "install", "app.id.prefix", mf,
                f"id `{app_id}` does not start with store id `{store_id}`; readRegistry() filters it out (silently hidden).")
        visible = False
    elif store_id and not app_id.startswith(store_id + "-"):
        rep.add("WARNING", "install", "app.id.prefix-dash", mf,
                f"id `{app_id}` passes umbreld's startsWith() check but lacks the `{store_id}-` convention.")
    if app_id != d.name:
        rep.add("ERROR", "install", "app.id.folder-mismatch", mf,
                f"Folder `{d.name}` != id `{app_id}`. The app is listed, but Install resolves "
                f"<repo>/{app_id}/ and fails with 'App template not found'.")
    if not APP_ID_RE.match(app_id):
        rep.add("ERROR", "install", "app.id.charset", mf, "id must match ^[a-zA-Z0-9-_]+$ or install throws 'Invalid app ID'.")
    if app_id in official_ports:
        rep.add("ERROR", "install", "app.id.official-collision", mf,
                f"id `{app_id}` also exists in the official Umbrel App Store. Duplicate ids resolve by repository "
                "order, so installs/updates use the OFFICIAL package, not yours.")
    if app_id in ids_seen:
        rep.add("ERROR", "install", "app.id.duplicate", mf, f"Duplicate id also used by `{ids_seen[app_id]}`.")
    ids_seen[app_id] = rel
    if m.get("disabled") is True:
        rep.add("INFO", "install", "app.disabled", mf, "`disabled: true` - hidden from the store.")
        visible = False

    # --- required fields (schema validation is DISABLED in umbreld) ----------
    for f in REQUIRED_FIELDS:
        if f not in m or m.get(f) in (None, ""):
            rep.add("ERROR", "install", f"manifest.{f}", mf,
                    f"Missing `{f}`. umbreld does not validate the schema at runtime, so this breaks later "
                    "in the UI or install path instead of being rejected up front.")
    for f in RECOMMENDED_FIELDS:
        if f not in m:
            rep.add("INFO" if f != "icon" else "ERROR", "icon" if f == "icon" else "install",
                    f"manifest.{f}", mf,
                    "Missing `icon`. umbreld falls back to the OFFICIAL gallery URL "
                    f"{OFFICIAL_GALLERY}/{app_id}/icon.svg, which 404s for community apps, so the UI shows a placeholder."
                    if f == "icon" else f"Recommended field `{f}` missing.")

    # manifestVersion compatibility
    mv = semver_norm(m.get("manifestVersion"))
    if mv is None:
        rep.add("ERROR", "install", "manifest.manifestVersion", mf, "manifestVersion is not a valid version; install throws 'App manifest version is invalid'.")
    elif ver_tuple(mv) > ver_tuple(os_version):
        rep.add("ERROR", "install", "manifest.manifestVersion", mf,
                f"manifestVersion {mv} > target umbrelOS {os_version}; listed as incompatible and install throws.")

    # version must be a quoted string (update detection = string inequality)
    raw_v = raw_scalar(text, "version")
    if raw_v is not None and not re.match(r"""^["']""", raw_v):
        parsed = m.get("version")
        if not isinstance(parsed, str) or str(parsed) != raw_v:
            rep.add("ERROR", "sync", "manifest.version.unquoted", mf,
                    f"version `{raw_v}` parses as {type(parsed).__name__} {parsed!r}. Quote it. Update detection "
                    "compares registry vs installed `version` with !==, so numeric coercion causes missed or phantom updates.")
        else:
            rep.add("WARNING", "sync", "manifest.version.unquoted", mf, f"Quote version `{raw_v}` to avoid YAML coercion.")

    # port
    port = m.get("port")
    if not isinstance(port, int):
        rep.add("ERROR", "install", "manifest.port", mf, "port must be an integer.")
    else:
        if port in RESERVED_PORTS:
            rep.add("ERROR", "install", "manifest.port.reserved", mf, f"port {port} is reserved ({RESERVED_PORTS[port]}).")
        if MACHINES_PORT_RANGE[0] <= port <= MACHINES_PORT_RANGE[1]:
            rep.add("ERROR", "install", "manifest.port.machines", mf,
                    f"port {port} is in 40000-49999, reserved for Machines in umbrelOS 2.0; install throws [app-port-reserved-for-machines].")
        clash = [k for k, v in official_ports.items() if v == port and k != app_id]
        if clash:
            rep.add("WARNING", "install", "manifest.port.official-clash", mf,
                    f"port {port} is also used by official app(s): {', '.join(clash[:4])}. Both cannot run together.")
        if port in ports_seen:
            rep.add("ERROR", "install", "manifest.port.duplicate", mf, f"port {port} duplicates `{ports_seen[port]}` in this store.")
        ports_seen[port] = rel

    for f in ("website", "support", "submission", "repo"):
        v = m.get(f)
        if isinstance(v, str) and v and not is_abs_url(v) and f != "support":
            rep.add("WARNING", "install", f"manifest.{f}.url", mf, f"`{f}` is not an absolute URL.")

    deps = m.get("dependencies") or []
    for dep in deps if isinstance(deps, list) else []:
        if dep not in all_ids:
            rep.add("ERROR", "install", "manifest.dependency.unknown", mf, f"dependency `{dep}` not found in this store or the official store.")

    # --- icon + gallery ---------------------------------------------------------
    audit_icon(d, m, app_id, rep, mf, online)

    # --- compose -------------------------------------------------------------------
    audit_compose(d, m, app_id, rep, rel)

    # --- update pipeline (file propagation) -------------------------------------------
    audit_update_files(d, rep, rel)
    return visible


def audit_icon(d: Path, m: dict, app_id: str, rep: Report, mf: str, online: bool):
    icon = m.get("icon")
    local_icons = [p.name for p in d.iterdir() if re.match(r"(?i)^(icon|logo)\.(svg|png|jpe?g|webp)$", p.name)]
    if isinstance(icon, str) and icon:
        if not is_abs_url(icon):
            rep.add("ERROR", "icon", "icon.relative", mf,
                    f"icon `{icon}` is not an absolute URL. umbreld passes it to the browser verbatim; it resolves "
                    "against the dashboard origin (e.g. http://umbrel.local/icon.svg) and 404s -> placeholder icon.")
        else:
            host = urllib.parse.urlparse(icon).netloc.lower()
            if icon.startswith("http://"):
                rep.add("WARNING", "icon", "icon.http", mf, "icon uses http://; blocked as mixed content when the dashboard is served over HTTPS.")
            for dead, why in DEAD_HOSTS.items():
                if host.endswith(dead):
                    rep.add("ERROR", "icon", "icon.dead-host", mf, why)
            for pat, why in MUTABLE_ICON_HOST_PATTERNS:
                if pat.search(icon):
                    rep.add("WARNING", "icon", "icon.mutable-url", mf,
                            f"icon URL is mutable ({why}). Browsers and CDNs cache by URL, so replacing the file in place "
                            "shows stale art. Use a commit-SHA or versioned filename URL and change the URL on each icon update.")
                    break
            if online:
                st, ct, cc, ln, err = http_probe(icon)
                if st != 200:
                    rep.add("ERROR", "icon", "icon.unreachable", mf, f"icon GET -> {st or err}. UI falls back to placeholder.")
                elif not ct.lower().startswith("image/"):
                    rep.add("ERROR", "icon", "icon.content-type", mf, f"icon served as `{ct}`; <img> will not render it.")
                elif ln and int(ln) > 512_000:
                    rep.add("WARNING", "icon", "icon.size", mf, f"icon is {int(ln)//1024} KB; keep under ~100 KB.")
        if local_icons:
            rep.add("INFO", "icon", "icon.local-file", mf,
                    f"Local file(s) {local_icons} exist in the app folder. umbreld never serves app-folder files to the UI; "
                    "only the `icon:` URL is used. Make sure the URL points to the hosted copy of this exact file.")
    elif local_icons:
        rep.add("ERROR", "icon", "icon.local-only", mf,
                f"Has {local_icons} but no `icon:` URL. The local file is never used; the official-gallery fallback 404s.")

    gallery = m.get("gallery")
    if isinstance(gallery, list):
        if len(set(map(str, gallery))) != len(gallery):
            rep.add("WARNING", "icon", "gallery.duplicate", mf, "gallery has duplicate entries.")
        for g in gallery:
            if not isinstance(g, str) or not is_abs_url(g):
                rep.add("ERROR", "icon", "gallery.relative", mf,
                        f"gallery entry {g!r} is not an absolute URL. Only the official store prefixes gallery filenames; "
                        "community stores use entries verbatim.")
            elif online:
                st, ct, *_ = http_probe(g)
                if st != 200 or not ct.lower().startswith("image/"):
                    rep.add("WARNING", "icon", "gallery.unreachable", mf, f"gallery image {g} -> {st} {ct}")
    elif gallery is not None:
        rep.add("ERROR", "icon", "gallery.type", mf, "gallery must be a list (use [] if none); readRegistry() maps over it.")


def audit_compose(d: Path, m: dict, app_id: str, rep: Report, rel: str):
    cf = d / "docker-compose.yml"
    where = f"{rel}/docker-compose.yml"
    if not cf.exists():
        rep.add("ERROR", "install", "compose.missing", where, "docker-compose.yml missing; install cannot start the app.")
        return
    try:
        c = load_yaml(cf) or {}
    except Exception as e:
        rep.add("ERROR", "install", "compose.parse", where, f"YAML parse failed: {e}")
        return
    services = c.get("services")
    if not isinstance(services, dict) or not services:
        rep.add("ERROR", "install", "compose.services", where, "No `services:` mapping.")
        return
    if "version" in c:
        rep.add("INFO", "install", "compose.version-key", where, "Top-level `version:` is obsolete in Compose v2 (harmless).")

    declared = exported_vars(d / "exports.sh")
    # container names umbreld will force: <app-id>_<service>_1 unless container_name set
    names = {}
    for sname, svc in services.items():
        svc = svc or {}
        names[svc.get("container_name") or f"{app_id}_{sname}_1"] = sname

    proxy = services.get("app_proxy")
    if proxy is None:
        rep.add("WARNING", "install", "compose.app_proxy.missing", where,
                "No `app_proxy` service. The umbrelOS 2.0 app gateway has nothing to route, so 'Open' from the dashboard will not work "
                "unless the app publishes its own host port.")
    else:
        env = proxy.get("environment") or {}
        if isinstance(env, list):
            env = dict(e.split("=", 1) if "=" in e else (e, "") for e in env)
        host, aport = str(env.get("APP_HOST", "")).strip(), env.get("APP_PORT")
        if not host:
            rep.add("ERROR", "install", "compose.app_proxy.APP_HOST", where, "app_proxy.APP_HOST missing; gateway config resolves to null.")
        elif "$" not in host and host not in names:
            expect = ", ".join(sorted(k for k in names if not k.startswith(f"{app_id}_app_proxy")))
            rep.add("ERROR", "install", "compose.app_proxy.APP_HOST", where,
                    f"APP_HOST `{host}` matches no container. umbreld names containers <app-id>_<service>_1; expected one of: {expect}.")
        try:
            p = int(str(aport))
            if not 1 <= p <= 65535:
                raise ValueError
        except (TypeError, ValueError):
            if "$" not in str(aport):
                rep.add("ERROR", "install", "compose.app_proxy.APP_PORT", where, f"APP_PORT {aport!r} is not a valid port.")
        extra = set(proxy) - {"environment"}
        if extra:
            rep.add("WARNING", "install", "compose.app_proxy.extra-keys", where,
                    f"app_proxy defines {sorted(extra)}; in umbrelOS 2.0 app_proxy is config-only (no container is created).")

    for sname, svc in services.items():
        if sname == "app_proxy":
            continue
        svc = svc or {}
        sw = f"{where} [{sname}]"
        img = svc.get("image")
        if not img and not svc.get("build"):
            rep.add("ERROR", "install", "compose.image.missing", sw, "Service has neither image nor build.")
        elif svc.get("build") and not img:
            rep.add("ERROR", "install", "compose.build", sw, "`build:` is not supported by the Umbrel install path; publish an image and reference it.")
        elif img:
            if "@sha256:" not in img:
                sev = "ERROR" if img.endswith(":latest") or ":" not in img.split("/")[-1] else "WARNING"
                rep.add(sev, "install", "compose.image.unpinned", sw,
                        f"Image `{img}` is not digest-pinned. The same app version can pull different bits; "
                        "use name:tag@sha256:<digest> (multi-arch index digest).")
        if not svc.get("restart"):
            rep.add("WARNING", "install", "compose.restart", sw, "No restart policy; use `restart: on-failure`.")
        if svc.get("network_mode") == "host":
            rep.add("WARNING", "install", "compose.host-network", sw, "network_mode: host bypasses the gateway and port checks.")
        for p in svc.get("ports") or []:
            hp = str(p).split(":")[-2] if str(p).count(":") >= 1 else None
            if hp and hp.isdigit():
                hpi = int(hp)
                if hpi in RESERVED_PORTS:
                    rep.add("ERROR", "install", "compose.ports.reserved", sw, f"Publishes reserved host port {hpi}.")
                if MACHINES_PORT_RANGE[0] <= hpi <= MACHINES_PORT_RANGE[1]:
                    rep.add("WARNING", "install", "compose.ports.machines", sw, f"Publishes host port {hpi} inside the Machines range.")
        for v in svc.get("volumes") or []:
            src = v.split(":")[0] if isinstance(v, str) else (v or {}).get("source", "")
            ro = isinstance(v, str) and v.rstrip().endswith(":ro")
            if isinstance(src, str) and src.startswith("/") and (ro or src in ("/var/run/docker.sock", "/etc/localtime")):
                rep.add("INFO", "install", "compose.volume.host-system", sw,
                        f"Host system path `{src}` mounted{' read-only' if ro else ''}; intentional for monitoring/Docker access, holds no app data.")
            elif isinstance(src, str) and src.startswith("/") and not src.startswith("${"):
                rep.add("WARNING", "install", "compose.volume.absolute", sw,
                        f"Bind mount `{src}` is an absolute host path; use ${{APP_DATA_DIR}}/data/... so data survives updates/backups.")
            elif isinstance(src, str) and src.startswith("./"):
                rep.add("INFO", "install", "compose.volume.relative", sw, f"Relative bind `{src}`; prefer ${{APP_DATA_DIR}}/data/...")
        user = svc.get("user")
        if user and str(user) not in ("1000:1000", "1000"):
            rep.add("INFO", "install", "compose.user", sw, f"Runs as {user}; repo files are chowned 1000:1000 at sync.")

    unknown = sorted({v for v in env_refs(c) if v not in UMBREL_ENV and v not in declared and not v.startswith("APP_")})
    if unknown:
        rep.add("WARNING", "install", "compose.env.undefined", where,
                f"References {unknown} not exported by umbrelOS or this app's exports.sh; they will be empty strings.")

    compose_cmd = compose_binary()
    if compose_cmd:
        # Mirror umbreld's runtime: app_proxy is removed and the common fragment
        # (external umbrel_main_network) is merged in front of the app file.
        import tempfile
        env = os.environ.copy()
        env.update({k: f"/tmp/{k.lower()}" for k in UMBREL_ENV})
        env.update({"APP_PASSWORD": "x", "APP_SEED": "x", "APP_ID": app_id, "DEVICE_DOMAIN_NAME": "umbrel.local"})
        env["APP_DATA_DIR"] = str(d)
        ex = d / "exports.sh"
        if ex.exists():  # evaluate exports.sh the way app-script does, to get real values
            r0 = subprocess.run(["bash", "-c", f"source '{ex}' >/dev/null 2>&1; env -0"], capture_output=True, env=env)
            for kv in r0.stdout.split(b"\0"):
                if b"=" in kv:
                    k, _, val = kv.decode(errors="ignore").partition("=")
                    env[k] = val
        for v in declared:
            env.setdefault(v, "x")
        runtime = copy.deepcopy(c)
        runtime.get("services", {}).pop("app_proxy", None)
        with tempfile.TemporaryDirectory() as td:
            common = Path(td) / "docker-compose.common.yml"
            common.write_text("networks:\n  default:\n    external: true\n    name: umbrel_main_network\n")
            rt = Path(td) / "docker-compose.yml"
            rt.write_text(yaml.safe_dump(runtime, sort_keys=False))
            r = subprocess.run(compose_cmd + ["-p", app_id, "--project-directory", str(d), "-f", str(common), "-f", str(rt), "config", "-q"],
                               capture_output=True, text=True, env=env)
        if r.returncode != 0:
            rep.add("ERROR", "install", "compose.config", where, f"`docker compose config` failed: {' '.join(l for l in r.stderr.splitlines() if 'obsolete' not in l)[:400]}")
        else:
            rep.add("INFO", "install", "compose.config.ok", where, "`docker compose config` passed with umbrelOS common fragment.")


def compose_binary():
    if shutil.which("docker"):
        r = subprocess.run(["docker", "compose", "version"], capture_output=True, text=True)
        if r.returncode == 0:
            return ["docker", "compose"]
    if shutil.which("docker-compose"):
        return ["docker-compose"]
    return None


def audit_update_files(d: Path, rep: Report, rel: str):
    extras = []
    for p in d.iterdir():
        if p.name in (".gitkeep", "README.md"):
            continue
        if any(fnmatch.fnmatch(p.name, pat) for pat in UPDATE_WHITELIST):
            continue
        if re.match(r"(?i)^(icon|logo)\.", p.name):
            continue
        if p.is_dir() and p.name == "data" and all(f.name == ".gitkeep" for f in p.rglob("*") if f.is_file()):
            continue  # skeleton of empty data dirs: only needed at install, nothing to update
        extras.append(p.name + ("/" if p.is_dir() else ""))
    if extras:
        rep.add("WARNING", "sync", "update.non-whitelisted-files", f"{rel}/",
                f"{extras} are copied on first INSTALL only. On UPDATE, app-script copies just "
                "docker-compose.yml, *.template, exports.sh, torrc, hooks/ and umbrel-app.yml, so changes to these files "
                "never reach already-installed apps. Generate them from a *.template or a pre-start hook instead.")
    hooks = d / "hooks"
    if hooks.is_dir():
        for h in hooks.iterdir():
            if h.name not in VALID_HOOKS:
                rep.add("WARNING", "install", "hooks.name", f"{rel}/hooks/{h.name}", "Not a hook name umbrelOS calls.")
            elif not (h.stat().st_mode & stat.S_IXUSR):
                rep.add("ERROR", "install", "hooks.not-executable", f"{rel}/hooks/{h.name}",
                        "Hook is not executable; execute_hook() silently skips non-executable hooks. `git update-index --chmod=+x`.")
        rep.add("INFO", "install", "hooks.errors-swallowed", f"{rel}/hooks/",
                "Hook failures are swallowed (`|| true`); a failing hook will not fail the install - test hooks explicitly.")
    for g in d.rglob(".gitkeep"):
        rep.add("INFO", "sync", "sync.gitkeep", str(g.relative_to(d.parent)),
                "umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended).")
        break


# ---- repository sync -----------------------------------------------------------
def git(root: Path, *args):
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def audit_sync(root: Path, rep: Report, online: bool, remote: str | None):
    rep.add("INFO", "sync", "sync.model", "(umbreld)",
            "umbreld checks every 5 min: compares local HEAD with the remote's default-branch HEAD and, if different, does a "
            "fresh shallow clone (depth 1, single default branch) swapped in atomically. Only the DEFAULT branch is ever used.")
    size = sum(p.stat().st_size for p in root.rglob("*") if p.is_file() and ".git" not in p.parts)
    if size > 50 * 1024 * 1024:
        rep.add("WARNING", "sync", "sync.repo-size", ".",
                f"Working tree is {size/1e6:.0f} MB. Every change triggers a full re-clone; keep images/binaries out of the repo.")
    if shutil.which("git") and (root / ".git").exists():
        rc, dirty, _ = git(root, "status", "--porcelain")
        if dirty:
            rep.add("WARNING", "sync", "sync.uncommitted", ".", "Uncommitted changes: Umbrel only sees what is pushed.")
        rc, branch, _ = git(root, "rev-parse", "--abbrev-ref", "HEAD")
        rc, head_ref, _ = git(root, "symbolic-ref", "--short", "refs/remotes/origin/HEAD")
        if head_ref and branch and head_ref.split("/")[-1] != branch:
            rep.add("WARNING", "sync", "sync.branch", ".",
                    f"Local branch `{branch}` != remote default `{head_ref}`. Umbrel ignores non-default branches.")
        rc, ahead, _ = git(root, "rev-list", "--count", "@{u}..HEAD")
        if rc == 0 and ahead not in ("", "0"):
            rep.add("WARNING", "sync", "sync.unpushed", ".", f"{ahead} unpushed commit(s).")
        rc, modes, _ = git(root, "ls-files", "-s", "--", "*/hooks/*")
        for line in modes.splitlines():
            if line.startswith("100644"):
                rep.add("ERROR", "sync", "sync.hook-mode", line.split("\t")[-1],
                        "Committed as 100644; the clone on Umbrel will not be executable.")
        if not remote:
            rc, remote, _ = git(root, "remote", "get-url", "origin")
    if remote:
        if remote.startswith("git@") or remote.startswith("ssh://"):
            rep.add("ERROR", "sync", "sync.url.ssh", remote,
                    "SSH URLs are rejected (umbreld requires a valid http(s) URL and clones over HTTP). Add the https:// URL.")
            remote = None
        elif remote.rstrip("/").endswith(".git"):
            rep.add("INFO", "sync", "sync.url.identity", remote,
                    "Store identity is the exact URL string. Adding the same repo with and without `.git` creates two stores; "
                    "duplicate ids then resolve to whichever was added first.")
    if online and remote and shutil.which("git"):
        env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
        r = subprocess.run(["git", "ls-remote", "--symref", remote, "HEAD"], capture_output=True, text=True, env=env, timeout=40)
        if r.returncode != 0:
            rep.add("ERROR", "sync", "sync.remote.unreachable", remote,
                    "Anonymous `git ls-remote` failed. umbreld clones without credentials, so private repos cannot be added "
                    f"(addRepository throws). stderr: {r.stderr.strip()[:200]}")
        else:
            m = re.search(r"ref: refs/heads/(\S+)\s+HEAD", r.stdout)
            rep.add("INFO", "sync", "sync.remote.ok", remote,
                    f"Anonymous HEAD resolves (default branch: {m.group(1) if m else 'unknown'}). This is the only branch Umbrel will track.")
            if shutil.which("git") and (root / ".git").exists():
                rc, local, _ = git(root, "rev-parse", "HEAD")
                remote_sha = r.stdout.split()[-2] if r.stdout.split() else ""
                if local and remote_sha and local != remote_sha:
                    rep.add("WARNING", "sync", "sync.remote.drift", remote,
                            f"Local HEAD {local[:8]} != remote HEAD {remote_sha[:8]}; Umbrel will install the remote version.")


# ---- output -----------------------------------------------------------------------
def render(rep: Report, fmt: str, root: Path) -> str:
    order = {"ERROR": 0, "WARNING": 1, "INFO": 2}
    issues = sorted(rep.issues, key=lambda i: (order[i.severity], i.area, i.where))
    counts = {s: sum(1 for i in issues if i.severity == s) for s in order}
    if fmt == "json":
        return json.dumps({"root": str(root), "apps_seen": rep.apps_seen, "apps_visible": rep.apps_visible,
                           "counts": counts, "issues": [i.__dict__ for i in issues]}, indent=2)
    if fmt == "md":
        out = [f"# umbrelOS store audit: `{root.name}`", "",
               f"Apps found: {rep.apps_seen} · visible in store: {rep.apps_visible} · "
               f"errors: {counts['ERROR']} · warnings: {counts['WARNING']} · info: {counts['INFO']}", "",
               "| Severity | Area | Rule | Location | Finding |", "|---|---|---|---|---|"]
        for i in issues:
            msg = i.message.replace("|", "\\|")
            out.append(f"| {i.severity} | {i.area} | `{i.rule}` | `{i.where}` | {msg} |")
        return "\n".join(out) + "\n"
    out = [f"umbrelOS store audit: {root}",
           f"apps found={rep.apps_seen} visible={rep.apps_visible} errors={counts['ERROR']} "
           f"warnings={counts['WARNING']} info={counts['INFO']}", ""]
    for i in issues:
        out.append(f"{i.severity:<7} [{i.area}] {i.rule}  {i.where}\n        {i.message}")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", type=Path, help="Path to the community store repository checkout")
    ap.add_argument("--online", action="store_true", help="Probe icon/gallery URLs and the git remote")
    ap.add_argument("--remote", help="Store URL exactly as you will add it in Umbrel (defaults to git origin)")
    ap.add_argument("--os-version", default="2.0.0", help="Target umbrelOS version (default 2.0.0)")
    ap.add_argument("--official-ports", type=Path, default=HERE / "official_ports.json",
                    help="JSON {app_id: port} snapshot of the official store")
    ap.add_argument("--format", choices=["text", "md", "json"], default="text")
    a = ap.parse_args()
    root = a.root.resolve()
    if not root.is_dir():
        sys.exit(f"Not a directory: {root}")
    official = json.loads(a.official_ports.read_text()) if a.official_ports.exists() else {}
    rep = Report()
    audit_store(root, rep, official, semver_norm(a.os_version) or "2.0.0", a.online, a.remote)
    print(render(rep, a.format, root), end="")
    sys.exit(1 if any(i.severity == "ERROR" for i in rep.issues) else 0)


if __name__ == "__main__":
    main()
