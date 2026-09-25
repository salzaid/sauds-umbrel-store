#!/usr/bin/env python3
"""Generate the corrected 48-app Saud community app store for umbrelOS 1.x/2.x.

Usage: python3 generate.py [--resolve]   (--resolve refreshes image digests)
Output: ../saud-umbrel-store/
"""
import copy, json, os, re, shutil, stat, subprocess, sys
from pathlib import Path
import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, "/tmp/build")
import apps as A

OUT = HERE.parent / "saud-umbrel-store"
UA = Path("/tmp/ua")  # sparse clone of getumbrel/umbrel-apps
AUDIT = HERE.parent / "umbrel-audit"
DIGESTS = HERE / "digests.json"
GALLERY_SHA = "7655ed83a9b26c50dc5f16888591da9d46d294a6"
PREFIX = "saud"

official_ports = json.loads((AUDIT / "official_ports.json").read_text())
taken = set(int(p) for p in official_ports.values())
RESERVED = {80, 443, 2000, 8080}  # 8080 kept free: common default and umbrel dev port


class Q(str):
    pass

def q_repr(d, v):
    return d.represent_scalar("tag:yaml.org,2002:str", v, style='"')

class Lit(str):
    pass

def lit_repr(d, v):
    return d.represent_scalar("tag:yaml.org,2002:str", v, style="|")

yaml.add_representer(Q, q_repr)
yaml.add_representer(Lit, lit_repr)


def dump(obj):
    return yaml.dump(obj, sort_keys=False, allow_unicode=True, width=1000, default_flow_style=False)


# ---------------------------------------------------------------------------
# Ports
# ---------------------------------------------------------------------------
_next = [5401]

def alloc_port():
    while True:
        p = _next[0]
        _next[0] += 1
        if p in taken or p in RESERVED or 40000 <= p <= 49999:
            continue
        taken.add(p)
        return p


# ---------------------------------------------------------------------------
# Images
# ---------------------------------------------------------------------------
def collect_images(services):
    for s in services.values():
        if "image" in s:
            yield s["image"]

digest_cache = json.loads(DIGESTS.read_text()) if DIGESTS.exists() else {}

def pin(ref):
    if "@sha256:" in ref:
        return ref
    if ref not in digest_cache or "--resolve" in sys.argv:
        import reg
        d, plats = reg.digest(ref)
        if plats and "linux/amd64" not in plats:
            raise SystemExit(f"{ref}: no linux/amd64 image")
        digest_cache[ref] = d
    return f"{ref}@{digest_cache[ref]}"


def subst(obj, mapping):
    if isinstance(obj, str):
        for k, v in mapping.items():
            obj = obj.replace(k, str(v))
        return obj
    if isinstance(obj, dict):
        return {k: subst(v, mapping) for k, v in obj.items()}
    if isinstance(obj, list):
        return [subst(v, mapping) for v in obj]
    return obj


# ---------------------------------------------------------------------------
# Custom apps
# ---------------------------------------------------------------------------
def write_exec(path: Path, text: str):
    path.write_text(text)
    path.chmod(0o755)


def build_custom(spec, catalog):
    app_id = f"{PREFIX}-{spec['slug']}"
    d = OUT / app_id
    d.mkdir(parents=True)
    port = alloc_port()
    m = {"{ID}": app_id, "{PORT}": port, "{DOMAIN}": "umbrel.local"}
    services = subst(copy.deepcopy(spec["services"]), m)
    for s in services.values():
        if "image" in s:
            s["image"] = pin(s["image"])
    app_port = int(subst(str(spec["app_port"]), m))

    proxy_env = {"APP_HOST": f"{app_id}_{spec['main']}_1", "APP_PORT": app_port}
    if spec.get("app_protocol"):
        proxy_env["APP_PROTOCOL"] = spec["app_protocol"]
    if spec.get("no_proxy_auth"):
        proxy_env["PROXY_AUTH_ADD"] = Q("false")
    compose = {"version": Q("3.7"), "services": {"app_proxy": {"environment": proxy_env}}}
    for s in services.values():
        if "user" in s:
            s["user"] = Q(s["user"])
        if "ports" in s:
            s["ports"] = [Q(x) for x in s["ports"]]
    compose["services"].update(services)
    if spec.get("top_networks"):
        compose["networks"] = spec["top_networks"]
    if spec.get("top_configs"):
        compose["configs"] = {k: {"content": Lit(v["content"])} for k, v in spec["top_configs"].items()}
    (d / "docker-compose.yml").write_text(dump(compose))

    # data dirs with .gitkeep
    for sub in spec.get("data_dirs", []):
        p = d / "data" / sub
        p.mkdir(parents=True, exist_ok=True)
        (p / ".gitkeep").write_text("")

    # exports.sh for published ports / extra vars
    ex = ""
    upper = spec["slug"].upper().replace("-", "_")
    for k, v in (spec.get("exports_ports") or {}).items():
        ex += f'export APP_SAUD_{upper}_{k}_PORT="{v}"\n'
    ex += spec.get("exports_extra", "")
    if ex:
        (d / "exports.sh").write_text("# Sourced by umbrelOS before compose; values are informational or used in compose.\n" + ex)

    desc = subst(spec["description"], m)
    man = {
        "manifestVersion": 1.1,
        "id": app_id,
        "disabled": bool(spec.get("disabled", False)),
        "name": spec["name"],
        "tagline": spec["tagline"],
        "icon": spec["icon"],
        "category": spec["category"],
        "version": Q(spec["version"]),
        "port": port,
        "description": Lit(desc.rstrip() + "\n"),
        "developer": spec["developer"],
        "website": spec["website"],
        "submitter": "Saud Alzaid",
        "submission": "https://github.com/CHANGE-ME/saud-umbrel-store",
        "repo": spec["repo"],
        "support": spec["support"],
        "gallery": [],
        "releaseNotes": Q(""),
        "dependencies": [],
        "path": Q(spec.get("path", "")),
        "defaultUsername": Q(spec.get("default_username", "")),
        "defaultPassword": Q(spec.get("default_password_text", "")),
    }
    if spec.get("default_password"):
        man["deterministicPassword"] = True
    if spec.get("permissions"):
        man["permissions"] = spec["permissions"]
    if not man["disabled"]:
        del man["disabled"]
    (d / "umbrel-app.yml").write_text(dump(man))
    catalog.append({"id": app_id, "name": spec["name"], "group": spec["group"], "port": port,
                    "status": "disabled" if spec.get("disabled") else "custom",
                    "version": spec["version"], "images": [s["image"] for s in services.values() if "image" in s],
                    "published": list((spec.get("exports_ports") or {}).values()), "gpu": bool(spec.get("permissions")),
                    "icon": spec["icon"], "note": spec["tagline"]})


# ---------------------------------------------------------------------------
# Mirrored official apps (disabled duplicates)
# ---------------------------------------------------------------------------
def build_mirror(off_id, catalog):
    src = UA / off_id
    if not src.exists():
        raise SystemExit(f"missing official app {off_id} in {UA}")
    app_id = f"{PREFIX}-{off_id}"
    d = OUT / app_id
    shutil.copytree(src, d, symlinks=False)
    pat = re.compile(rf"(?<![\w.-]){re.escape(off_id)}_([A-Za-z0-9-]+)_1\b")
    for f in d.rglob("*"):
        if f.is_file() and f.name != ".gitkeep":
            try:
                t = f.read_text()
            except UnicodeDecodeError:
                continue
            nt = pat.sub(lambda mo: f"{app_id}_{mo.group(1)}_1", t)
            if nt != t:
                mode = f.stat().st_mode
                f.write_text(nt)
                f.chmod(mode)
    mf = d / "umbrel-app.yml"
    man = yaml.safe_load(mf.read_text())
    port = alloc_port()
    official_port = man.get("port")
    man["id"] = app_id
    man["disabled"] = True
    man["port"] = port
    man["icon"] = f"https://raw.githubusercontent.com/getumbrel/umbrel-apps-gallery/{GALLERY_SHA}/{off_id}/icon.svg"
    man["gallery"] = []
    man["version"] = Q(str(man.get("version")))
    man["tagline"] = f"Install from the official Umbrel App Store ({man.get('tagline', '')})"
    man["description"] = Lit(f"This is a disabled mirror of the official `{off_id}` app. Install {man.get('name')} from the official Umbrel App Store instead: it is maintained, updated and tested there.\n\nThe mirror is kept only so this store's catalog stays complete. If you ever enable it, it uses its own app id and port {port} so it cannot collide with the official app.\n\n" + str(man.get("description", "")).strip() + "\n")
    man["submitter"] = "Saud Alzaid (mirror of official package)"
    man["submission"] = "https://github.com/getumbrel/umbrel-apps"
    for k in ("releaseNotes", "path", "defaultUsername", "defaultPassword"):
        if k in man and isinstance(man[k], str):
            man[k] = Q(man[k])
    man.setdefault("releaseNotes", Q(""))
    man.setdefault("path", Q(""))
    man.setdefault("dependencies", [])
    if isinstance(man.get("manifestVersion"), (int, float)) and man["manifestVersion"] < 1.1:
        pass
    mf.write_text(dump(man))
    cmp = yaml.safe_load((d / "docker-compose.yml").read_text())
    imgs = [s.get("image") for s in (cmp.get("services") or {}).values() if s.get("image")]
    catalog.append({"id": app_id, "name": man.get("name"), "group": A.MIRROR_GROUP[off_id], "port": port,
                    "status": "mirror", "version": str(man["version"]), "images": imgs, "published": [], "gpu": False,
                    "icon": man["icon"], "note": f"Official app `{off_id}` (official port {official_port})"})


# ---------------------------------------------------------------------------
def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    (OUT / "umbrel-app-store.yml").write_text('id: "saud"\nname: "Saud"\n')
    catalog = []
    for spec in A.CUSTOM:
        build_custom(spec, catalog)
    for off in A.MIRRORS:
        build_mirror(off, catalog)
    import docs
    docs.write_all(OUT, catalog, AUDIT)
    DIGESTS.write_text(json.dumps(digest_cache, indent=1, sort_keys=True))
    (HERE / "catalog.json").write_text(json.dumps(catalog, indent=1))
    print(f"apps: {len(catalog)} custom={sum(c['status']=='custom' for c in catalog)} "
          f"disabled={sum(c['status']=='disabled' for c in catalog)} mirrors={sum(c['status']=='mirror' for c in catalog)}")


if __name__ == "__main__":
    main()
