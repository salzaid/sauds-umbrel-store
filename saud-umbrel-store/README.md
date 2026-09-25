# Saud community app store for umbrelOS

A personal community app store for umbrelOS with 48 app folders: 29 packaged apps, 3 disabled placeholders and 16 disabled mirrors of apps that already exist in the official Umbrel App Store.

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

| Group | App id | Name | Version | Port | Status | Notes |
|---|---|---|---|---|---|---|
| Operations | `saud-backrest` | Backrest | 1.14.1 | 5403 | Packaged |  |
| Operations | `saud-dozzle` | Dozzle | 11.1.1 | 5401 | Packaged |  |
| Operations | `saud-grafana` | Grafana | 13.2.2-patch.1 | 5436 | Disabled mirror: install the official app |  |
| Operations | `saud-netdata` | Netdata | 2.11.1 | 5402 | Packaged |  |
| Operations | `saud-portainer` | Portainer | 2.45.1 | 5433 | Disabled mirror: install the official app |  |
| Operations | `saud-uptime-kuma` | Uptime Kuma | 2.5.5 | 5434 | Disabled mirror: install the official app |  |
| AI | `saud-dify` | Dify | 1.17.1 | 5406 | Disabled (see note) |  |
| AI | `saud-flowise` | Flowise | 3.1.4 | 5405 | Packaged |  |
| AI | `saud-langflow` | Langflow | 1.12.3 | 5435 | Disabled mirror: install the official app |  |
| AI | `saud-lemonade` | Lemonade Server | 2026.39.1 | 5404 | Packaged | GPU |
| AI | `saud-litellm` | LiteLLM Proxy | 1.83.14 | 5408 | Packaged |  |
| AI | `saud-qdrant` | Qdrant | 1.19.1 | 5407 | Packaged |  |
| Analytics | `saud-duckdb` | DuckDB Lab | 2026-09-21 | 5412 | Packaged |  |
| Analytics | `saud-jupyterlab` | JupyterLab | v4.6.3-patch.2 | 5437 | Disabled mirror: install the official app |  |
| Analytics | `saud-metabase` | Metabase | 0.63.18.2 | 5410 | Packaged |  |
| Analytics | `saud-pgadmin` | pgAdmin | 9.18 | 5413 | Packaged |  |
| Analytics | `saud-postgresql` | PostgreSQL | 16.15 | 5409 | Packaged |  |
| Analytics | `saud-superset` | Apache Superset | 6.1.0 | 5411 | Packaged |  |
| Imaging | `saud-dicom-deid` | DICOM De-identifier | 26.9.1 | 5418 | Packaged | host ports 14246 |
| Imaging | `saud-ohif-viewer` | OHIF Viewer | 26.9.1 | 5417 | Packaged | host ports 14245 |
| Imaging | `saud-orthanc-lab-basic` | Orthanc Lab | 26.9.1 | 5414 | Packaged | host ports 14242 |
| Imaging | `saud-orthanc-research-archive` | Orthanc Research Archive | 26.9.1 | 5416 | Packaged | host ports 14244 |
| Imaging | `saud-orthanc-research-viewer` | Orthanc Research Viewer | 26.9.1 | 5415 | Packaged | host ports 14243 |
| Documents | `saud-bookstack` | BookStack | 26.09 | 5441 | Disabled mirror: install the official app |  |
| Documents | `saud-hedgedoc` | HedgeDoc | 1.12.0 | 5420 | Packaged |  |
| Documents | `saud-nextcloud` | Nextcloud | 35.0.0 | 5438 | Disabled mirror: install the official app |  |
| Documents | `saud-onlyoffice` | ONLYOFFICE Docs | 9.4.0.1 | 5419 | Packaged |  |
| Documents | `saud-outline` | Outline | 1.7.1 | 5440 | Disabled mirror: install the official app |  |
| Interoperability | `saud-fhir-validator` | FHIR Validator | 1.0.84 | 5423 | Packaged |  |
| Interoperability | `saud-hapi-fhir` | HAPI FHIR Server | 8.12.0 | 5422 | Packaged |  |
| Interoperability | `saud-oie` | Open Integration Engine | 4.5.2 | 5421 | Packaged | host ports 18443, 6661 |
| Interoperability | `saud-openemr` | OpenEMR | 8.4.1 | 5425 | Packaged |  |
| Interoperability | `saud-openmrs` | OpenMRS 3 | 3.7.1 | 5426 | Packaged |  |
| Interoperability | `saud-synthea` | Synthea | 4.0.0 | 5424 | Packaged |  |
| Education | `saud-h5p` | H5P | 1.0.0 | 5429 | Disabled (see note) |  |
| Education | `saud-limesurvey` | LimeSurvey | 7.1.2 | 5427 | Packaged |  |
| Education | `saud-moodle` | Moodle | 5.2.3 | 5428 | Packaged |  |
| Development | `saud-appsmith` | Appsmith | v2.4.2 | 5447 | Disabled mirror: install the official app |  |
| Development | `saud-baserow` | Baserow | 2.3.4 | 5430 | Packaged |  |
| Development | `saud-code-server` | code-server | 4.138.0 | 5443 | Disabled mirror: install the official app |  |
| Development | `saud-forgejo` | Forgejo | 16.0.5 | 5445 | Disabled mirror: install the official app |  |
| Development | `saud-gitea` | Gitea | 1.27.3-patch.1 | 5444 | Disabled mirror: install the official app |  |
| Development | `saud-github-actions-runner` | GitHub Actions Runner | 2.337.0 | 5432 | Disabled (see note) |  |
| Development | `saud-glitchtip` | GlitchTip (Sentry-compatible) | 6.2.6 | 5431 | Packaged |  |
| Development | `saud-mattermost` | Mattermost | 11.11.0 | 5442 | Disabled mirror: install the official app |  |
| Development | `saud-minio` | MinIO | RELEASE.2025-06-13T11-33-47Z-patch.1 | 5446 | Disabled mirror: install the official app |  |
| Development | `saud-nocodb` | NocoDB | 2026.09.0-patch.1 | 5448 | Disabled mirror: install the official app |  |
| Development | `saud-vikunja` | Vikunja | 2.6.0-patch.1 | 5439 | Disabled mirror: install the official app |  |

Open an app at `http://umbrel.local:<Port>`. Where an app shows a password in umbrelOS, it is derived from your device and is stable across reinstalls on the same Umbrel.

## Why some apps are disabled

- The 16 mirrors duplicate apps in the official store (Portainer, Uptime Kuma, Langflow, Grafana, JupyterLab, Nextcloud, Vikunja, Outline, BookStack, Mattermost, code-server, Gitea, Forgejo, MinIO, Appsmith, NocoDB). Install those from the official store, which keeps them updated. The mirrors are copies of the official packages with renamed ids, container names and ports, kept so the catalog is complete.
- `saud-dify`: Dify 1.17 needs about ten containers with fixed service names and many env files. It cannot be packaged reliably without hardware testing. Run it as a Portainer stack with the upstream compose file, or use Flowise.
- `saud-h5p`: H5P has no maintained stand-alone server. It is built into Moodle.
- `saud-github-actions-runner`: needs a repository URL and token and has no web page. See its description to enable it.
- Sentry is replaced by `saud-glitchtip`, which accepts Sentry SDKs. Self-hosted Sentry needs 20+ containers and far more memory than this machine has spare.

## Corrections applied

See [docs/CORRECTIONS.md](docs/CORRECTIONS.md) for the full list. In short: app folders sit at the repository root with `saud-` ids that match their folder names; every manifest is complete with a quoted version; icons are absolute, pinned URLs that were checked to return an image; ports are unique and avoid official apps; every image is pinned to a multi-architecture digest; data lives under `${APP_DATA_DIR}/data` with the folders committed; non-1000 containers get a one-shot ownership fix; GPU access uses the `GPU` permission instead of device mappings; and config files live inside `docker-compose.yml` so they update with the app.

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
