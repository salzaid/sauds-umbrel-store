# Corrections applied to the 48-app scaffold

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
