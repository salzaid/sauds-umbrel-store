"""README, docs/ and tooling for the generated store."""
import shutil
from pathlib import Path

GROUP_ORDER = ["Operations", "AI", "Analytics", "Imaging", "Documents", "Interoperability", "Education", "Development"]

STATUS_TEXT = {
    "custom": "Packaged",
    "disabled": "Disabled (see note)",
    "mirror": "Disabled mirror: install the official app",
}

# Rough steady-state RAM for planning on a 16 GB machine (not measured on hardware).
RAM = {
    "saud-dozzle": 0.05, "saud-netdata": 0.3, "saud-backrest": 0.1, "saud-lemonade": 1.0, "saud-flowise": 0.5,
    "saud-qdrant": 0.3, "saud-litellm": 0.8, "saud-postgresql": 0.3, "saud-metabase": 1.5, "saud-superset": 1.0,
    "saud-duckdb": 0.5, "saud-pgadmin": 0.3, "saud-orthanc-lab-basic": 0.2, "saud-orthanc-research-viewer": 0.3,
    "saud-orthanc-research-archive": 0.5, "saud-ohif-viewer": 0.3, "saud-dicom-deid": 0.2, "saud-onlyoffice": 2.0,
    "saud-hedgedoc": 0.3, "saud-oie": 1.0, "saud-hapi-fhir": 1.5, "saud-fhir-validator": 1.5, "saud-synthea": 0.2,
    "saud-openemr": 0.8, "saud-openmrs": 2.5, "saud-limesurvey": 0.4, "saud-moodle": 0.6, "saud-baserow": 1.5,
    "saud-glitchtip": 0.5,
}

WAVES = [
    ("Wave 1: foundation", ["saud-dozzle", "saud-netdata", "saud-backrest", "saud-postgresql"],
     "Install these first. Dozzle shows the logs of every later install, Netdata shows memory pressure, Backrest protects app data."),
    ("Wave 2: local AI", ["saud-lemonade", "saud-qdrant", "saud-flowise", "saud-litellm"],
     "Load a small model in Lemonade first and confirm the GPU is used (Netdata > GPU) before adding the rest."),
    ("Wave 3: analytics", ["saud-pgadmin", "saud-metabase", "saud-duckdb", "saud-superset"],
     "Metabase and Superset overlap; keep the one you prefer running and stop the other."),
    ("Wave 4: imaging lab", ["saud-orthanc-lab-basic", "saud-orthanc-research-viewer", "saud-ohif-viewer", "saud-dicom-deid", "saud-orthanc-research-archive"],
     "Each Orthanc app has its own DICOM port (14242 to 14246). Send studies to saud-dicom-deid first, then forward the de-identified copy."),
    ("Wave 5: interoperability", ["saud-synthea", "saud-hapi-fhir", "saud-fhir-validator", "saud-oie"],
     "Generate synthetic patients with Synthea, load them into HAPI FHIR, validate with the FHIR Validator, route messages with OIE."),
    ("Wave 6: documents and education", ["saud-hedgedoc", "saud-onlyoffice", "saud-limesurvey", "saud-moodle"],
     "Moodle and LimeSurvey must be opened at the umbrel.local address shown in their description."),
    ("Wave 7: clinical sandboxes and development", ["saud-openemr", "saud-openmrs", "saud-baserow", "saud-glitchtip"],
     "OpenEMR and OpenMRS are heavy; run one at a time with synthetic data only."),
]


def table(rows, header):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def write_all(out: Path, catalog, audit_dir: Path):
    by = {c["id"]: c for c in catalog}

    # ---------------- README ----------------
    rows = []
    for g in GROUP_ORDER:
        for c in sorted([c for c in catalog if c["group"] == g], key=lambda c: c["id"]):
            extra = []
            if c["published"]:
                extra.append("host ports " + ", ".join(str(p) for p in c["published"]))
            if c["gpu"]:
                extra.append("GPU")
            rows.append([g, f"`{c['id']}`", c["name"], c["version"], c["port"], STATUS_TEXT[c["status"]], "; ".join(extra)])
    n_custom = sum(c["status"] == "custom" for c in catalog)
    n_dis = sum(c["status"] == "disabled" for c in catalog)
    n_mir = sum(c["status"] == "mirror" for c in catalog)

    readme = f"""# Saud community app store for umbrelOS

A personal community app store for umbrelOS with {len(catalog)} app folders: {n_custom} packaged apps, {n_dis} disabled placeholders and {n_mir} disabled mirrors of apps that already exist in the official Umbrel App Store.

This repository is a reconstruction. The original 48-app scaffold archive was not available, so the store was rebuilt from its catalog with every correction from the umbrelOS store audit applied. It passes the audit with 0 errors and every compose file passes `docker compose config`, but no app has yet been installed on real hardware. Treat the first install of each app as a test.

Use it with de-identified or synthetic data only. None of these packages is configured for clinical use.

## Add the store to your Umbrel

1. Create an empty public GitHub repository, for example `saud-umbrel-store`.
2. Replace `CHANGE-ME` in every `umbrel-app.yml` (field `submission`) with your GitHub user name:
   `grep -rl CHANGE-ME . | xargs sed -i 's/CHANGE-ME/<your-user>/g'`
3. Push this folder to the default branch (umbrelOS only reads the default branch):
   ```
   git init -b main
   git add -A
   git commit -m "Saud app store"
   git remote add origin https://github.com/<your-user>/saud-umbrel-store.git
   git push -u origin main
   ```
4. On the Umbrel: App Store > the three-dot menu > Community App Stores > paste `https://github.com/<your-user>/saud-umbrel-store` > Add.
5. The store appears as "Saud". Install apps in the order in [docs/INSTALL-WAVES.md](docs/INSTALL-WAVES.md).

umbrelOS re-reads the repository about every 5 minutes. After a push, wait a few minutes or remove and re-add the store.

## Apps

{table(rows, ["Group", "App id", "Name", "Version", "Port", "Status", "Notes"])}

Open an app at `http://umbrel.local:<Port>`. Where an app shows a password in umbrelOS, it is derived from your device and is stable across reinstalls on the same Umbrel.

## Why some apps are disabled

- The {n_mir} mirrors duplicate apps in the official store (Portainer, Uptime Kuma, Langflow, Grafana, JupyterLab, Nextcloud, Vikunja, Outline, BookStack, Mattermost, code-server, Gitea, Forgejo, MinIO, Appsmith, NocoDB). Install those from the official store, which keeps them updated. The mirrors are copies of the official packages with renamed ids, container names and ports, kept so the catalog is complete.
- `saud-dify`: Dify 1.17 needs about ten containers with fixed service names and many env files. It cannot be packaged reliably without hardware testing. Run it as a Portainer stack with the upstream compose file, or use Flowise.
- `saud-h5p`: H5P has no maintained stand-alone server. It is built into Moodle.
- `saud-github-actions-runner`: needs a repository URL and token and has no web page. See its description to enable it.
- Sentry is replaced by `saud-glitchtip`, which accepts Sentry SDKs. Self-hosted Sentry needs 20+ containers and far more memory than this machine has spare.

## Corrections applied

See [docs/CORRECTIONS.md](docs/CORRECTIONS.md) for the full list. In short: app folders sit at the repository root with `saud-` ids that match their folder names; every manifest is complete with a quoted version; icons are absolute, pinned URLs that were checked to return an image; ports are unique and avoid official apps; every image is pinned to a multi-architecture digest; data lives under `${{APP_DATA_DIR}}/data` with the folders committed; non-1000 containers get a one-shot ownership fix; GPU access uses the `GPU` permission instead of device mappings; and config files live inside `docker-compose.yml` so they update with the app.

## Updating an app

1. Change the tag in `docker-compose.yml`, resolve the new digest, and write `image: name:tag@sha256:<digest>`.
2. Update `version` (quoted) and `releaseNotes` in `umbrel-app.yml`.
3. Run the audit (next section), commit and push. umbrelOS offers the update when the version changes.

Only `docker-compose.yml`, `*.template`, `exports.sh`, `torrc`, `hooks/` and `umbrel-app.yml` are copied to installed apps on update, which is why this store keeps configuration inside the compose file.

## Updating an icon

Icons are cached by URL in browsers and CDNs, so never replace an image in place.

1. Pick the new image and host it at an immutable URL: a file in a repository at a specific commit (`https://raw.githubusercontent.com/<owner>/<repo>/<commit-sha>/<path>`) or a jsDelivr URL pinned to a commit (`https://cdn.jsdelivr.net/gh/<owner>/<repo>@<commit-sha>/<path>`).
2. Check it: `curl -sIL <url>` must end with `HTTP/2 200` and `content-type: image/...`.
3. Put the new URL in `icon:` and bump `version` if you want installed apps to pick it up at once; the store listing refreshes at the next sync either way.
4. Run the audit with `--online`, which fetches every icon.

## Audit before every push

```
pip install pyyaml
python3 .tools/audit_umbrel_store.py . --online
```

It exits with code 1 if there is any ERROR. The GitHub workflow in `.github/workflows/umbrel-store-audit.yml` runs the same check on every push and pull request.

## Troubleshooting

- App not listed: the folder name must equal `id`, the folder must be at the repository root, and the app must not be `disabled: true`.
- Install spins and fails: open Dozzle and read the log of the failing container. Most first-start failures are a database that is still initialising; wait and restart the app.
- "Permission denied" in a log: the app writes as a user other than 1000. Check that its `init` or `perms` container completed.
- Page loads at the IP but redirects to `umbrel.local`: Moodle, LimeSurvey, HedgeDoc, Baserow, GlitchTip and HAPI FHIR build links from `DEVICE_DOMAIN_NAME`. Open them at `http://umbrel.local:<Port>`, or change the hostname part of the URL in their compose file.
- GPU not used by Lemonade: make sure the app was installed after the `GPU` permission was added, then check Netdata's GPU section while a model is loaded. To try ROCm, choose it in Lemonade's settings.
"""
    (out / "README.md").write_text(readme)

    # ---------------- docs ----------------
    docs = out / "docs"
    docs.mkdir(exist_ok=True)
    cat_rows = [[f"`{c['id']}`", c["group"], c["status"], c["port"], "<br>".join(f"`{i}`" for i in c["images"]), c["note"]]
                for c in sorted(catalog, key=lambda c: (GROUP_ORDER.index(c["group"]), c["id"]))]
    (docs / "CATALOG.md").write_text("# Catalog with pinned images\n\nEvery image is pinned as `name:tag@sha256:<multi-arch index digest>`, resolved on 2026-09-25.\n\n"
                                     + table(cat_rows, ["App id", "Group", "Status", "Port", "Images", "Note"]) + "\n")

    w = ["# Install waves for a 16 GB Umbrel\n",
         "RAM figures are rough planning estimates, not measurements. Keep total steady-state use under about 10 GB so umbrelOS and the page cache have room. Stop apps you are not using.\n"]
    for title, ids, note in WAVES:
        w.append(f"## {title}\n\n{note}\n")
        w.append(table([[f"`{i}`", by[i]["name"], by[i]["port"], f"{RAM.get(i, 0):.1f} GB"] for i in ids], ["App id", "Name", "Port", "Approx. RAM"]) + "\n")
        w.append(f"Wave total about {sum(RAM.get(i, 0) for i in ids):.1f} GB.\n")
    w.append("## Host ports published outside the Umbrel gateway\n\n" + table(
        [[f"`{c['id']}`", ", ".join(str(p) for p in c["published"])] for c in catalog if c["published"]], ["App id", "Host ports"]) +
        "\n\nThese are DICOM, HL7 MLLP and OIE Administrator ports. They bypass the umbrelOS login, so keep the Umbrel on a trusted network.\n")
    (docs / "INSTALL-WAVES.md").write_text("\n".join(w))

    (docs / "CORRECTIONS.md").write_text(CORRECTIONS)

    # ---------------- tooling ----------------
    tools = out / ".tools"
    tools.mkdir(exist_ok=True)
    shutil.copy(audit_dir / "audit_umbrel_store.py", tools / "audit_umbrel_store.py")
    shutil.copy(audit_dir / "official_ports.json", tools / "official_ports.json")
    (tools / "audit_umbrel_store.py").chmod(0o755)
    wf = out / ".github" / "workflows"
    wf.mkdir(parents=True, exist_ok=True)
    shutil.copy(audit_dir / "ci" / "umbrel-store-audit.yml", wf / "umbrel-store-audit.yml")
    (out / ".gitignore").write_text("__pycache__/\n*.pyc\n.DS_Store\n")


CORRECTIONS = """# Corrections applied to the 48-app scaffold

Each rule comes from the umbrelOS store audit (umbreld 2.0.0 source). The left column is the failure mode the audit checks for; the right column is how this rebuilt store handles it. Because the original archive was not available, this lists the audit rules rather than a line-by-line diff of the old files.

## Store layout and identity

| Failure mode | How this store handles it |
|---|---|
| App folders nested under a subfolder, so umbreld's `*/umbrel-app.yml` glob found nothing | All 48 app folders sit at the repository root |
| No `umbrel-app-store.yml` store file | `umbrel-app-store.yml` with `id: "saud"` and `name: "Saud"` |
| Ids without the store prefix, or not matching the folder | Every id is `saud-<app>` and equals its folder name |
| Ids that collide with official apps | No id collides; the 16 official duplicates are renamed `saud-<id>` and disabled |

## Manifest

| Failure mode | How this store handles it |
|---|---|
| Missing required fields | Every manifest has manifestVersion, id, name, tagline, icon, category, version, port, description, developer, website, submitter, submission, repo, support, gallery, releaseNotes, dependencies, path, defaultUsername, defaultPassword |
| Unquoted versions (YAML turns `1.10` into `1.1`) | `version` is always quoted and matches the upstream release |
| Non-standard categories | Lowercase official categories only (ai, developer, files, media, social) |
| Placeholder or shared passwords | `deterministicPassword: true` and `${APP_PASSWORD}`, shown per device in umbrelOS |

## Icons

| Failure mode | How this store handles it |
|---|---|
| Relative icon paths and svgur.com links (404) | Absolute URLs, each checked for HTTP 200 and an image content type |
| Mutable URLs (branch names) | Official-store duplicates use the umbrel-apps-gallery at commit `7655ed8`; others use dashboard-icons via jsDelivr at commit `ab52e3b`, or upstream repository files at a fixed commit. The Orthanc, HAPI FHIR, Synthea and H5P icons are GitHub organisation avatars because those projects have no suitable logo file |
| Gallery entries pointing at missing files | `gallery: []` |

## Ports

| Failure mode | How this store handles it |
|---|---|
| Duplicate or reserved ports (80, 443, 2000, 40000-49999) | Unique manifest ports from 5401 upward, skipping every port used by an official app |
| DICOM and HL7 ports shared between apps | Unique host ports: DICOM 14242-14246, OIE Administrator 18443, MLLP 6661 |

## docker-compose

| Failure mode | How this store handles it |
|---|---|
| `app_proxy` with image, ports or extra keys | `app_proxy` has only `environment`: `APP_HOST: saud-<app>_<service>_1`, `APP_PORT`, and `PROXY_AUTH_ADD: "false"` only where the app has its own login |
| Floating tags (`latest`, major-only) | Every image is `name:tag@sha256:<multi-arch index digest>` |
| Missing restart policy | `restart: on-failure` on every long-running service; one-shot init containers use `restart: "no"` |
| Named volumes and root-owned bind mounts | Data under `${APP_DATA_DIR}/data/...`, with each folder committed as `.gitkeep` so it exists owned by 1000:1000 |
| Containers that run as another user (pgAdmin 5050, Lemonade, OIE, LimeSurvey, Moodle, GlitchTip, Superset, OpenMRS 1001) | A one-shot `init`/`perms` container fixes ownership; the main service waits with `condition: service_completed_successfully` |
| Sidecars addressed by short names such as `db`, which collide on the shared Umbrel network | Sidecars are addressed by container name (`saud-<app>_db_1`). OpenMRS, whose gateway hard-codes `frontend` and `backend`, runs on a private network |
| Manual `/dev/dri` device mappings | `permissions: [GPU]` in the Lemonade manifest; umbreld adds /dev/dri, /dev/kfd and the right groups |
| Config files that never reach installed apps on update | The Orthanc Lua script lives in the compose file as an inline `configs:` entry; other apps are configured by environment variables |
| Hard-coded secrets | `${APP_PASSWORD}` and `${APP_SEED}` from umbrelOS |

## Scope changes

| App | Change |
|---|---|
| Sentry | Replaced by GlitchTip (Sentry SDK compatible) |
| Dify | Disabled with an explanation; run upstream compose as a stack |
| H5P | Disabled; built into Moodle |
| GitHub Actions runner | Disabled until a repository URL and token are set |
| Synthea | The 2016 Docker image is replaced by the pinned Synthea 4.0.0 release jar (SHA-256 checked) run on Eclipse Temurin 21, with File Browser for the output |
| DuckDB | JupyterLab (docker-stacks `scipy-notebook` 2026-09-21) with DuckDB 1.5.5 installed into the persistent home folder |
| PostgreSQL UI | pgweb 0.17.0 behind the umbrelOS login |
| Netdata | The Docker socket mount was removed (the official linter forbids it); container names may show as IDs |

## Known policy exception

`saud-dozzle` mounts the Docker socket read-only because a log viewer cannot work without it. The official umbrel-apps linter rejects this for the official store; umbreld itself installs it. Remove Dozzle if you do not want any app to see the Docker API.
"""
