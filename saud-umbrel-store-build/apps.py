# App specifications for the Saud community app store (reconstruction).
# Each custom app: dict with manifest fields + compose services (Python dicts).
# Placeholders: {ID} -> app id, {PORT} -> manifest port, IMG('ref') -> pinned image.

DH = "https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons@ab52e3bfaa737cba86793c76ccfcb312f8841278"
def di(name, ext="svg"):
    return f"{DH}/{ext}/{name}.{ext}"
def gh(repo, sha, path):
    return f"https://raw.githubusercontent.com/{repo}/{sha}/{path}"

ICON_ORTHANC = "https://avatars.githubusercontent.com/orthanc-team?s=256"

# Shared images
PG = "postgres:16.15"
MARIADB = "mariadb:11.8.9"
BUSYBOX = "busybox:1.38.0"


def pg_service(app, db, user, extra=None):
    s = {
        "image": PG,
        "user": "1000:1000",
        "restart": "on-failure",
        "stop_grace_period": "1m",
        "volumes": ["${APP_DATA_DIR}/data/db:/var/lib/postgresql/data"],
        "environment": {
            "POSTGRES_DB": db,
            "POSTGRES_USER": user,
            "POSTGRES_PASSWORD": "${APP_PASSWORD}",
        },
        "healthcheck": {
            "test": ["CMD-SHELL", f"pg_isready -U {user} -d {db}"],
            "interval": "10s", "timeout": "5s", "retries": 10,
        },
    }
    if extra:
        s.update(extra)
    return s


def mariadb_service(db, user, image=MARIADB):
    return {
        "image": image,
        "user": "1000:1000",
        "restart": "on-failure",
        "stop_grace_period": "1m",
        "command": "--character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci",
        "volumes": ["${APP_DATA_DIR}/data/db:/var/lib/mysql"],
        "environment": {
            "MARIADB_DATABASE": db,
            "MARIADB_USER": user,
            "MARIADB_PASSWORD": "${APP_PASSWORD}",
            "MARIADB_ROOT_PASSWORD": "${APP_PASSWORD}",
        },
        "healthcheck": {
            "test": ["CMD", "healthcheck.sh", "--connect", "--innodb_initialized"],
            "interval": "10s", "timeout": "5s", "retries": 20,
        },
    }


def chown_init(owner, paths, image=BUSYBOX, as_root_same_image=False):
    """One-shot init container that fixes ownership of bind mounts.
    owner: 'uid:gid' (busybox) or 'user:group' (same image run as root)."""
    vols = [f"${{APP_DATA_DIR}}/data/{h}:{c}" for h, c in paths]
    cmd = ["chown", "-R", owner] + [c for _, c in paths]
    s = {"image": image, "user": "0:0", "restart": "no", "entrypoint": cmd, "volumes": vols}
    return s


def dep_ok(*names, healthy=()):
    d = {}
    for n in names:
        d[n] = {"condition": "service_completed_successfully"}
    for n in healthy:
        d[n] = {"condition": "service_healthy"}
    return d


def orthanc_env(name, aet, extra=None):
    e = {
        "ORTHANC__NAME": name,
        "ORTHANC__DICOM_AET": aet,
        "ORTHANC__DICOM_PORT": "4242",
        "ORTHANC__AUTHENTICATION_ENABLED": "false",
        "ORTHANC__REMOTE_ACCESS_ALLOWED": "true",
        "ORTHANC__DICOM_ALWAYS_ALLOW_STORE": "true",
        "ORTHANC__DICOM_CHECK_CALLED_AET": "false",
        "ORTHANC__STORAGE_DIRECTORY": "/var/lib/orthanc/db",
        "VERBOSE_STARTUP": "true",
    }
    if extra:
        e.update(extra)
    return e


DEID_LUA = r'''-- Auto de-identification for saud-dicom-deid (Orthanc Lua).
-- When a study becomes stable, anonymize it with the DICOM PS3.15 basic profile,
-- keep the anonymized copy, and delete the identifiable original.
function OnStableStudy(studyId, tags, metadata)
  if metadata['AnonymizedFrom'] ~= nil then
    return
  end
  local body = {}
  body['Force'] = true
  body['KeepPrivateTags'] = false
  body['DicomVersion'] = '2023b'
  body['Replace'] = {}
  body['Replace']['PatientName'] = 'DEID^' .. string.sub(studyId, 1, 8)
  body['Replace']['PatientID'] = 'DEID-' .. string.sub(studyId, 1, 8)
  local result = ParseJson(RestApiPost('/studies/' .. studyId .. '/anonymize', DumpJson(body, true)))
  if result ~= nil and result['ID'] ~= nil then
    RestApiDelete('/studies/' .. studyId)
    print('saud-dicom-deid: anonymized ' .. studyId .. ' -> ' .. result['ID'])
  end
end
'''

INFO_PAGE = '''<!doctype html><html><head><meta charset="utf-8"><title>{title}</title>
<style>body{{font-family:system-ui,sans-serif;max-width:40rem;margin:4rem auto;padding:0 1rem;line-height:1.5;color:#222}}code{{background:#f2f2f2;padding:.1rem .3rem}}</style>
</head><body><h1>{title}</h1>{body}</body></html>
'''

def info_page_service(title, body_html):
    html = INFO_PAGE.format(title=title, body=body_html).replace("$", "$$")
    return {
        "image": BUSYBOX,
        "user": "1000:1000",
        "restart": "on-failure",
        "command": ["sh", "-c", "mkdir -p /tmp/www && cat > /tmp/www/index.html <<'EOF'\n" + html + "EOF\nexec httpd -f -p 8080 -h /tmp/www"],
    }


# ---------------------------------------------------------------------------
# 32 custom apps
# ---------------------------------------------------------------------------
CUSTOM = []

def app(**kw):
    CUSTOM.append(kw)
    return kw

# ---------------- Operations ----------------
app(slug="dozzle", name="Dozzle", category="developer", version="11.1.1",
    tagline="Real-time log viewer for your Docker containers",
    description="Dozzle streams the logs of every container on your Umbrel in the browser. It is read-only: it mounts the Docker socket read-only and does not store logs.\n\nUse it to troubleshoot app installs from this store.",
    developer="Amir Raminfar", website="https://dozzle.dev", repo="https://github.com/amir20/dozzle",
    support="https://github.com/amir20/dozzle/issues", icon=di("dozzle"),
    main="web", app_port=8080,
    services={"web": {"image": "amir20/dozzle:v11.1.1", "restart": "on-failure",
        "volumes": ["/var/run/docker.sock:/var/run/docker.sock:ro"],
        "environment": {"DOZZLE_NO_ANALYTICS": "true", "DOZZLE_ENABLE_ACTIONS": "false"}}},
    group="Operations")

app(slug="netdata", name="Netdata", category="developer", version="2.11.1",
    tagline="Per-second health and performance monitoring",
    description="Netdata collects per-second metrics for CPU, memory, disks, network, containers and GPU on your Umbrel and shows them in live dashboards.\n\nCloud features are optional and disabled by default.",
    developer="Netdata Inc.", website="https://www.netdata.cloud", repo="https://github.com/netdata/netdata",
    support="https://github.com/netdata/netdata/issues", icon=di("netdata"),
    main="web", app_port=19999, data_dirs=["config", "lib", "cache"],
    services={"web": {"image": "netdata/netdata:v2.11.1", "restart": "on-failure",
        "hostname": "umbrel-netdata", "pid": "host",
        "cap_add": ["SYS_PTRACE", "SYS_ADMIN"], "security_opt": ["apparmor:unconfined"],
        "environment": {"DO_NOT_TRACK": "1", "NETDATA_DISABLE_CLOUD": "1"},
        "volumes": ["${APP_DATA_DIR}/data/config:/etc/netdata", "${APP_DATA_DIR}/data/lib:/var/lib/netdata",
                    "${APP_DATA_DIR}/data/cache:/var/cache/netdata",
                    "/etc/passwd:/host/etc/passwd:ro", "/etc/group:/host/etc/group:ro",
                    "/etc/localtime:/etc/localtime:ro", "/proc:/host/proc:ro", "/sys:/host/sys:ro",
                    "/etc/os-release:/host/etc/os-release:ro"]}},
    group="Operations")

app(slug="backrest", name="Backrest", category="files", version="1.14.1",
    tagline="Web UI and scheduler for restic backups",
    description="Backrest is a web interface for restic. It schedules snapshots, prunes old ones and lets you browse and restore files.\n\nYour Umbrel home folder is mounted read-only at /userdata. Local repositories can be created under /repos, but keep at least one copy off the device.",
    developer="Gareth George", website="https://garethgeorge.github.io/backrest", repo="https://github.com/garethgeorge/backrest",
    support="https://github.com/garethgeorge/backrest/issues", icon=di("backrest"),
    main="web", app_port=9898, data_dirs=["data", "config", "cache", "repos"],
    services={"web": {"image": "garethgeorge/backrest:v1.14.1", "restart": "on-failure",
        "hostname": "umbrel-backrest",
        "environment": {"BACKREST_PORT": "0.0.0.0:9898", "BACKREST_DATA": "/data",
                        "BACKREST_CONFIG": "/config/config.json", "XDG_CACHE_HOME": "/cache", "TMPDIR": "/tmp"},
        "volumes": ["${APP_DATA_DIR}/data/data:/data", "${APP_DATA_DIR}/data/config:/config",
                    "${APP_DATA_DIR}/data/cache:/cache", "${APP_DATA_DIR}/data/repos:/repos",
                    "${UMBREL_ROOT}/home:/userdata:ro"]}},
    no_proxy_auth=True, group="Operations")

# ---------------- AI ----------------
LEM_PATHS = [("hf", "/opt/lemonade/.cache/huggingface"), ("llama", "/opt/lemonade/llama"),
             ("cache", "/opt/lemonade/.cache/lemonade"), ("config", "/opt/lemonade/.config/lemonade")]
LEM_IMG = "ghcr.io/lemonade-sdk/lemonade-server:v2026.39.1"
app(slug="lemonade", name="Lemonade Server", category="ai", version="2026.39.1",
    tagline="Local LLM server with an OpenAI-compatible API and AMD GPU acceleration",
    description="Lemonade runs large language models locally with llama.cpp and exposes an OpenAI-compatible API at /api/v1.\n\nThis package requests GPU access, so umbrelOS passes /dev/dri and /dev/kfd to the container automatically. Vulkan works out of the box on Radeon RX 7000 cards; ROCm can be selected in Settings.\n\nOther Umbrel apps can reach the API at http://saud-lemonade_server_1:13305/api/v1.",
    developer="Lemonade SDK", website="https://lemonade-server.ai", repo="https://github.com/lemonade-sdk/lemonade",
    support="https://github.com/lemonade-sdk/lemonade/issues",
    icon=gh("lemonade-sdk/lemonade", "6deeb05f77", "docs/assets/logo_512.png"),
    main="server", app_port=13305, data_dirs=[p for p, _ in LEM_PATHS], permissions=["GPU"],
    services={
        "init": chown_init("lemonade:lemonade", LEM_PATHS, image=LEM_IMG),
        "server": {"image": LEM_IMG, "restart": "on-failure",
            "depends_on": dep_ok("init"),
            "volumes": [f"${{APP_DATA_DIR}}/data/{h}:{c}" for h, c in LEM_PATHS]}},
    group="AI")

app(slug="flowise", name="Flowise", category="ai", version="3.1.4",
    tagline="Build LLM agents and RAG flows visually",
    description="Flowise is a drag-and-drop builder for LLM chains, agents and retrieval pipelines. Point it at Lemonade (http://saud-lemonade_server_1:13305/api/v1) or Qdrant (http://saud-qdrant_web_1:6333) from this store.\n\nCreate the admin account on first launch.",
    developer="FlowiseAI", website="https://flowiseai.com", repo="https://github.com/FlowiseAI/Flowise",
    support="https://github.com/FlowiseAI/Flowise/issues", icon=di("flowise"),
    main="web", app_port=3000, data_dirs=["flowise"],
    services={"web": {"image": "flowiseai/flowise:3.1.4", "user": "1000:1000", "restart": "on-failure",
        "environment": {"PORT": "3000", "DATABASE_PATH": "/home/node/.flowise", "SECRETKEY_PATH": "/home/node/.flowise",
                        "LOG_PATH": "/home/node/.flowise/logs", "BLOB_STORAGE_PATH": "/home/node/.flowise/storage",
                        "DISABLE_FLOWISE_TELEMETRY": "true"},
        "volumes": ["${APP_DATA_DIR}/data/flowise:/home/node/.flowise"]}},
    group="AI")

app(slug="dify", name="Dify", category="ai", version="1.17.1",
    tagline="LLM app platform (not packaged here, see description)",
    description="Dify 1.17 needs about ten cooperating containers (API, worker, beat, web, sandbox, plugin daemon, SSRF proxy, nginx, vector store, database, cache) with hard-coded service names and many env files. That cannot be packaged reliably as an Umbrel app without testing on hardware.\n\nThis entry is disabled. Run Dify with its own docker compose files, for example as a Portainer stack, or use Flowise from this store.",
    developer="LangGenius", website="https://dify.ai", repo="https://github.com/langgenius/dify",
    support="https://github.com/langgenius/dify/issues",
    icon=gh("langgenius/dify", "d86435ee1e69b5badef832baf785863ea99bfbd7", "web/public/logo/logo.svg"),
    main="web", app_port=8080, disabled=True,
    services={"web": info_page_service("Dify is not packaged in this store",
        "<p>Dify needs about ten containers and is not packaged here. Deploy it with the upstream <code>docker/docker-compose.yaml</code> as a Portainer stack, or use Flowise.</p>")},
    group="AI")

app(slug="qdrant", name="Qdrant", category="ai", version="1.19.1",
    tagline="Vector database for retrieval-augmented generation",
    description="Qdrant stores embeddings and runs fast similarity search. The web dashboard is at /dashboard.\n\nThe API key is the password shown for this app in umbrelOS. Other apps connect to http://saud-qdrant_web_1:6333 with header api-key.",
    developer="Qdrant", website="https://qdrant.tech", repo="https://github.com/qdrant/qdrant",
    support="https://github.com/qdrant/qdrant/issues", icon=di("qdrant"),
    main="web", app_port=6333, path="/dashboard", data_dirs=["storage", "snapshots"],
    default_password=True,
    services={"web": {"image": "qdrant/qdrant:v1.19.1", "restart": "on-failure",
        "environment": {"QDRANT__SERVICE__API_KEY": "${APP_PASSWORD}", "QDRANT__TELEMETRY_DISABLED": "true"},
        "volumes": ["${APP_DATA_DIR}/data/storage:/qdrant/storage", "${APP_DATA_DIR}/data/snapshots:/qdrant/snapshots"]}},
    group="AI")

app(slug="litellm", name="LiteLLM Proxy", category="ai", version="1.83.14",
    tagline="One OpenAI-compatible gateway in front of all your model providers",
    description="LiteLLM Proxy routes OpenAI-format requests to local and cloud models, with keys, budgets and logging. Models are managed in the admin UI at /ui and stored in the bundled PostgreSQL.\n\nLog in with username admin and the password shown in umbrelOS. The master API key is sk- followed by that password.",
    developer="BerriAI", website="https://www.litellm.ai", repo="https://github.com/BerriAI/litellm",
    support="https://github.com/BerriAI/litellm/issues",
    icon=gh("BerriAI/litellm", "c19ce71bcdad234ca87a7af10cee45375ce811a8", "litellm/proxy/swagger/favicon.png"),
    main="proxy", app_port=4000, path="/ui", data_dirs=["db"], default_username="admin", default_password=True,
    services={
        "proxy": {"image": "litellm/litellm:v1.83.14-stable.patch.3", "restart": "on-failure",
            "depends_on": dep_ok(healthy=["db"]),
            "environment": {"DATABASE_URL": "postgresql://litellm:${APP_PASSWORD}@saud-litellm_db_1:5432/litellm",
                            "LITELLM_MASTER_KEY": "sk-${APP_PASSWORD}", "UI_USERNAME": "admin", "UI_PASSWORD": "${APP_PASSWORD}",
                            "STORE_MODEL_IN_DB": "True", "LITELLM_TELEMETRY": "False"}},
        "db": pg_service("litellm", "litellm", "litellm")},
    no_proxy_auth=True, group="AI")

# ---------------- Analytics ----------------
app(slug="postgresql", name="PostgreSQL", category="developer", version="16.15",
    tagline="Shared PostgreSQL 16 server with a web SQL console",
    description="A PostgreSQL 16 server for registry and analytics work, with pgweb as a browser-based SQL console.\n\nOther apps connect to host saud-postgresql_db_1, port 5432, user postgres, and the password shown in umbrelOS. The server is not published on the LAN by default.",
    developer="PostgreSQL Global Development Group", website="https://www.postgresql.org", repo="https://github.com/postgres/postgres",
    support="https://www.postgresql.org/support/", icon=di("postgresql"),
    main="web", app_port=8081, data_dirs=["db"], default_username="postgres", default_password=True,
    services={
        "db": pg_service("postgresql", "postgres", "postgres"),
        "web": {"image": "sosedoff/pgweb:0.17.0", "restart": "on-failure", "depends_on": dep_ok(healthy=["db"]),
            "environment": {"PGWEB_DATABASE_URL": "postgres://postgres:${APP_PASSWORD}@saud-postgresql_db_1:5432/postgres?sslmode=disable"}}},
    group="Analytics")

app(slug="metabase", name="Metabase", category="developer", version="0.63.18.2",
    tagline="Dashboards and questions on your registry data",
    description="Metabase turns SQL databases into charts and dashboards. Its own settings live in a bundled PostgreSQL.\n\nAdd saud-postgresql_db_1 (port 5432) as a data source to analyse registry or TQIP extracts. Create the admin account on first launch.",
    developer="Metabase", website="https://www.metabase.com", repo="https://github.com/metabase/metabase",
    support="https://github.com/metabase/metabase/issues", icon=di("metabase"),
    main="web", app_port=3000, data_dirs=["db"],
    services={
        "web": {"image": "metabase/metabase:v0.63.18.2", "restart": "on-failure", "depends_on": dep_ok(healthy=["db"]),
            "environment": {"MB_DB_TYPE": "postgres", "MB_DB_DBNAME": "metabase", "MB_DB_PORT": "5432",
                            "MB_DB_USER": "metabase", "MB_DB_PASS": "${APP_PASSWORD}", "MB_DB_HOST": "saud-metabase_db_1",
                            "MB_ANON_TRACKING_ENABLED": "false", "MB_CHECK_FOR_UPDATES": "false", "JAVA_TIMEZONE": "Asia/Kuwait"}},
        "db": pg_service("metabase", "metabase", "metabase")},
    group="Analytics")

SUP_IMG = "apache/superset:6.1.0"
app(slug="superset", name="Apache Superset", category="developer", version="6.1.0",
    tagline="Open-source business intelligence and data exploration",
    description="Superset explores SQL data with charts, dashboards and a SQL Lab. Metadata is stored in SQLite inside the app data folder, which is enough for single-user use.\n\nLog in as admin with the password shown in umbrelOS.",
    developer="Apache Software Foundation", website="https://superset.apache.org", repo="https://github.com/apache/superset",
    support="https://github.com/apache/superset/issues", icon=di("apache-superset"),
    main="web", app_port=8088, data_dirs=["home"], default_username="admin", default_password=True,
    services={
        "perms": chown_init("superset:superset", [("home", "/app/superset_home")], image=SUP_IMG),
        "init": {"image": SUP_IMG, "restart": "no", "depends_on": dep_ok("perms"),
            "environment": {"SUPERSET_SECRET_KEY": "${APP_SEED}"},
            "volumes": ["${APP_DATA_DIR}/data/home:/app/superset_home"],
            "command": ["sh", "-c", "superset db upgrade && (superset fab create-admin --username admin --firstname Admin --lastname User --email admin@example.com --password ${APP_PASSWORD} || true) && superset init"]},
        "web": {"image": SUP_IMG, "restart": "on-failure", "depends_on": dep_ok("init"),
            "environment": {"SUPERSET_SECRET_KEY": "${APP_SEED}"},
            "volumes": ["${APP_DATA_DIR}/data/home:/app/superset_home"]}},
    no_proxy_auth=True, group="Analytics")

app(slug="duckdb", name="DuckDB Lab", category="developer", version="2026-09-21",
    tagline="JupyterLab with DuckDB for fast local analytics",
    description="A JupyterLab notebook server with DuckDB, JupySQL and pandas, for analysing CSV and Parquet extracts locally.\n\nThe Python packages are installed into your persistent home folder on first start, which takes a few minutes. Access is protected by the umbrelOS login.",
    developer="Project Jupyter / DuckDB Foundation", website="https://duckdb.org", repo="https://github.com/jupyter/docker-stacks",
    support="https://github.com/jupyter/docker-stacks/issues",
    icon=gh("duckdb/duckdb", "ca15f79c32", "logo/DuckDB_Logo-stacked.svg"),
    main="lab", app_port=8888, data_dirs=["home"],
    services={"lab": {"image": "quay.io/jupyter/scipy-notebook:2026-09-21", "user": "1000:100", "restart": "on-failure",
        "environment": {"JUPYTER_ENABLE_LAB": "yes"},
        "volumes": ["${APP_DATA_DIR}/data/home:/home/jovyan"],
        "command": ["bash", "-c", "pip install --user --quiet --disable-pip-version-check duckdb==1.5.5 jupysql duckdb-engine && exec start-notebook.py --IdentityProvider.token='' --ServerApp.password='' --ServerApp.allow_origin='*'"]}},
    group="Analytics")

app(slug="pgadmin", name="pgAdmin", category="developer", version="9.18",
    tagline="Full PostgreSQL administration in the browser",
    description="pgAdmin 4 manages PostgreSQL servers, including saud-postgresql_db_1 from this store.\n\nLog in with admin@example.com and the password shown in umbrelOS.",
    developer="pgAdmin Development Team", website="https://www.pgadmin.org", repo="https://github.com/pgadmin-org/pgadmin4",
    support="https://github.com/pgadmin-org/pgadmin4/issues", icon=di("pgadmin"),
    main="web", app_port=80, data_dirs=["pgadmin"], default_username="admin@example.com", default_password=True,
    services={
        "init": chown_init("5050:5050", [("pgadmin", "/var/lib/pgadmin")]),
        "web": {"image": "dpage/pgadmin4:9.18.0", "restart": "on-failure", "depends_on": dep_ok("init"),
            "environment": {"PGADMIN_DEFAULT_EMAIL": "admin@example.com", "PGADMIN_DEFAULT_PASSWORD": "${APP_PASSWORD}",
                            "PGADMIN_DISABLE_POSTFIX": "true", "PGADMIN_CONFIG_UPGRADE_CHECK_ENABLED": "False"},
            "volumes": ["${APP_DATA_DIR}/data/pgadmin:/var/lib/pgadmin"]}},
    no_proxy_auth=True, group="Analytics")

# ---------------- Imaging (Orthanc family) ----------------
ORTHANC_IMG = "orthancteam/orthanc:26.9.1"
ORTH_NOTE = "\n\nFor de-identified or synthetic studies only. Not a clinical PACS."

def orthanc_app(slug, name, tagline, desc, aet, dicom_host_port, env_extra=None, extra_services=None, depends=None, configs=None, data_dirs=("db",)):
    svc = {"image": ORTHANC_IMG, "restart": "on-failure",
           "ports": [f"{dicom_host_port}:4242"],
           "environment": orthanc_env(name, aet, env_extra),
           "volumes": ["${APP_DATA_DIR}/data/db:/var/lib/orthanc/db"]}
    if depends:
        svc["depends_on"] = depends
    if configs:
        svc["configs"] = configs
    services = {"server": svc}
    if extra_services:
        services.update(extra_services)
    return app(slug=slug, name=name, category="media", version="26.9.1", tagline=tagline,
               description=desc + f"\n\nDICOM C-STORE: AE title {aet}, port {dicom_host_port} on your Umbrel." + ORTH_NOTE,
               developer="Orthanc Team", website="https://www.orthanc-server.com", repo="https://github.com/orthanc-team/orthanc-builder",
               support="https://discourse.orthanc-server.org", icon=ICON_ORTHANC,
               main="server", app_port=8042, data_dirs=list(data_dirs), services=services, group="Imaging",
               exports_ports={"DICOM": dicom_host_port})

orthanc_app("orthanc-lab-basic", "Orthanc Lab", "Lightweight DICOM server for teaching and testing",
            "Orthanc with the Orthanc Explorer 2 interface and SQLite storage. Good for a first look at DICOM routing.",
            "SAUDLAB", 14242)
orthanc_app("orthanc-research-viewer", "Orthanc Research Viewer", "DICOM server with DICOMweb and the Stone Web Viewer",
            "Orthanc with DICOMweb and the Stone Web Viewer enabled, for viewing de-identified research studies in the browser.",
            "SAUDVIEW", 14243, env_extra={"DICOM_WEB_PLUGIN_ENABLED": "true", "STONE_WEB_VIEWER_PLUGIN_ENABLED": "true"})
orthanc_app("orthanc-research-archive", "Orthanc Research Archive", "Orthanc with a PostgreSQL index for larger research archives",
            "Orthanc with its index in PostgreSQL (files stay on disk), plus DICOMweb and the Stone Web Viewer. Suited to larger de-identified collections.",
            "SAUDARCH", 14244,
            env_extra={"DICOM_WEB_PLUGIN_ENABLED": "true", "STONE_WEB_VIEWER_PLUGIN_ENABLED": "true",
                       "ORTHANC__POSTGRESQL__HOST": "saud-orthanc-research-archive_db_1", "ORTHANC__POSTGRESQL__PORT": "5432",
                       "ORTHANC__POSTGRESQL__DATABASE": "orthanc", "ORTHANC__POSTGRESQL__USERNAME": "orthanc",
                       "ORTHANC__POSTGRESQL__PASSWORD": "${APP_PASSWORD}", "ORTHANC__POSTGRESQL__ENABLE_INDEX": "true",
                       "ORTHANC__POSTGRESQL__ENABLE_STORAGE": "false"},
            extra_services={"db": pg_service("orthanc", "orthanc", "orthanc", {"volumes": ["${APP_DATA_DIR}/data/pg:/var/lib/postgresql/data"]})},
            depends=dep_ok(healthy=["db"]), data_dirs=("db", "pg"))
orthanc_app("ohif-viewer", "OHIF Viewer", "OHIF zero-footprint viewer served by Orthanc",
            "The OHIF Viewer, served by the Orthanc OHIF plugin with DICOMweb. Open a study from Orthanc Explorer 2 and choose OHIF.",
            "SAUDOHIF", 14245, env_extra={"DICOM_WEB_PLUGIN_ENABLED": "true", "OHIF_PLUGIN_ENABLED": "true",
                                            "ORTHANC__OHIF__DATA_SOURCE": "dicom-web"})
orthanc_app("dicom-deid", "DICOM De-identifier", "Inbox that de-identifies every study it receives",
            "An Orthanc inbox with a Lua script: each study sent to it is anonymized with the DICOM basic profile when it becomes stable, and the identifiable original is deleted. Check results before sharing; burned-in pixel text is not removed.",
            "SAUDDEID", 14246,
            env_extra={"ORTHANC__LUA_SCRIPTS": '["/etc/orthanc/deid.lua"]', "ORTHANC__STABLE_AGE": "30",
                       "ORTHANC__OVERWRITE_INSTANCES": "true"},
            configs=[{"source": "deid_lua", "target": "/etc/orthanc/deid.lua"}])
CUSTOM[-1]["top_configs"] = {"deid_lua": {"content": DEID_LUA.replace("$", "$$")}}

# ---------------- Documents ----------------
app(slug="onlyoffice", name="ONLYOFFICE Docs", category="files", version="9.4.0.1",
    tagline="Document server for editing Word, Excel and PowerPoint files",
    description="ONLYOFFICE Document Server lets Nextcloud and other apps edit office files in the browser. JWT is enabled; the secret is the password shown in umbrelOS.\n\nFrom Nextcloud, set the Document Server address to http://<umbrel-ip>:{PORT} and paste the secret.",
    developer="Ascensio System SIA", website="https://www.onlyoffice.com", repo="https://github.com/ONLYOFFICE/DocumentServer",
    support="https://github.com/ONLYOFFICE/DocumentServer/issues", icon=di("onlyoffice"),
    main="web", app_port=80, data_dirs=["data", "lib", "logs", "db"], default_password=True,
    services={"web": {"image": "onlyoffice/documentserver:9.4.0.1", "restart": "on-failure", "stop_grace_period": "1m",
        "environment": {"JWT_ENABLED": "true", "JWT_SECRET": "${APP_PASSWORD}", "JWT_HEADER": "Authorization"},
        "volumes": ["${APP_DATA_DIR}/data/data:/var/www/onlyoffice/Data", "${APP_DATA_DIR}/data/lib:/var/lib/onlyoffice",
                    "${APP_DATA_DIR}/data/logs:/var/log/onlyoffice", "${APP_DATA_DIR}/data/db:/var/lib/postgresql"]}},
    no_proxy_auth=True, group="Documents")

app(slug="hedgedoc", name="HedgeDoc", category="files", version="1.12.0",
    tagline="Collaborative Markdown notes",
    description="HedgeDoc is a real-time collaborative Markdown editor for meeting notes, protocols and teaching material.\n\nAnonymous notes are off. Register with an email and password on first use. The app must be opened at http://{DOMAIN}:{PORT}.",
    developer="HedgeDoc", website="https://hedgedoc.org", repo="https://github.com/hedgedoc/hedgedoc",
    support="https://github.com/hedgedoc/hedgedoc/issues", icon=di("hedgedoc"),
    main="web", app_port="{PORT}", data_dirs=["uploads", "db"],
    services={
        "web": {"image": "quay.io/hedgedoc/hedgedoc:1.12.0", "restart": "on-failure", "depends_on": dep_ok(healthy=["db"]),
            "environment": {"CMD_DB_URL": "postgres://hedgedoc:${APP_PASSWORD}@saud-hedgedoc_db_1:5432/hedgedoc",
                            "CMD_DOMAIN": "${DEVICE_DOMAIN_NAME}", "CMD_PORT": "{PORT}", "CMD_URL_ADDPORT": "true",
                            "CMD_PROTOCOL_USESSL": "false", "CMD_ALLOW_ANONYMOUS": "false", "CMD_ALLOW_ANONYMOUS_EDITS": "false",
                            "CMD_EMAIL": "true", "CMD_ALLOW_EMAIL_REGISTER": "true", "CMD_SESSION_SECRET": "${APP_SEED}"},
            "volumes": ["${APP_DATA_DIR}/data/uploads:/hedgedoc/public/uploads"]},
        "db": pg_service("hedgedoc", "hedgedoc", "hedgedoc")},
    no_proxy_auth=True, group="Documents")

# ---------------- Interoperability ----------------
OIE_IMG = "openintegrationengine/engine:4.5.2-ubuntu-jre"
OIE_PATHS = [("appdata", "/opt/engine/appdata"), ("extensions", "/opt/engine/custom-extensions")]
app(slug="oie", name="Open Integration Engine", category="developer", version="4.5.2",
    tagline="HL7 v2 and FHIR integration engine (open fork of Mirth Connect)",
    description="Open Integration Engine routes and transforms HL7 v2, FHIR, DICOM and other healthcare messages.\n\nThe browser page links to the Administrator client. Point the client at https://{DOMAIN}:18443 and log in with admin / admin, then change the password. A sample MLLP listener port 6661 is published for test channels.",
    developer="Open Integration Engine", website="https://openintegrationengine.org", repo="https://github.com/OpenIntegrationEngine/engine",
    support="https://github.com/OpenIntegrationEngine/engine/issues",
    icon=gh("OpenIntegrationEngine/engine", "03eefcfe06", "server/public_html/images/oie_logo_bottom_text.svg"),
    main="engine", app_port=8443, app_protocol="https", data_dirs=[p for p, _ in OIE_PATHS],
    default_username="admin", default_password_text="admin",
    services={
        "init": chown_init("engine:engine", OIE_PATHS, image=OIE_IMG),
        "engine": {"image": OIE_IMG, "restart": "on-failure", "depends_on": dep_ok("init"),
            "environment": {"VMOPTIONS": "-Xmx768m"},
            "ports": ["18443:8443", "6661:6661"],
            "volumes": [f"${{APP_DATA_DIR}}/data/{h}:{c}" for h, c in OIE_PATHS]}},
    no_proxy_auth=True, exports_ports={"ADMIN": 18443, "MLLP": 6661}, group="Interoperability")

app(slug="hapi-fhir", name="HAPI FHIR Server", category="developer", version="8.12.0",
    tagline="FHIR R4 server with a PostgreSQL backend",
    description="The HAPI FHIR JPA starter server with a web tester UI and a FHIR R4 endpoint at /fhir, stored in a bundled PostgreSQL.\n\nLoad Synthea bundles from this store to practise FHIR queries. The endpoint has no authentication beyond the umbrelOS login, so keep it to synthetic data.",
    developer="Smile Digital Health / HAPI FHIR", website="https://hapifhir.io", repo="https://github.com/hapifhir/hapi-fhir-jpaserver-starter",
    support="https://github.com/hapifhir/hapi-fhir-jpaserver-starter/issues",
    icon="https://avatars.githubusercontent.com/hapifhir?s=256",
    main="server", app_port=8080, data_dirs=["db"],
    services={
        "server": {"image": "hapiproject/hapi:v8.12.0-1", "restart": "on-failure", "depends_on": dep_ok(healthy=["db"]),
            "mem_limit": "3g",
            "environment": {"SPRING_DATASOURCE_URL": "jdbc:postgresql://saud-hapi-fhir_db_1:5432/hapi",
                            "SPRING_DATASOURCE_USERNAME": "hapi", "SPRING_DATASOURCE_PASSWORD": "${APP_PASSWORD}",
                            "SPRING_DATASOURCE_DRIVERCLASSNAME": "org.postgresql.Driver",
                            "SPRING_JPA_PROPERTIES_HIBERNATE_DIALECT": "ca.uhn.fhir.jpa.model.dialect.HapiFhirPostgresDialect",
                            "HAPI_FHIR_FHIR_VERSION": "R4",
                            "HAPI_FHIR_SERVER_ADDRESS": "http://${DEVICE_DOMAIN_NAME}:{PORT}/fhir"}},
        "db": pg_service("hapi", "hapi", "hapi")},
    group="Interoperability")

app(slug="fhir-validator", name="FHIR Validator", category="developer", version="1.0.84",
    tagline="Validate FHIR resources against profiles and implementation guides",
    description="The official HL7 FHIR validator with a web interface. Paste or upload a resource, pick the FHIR version and any implementation guide, and see errors and warnings.\n\nImplementation guides are downloaded from packages.fhir.org when first used.",
    developer="HL7 International", website="https://validator.fhir.org", repo="https://github.com/hapifhir/org.hl7.fhir.validator-wrapper",
    support="https://github.com/hapifhir/org.hl7.fhir.validator-wrapper/issues",
    icon=gh("hapifhir/org.hl7.fhir.validator-wrapper", "d4805202a3", "src/jvmMain/resources/static-content/images/fhir-logo.png"),
    main="web", app_port=3500,
    services={"web": {"image": "markiantorno/validator-wrapper:1.0.84", "restart": "on-failure", "mem_limit": "3g"}},
    group="Interoperability")

SYN_JAR_URL = "https://github.com/synthetichealth/synthea/releases/download/v4.0.0/synthea-with-dependencies.jar"
SYN_SHA = "ed43c20ad40ba5c3bc724503a5af032715fe3c491620b766148e7c2361e6ecc1"
app(slug="synthea", name="Synthea", category="developer", version="4.0.0",
    tagline="Synthetic patient generator with a file browser for the output",
    description="Synthea generates realistic but fully synthetic patient records (FHIR R4 bundles and CSV). On each app start it generates a population of 100 patients into the output folder, which you can browse and download here.\n\nThe first start downloads the pinned Synthea 4.0.0 release (about 200 MB) and checks its SHA-256. Restart the app to generate another population.",
    developer="The MITRE Corporation", website="https://synthetichealth.github.io/synthea", repo="https://github.com/synthetichealth/synthea",
    support="https://github.com/synthetichealth/synthea/issues",
    icon="https://avatars.githubusercontent.com/synthetichealth?s=256",
    main="files", app_port=80, data_dirs=["jar", "output", "fb/database", "fb/config"],
    services={
        "fetch": {"image": "curlimages/curl:8.22.0", "user": "1000:1000", "restart": "no",
            "volumes": ["${APP_DATA_DIR}/data/jar:/jar"],
            "entrypoint": ["sh", "-c", f"J=/jar/synthea-4.0.0.jar; if [ ! -f $$J ]; then curl -fL -o $$J.tmp {SYN_JAR_URL} && echo '{SYN_SHA}  '$$J.tmp | sha256sum -c - && mv $$J.tmp $$J; fi"]},
        "generator": {"image": "eclipse-temurin:21-jre", "user": "1000:1000", "restart": "no", "depends_on": dep_ok("fetch"),
            "working_dir": "/output",
            "volumes": ["${APP_DATA_DIR}/data/jar:/jar:ro", "${APP_DATA_DIR}/data/output:/output"],
            "command": ["java", "-Xmx2g", "-jar", "/jar/synthea-4.0.0.jar", "-p", "100",
                        "--exporter.baseDirectory", "/output", "--exporter.fhir.export", "true", "--exporter.csv.export", "true"]},
        "files": {"image": "filebrowser/filebrowser:v2.63.23", "user": "1000:1000", "restart": "on-failure",
            "environment": {"FB_NOAUTH": "true"},
            "volumes": ["${APP_DATA_DIR}/data/output:/srv", "${APP_DATA_DIR}/data/fb/database:/database", "${APP_DATA_DIR}/data/fb/config:/config"]}},
    group="Interoperability")

app(slug="openemr", name="OpenEMR", category="developer", version="8.4.1",
    tagline="Open-source electronic health record for training and sandbox use",
    description="OpenEMR is a full EHR and practice-management system. This package is for training and sandbox use with synthetic patients only.\n\nThe first start sets up the database and takes 5 to 10 minutes. Log in as admin with the password shown in umbrelOS.",
    developer="OpenEMR Foundation", website="https://www.open-emr.org", repo="https://github.com/openemr/openemr",
    support="https://community.open-emr.org", icon=di("openemr"),
    main="web", app_port=80, data_dirs=["sites", "logs", "db"], default_username="admin", default_password=True,
    services={
        "web": {"image": "openemr/openemr:8.4.1", "restart": "on-failure", "depends_on": dep_ok(healthy=["db"]),
            "environment": {"MYSQL_HOST": "saud-openemr_db_1", "MYSQL_ROOT_PASS": "${APP_PASSWORD}", "MYSQL_USER": "openemr",
                            "MYSQL_PASS": "${APP_PASSWORD}", "OE_USER": "admin", "OE_PASS": "${APP_PASSWORD}"},
            "volumes": ["${APP_DATA_DIR}/data/sites:/var/www/localhost/htdocs/openemr/sites", "${APP_DATA_DIR}/data/logs:/var/log"]},
        "db": mariadb_service("openemr", "openemr")},
    no_proxy_auth=True, group="Interoperability")

OMRS_NET = ["openmrs"]
app(slug="openmrs", name="OpenMRS 3", category="developer", version="3.7.1",
    tagline="OpenMRS 3 reference application with demo data",
    description="The OpenMRS 3 reference application (backend, O3 frontend and gateway) with MariaDB. It includes demo patients and is meant for training.\n\nThe first start builds the database and can take 10 to 20 minutes. Log in with admin / Admin123 and change the password.\n\nThe containers run on a private network because the upstream gateway uses the fixed host names frontend and backend.",
    developer="OpenMRS Inc.", website="https://openmrs.org", repo="https://github.com/openmrs/openmrs-distro-referenceapplication",
    support="https://talk.openmrs.org",
    icon=gh("openmrs/openmrs-esm-core", "196e5d3a91", "packages/framework/esm-styleguide/src/logo/openmrs-logo-icon.svg"),
    main="gateway", app_port=80, path="/openmrs/spa/home", data_dirs=["openmrs", "db"],
    default_username="admin", default_password_text="Admin123",
    services={
        "gateway": {"image": "openmrs/openmrs-reference-application-3-gateway:3.7.1", "restart": "on-failure",
            "depends_on": ["frontend", "backend"], "networks": OMRS_NET},
        "frontend": {"image": "openmrs/openmrs-reference-application-3-frontend:3.7.1", "restart": "on-failure",
            "environment": {"SPA_PATH": "/openmrs/spa", "API_URL": "/openmrs", "SPA_CONFIG_URLS": "/openmrs/spa/config-core_demo.json"},
            "networks": OMRS_NET},
        "perms": dict(chown_init("1001:1001", [("openmrs", "/openmrs/data")]), networks=OMRS_NET),
        "backend": {"image": "openmrs/openmrs-reference-application-3-backend:3.7.1", "restart": "on-failure",
            "depends_on": {"perms": {"condition": "service_completed_successfully"}, "db": {"condition": "service_healthy"}},
            "environment": {"OMRS_CONFIG_MODULE_WEB_ADMIN": "true", "OMRS_CONFIG_AUTO_UPDATE_DATABASE": "true",
                            "OMRS_CONFIG_CREATE_TABLES": "true", "OMRS_CONFIG_CONNECTION_SERVER": "db",
                            "OMRS_CONFIG_CONNECTION_DATABASE": "openmrs", "OMRS_CONFIG_CONNECTION_USERNAME": "openmrs",
                            "OMRS_CONFIG_CONNECTION_PASSWORD": "${APP_PASSWORD}"},
            "volumes": ["${APP_DATA_DIR}/data/openmrs:/openmrs/data"], "networks": OMRS_NET},
        "db": dict(mariadb_service("openmrs", "openmrs", image="mariadb:10.11.19"), networks=OMRS_NET)},
    top_networks={"openmrs": {}}, no_proxy_auth=True, group="Interoperability")

# ---------------- Education ----------------
LS_IMG = "martialblog/limesurvey:7.1.2-260917-apache"
app(slug="limesurvey", name="LimeSurvey", category="social", version="7.1.2",
    tagline="Surveys, course evaluations and research questionnaires",
    description="LimeSurvey builds surveys with branching logic, quotas and exports to SPSS, R and CSV. Suited to course evaluations and research questionnaires.\n\nAdmin panel: /admin, user admin, password shown in umbrelOS. Survey links use http://{DOMAIN}:{PORT}.",
    developer="LimeSurvey GmbH", website="https://www.limesurvey.org", repo="https://github.com/martialblog/docker-limesurvey",
    support="https://github.com/martialblog/docker-limesurvey/issues", icon=di("limesurvey"),
    main="web", app_port=8080, path="/admin", data_dirs=["surveys", "db"], default_username="admin", default_password=True,
    services={
        "init": chown_init("www-data:www-data", [("surveys", "/var/www/html/upload/surveys")], image=LS_IMG),
        "web": {"image": LS_IMG, "restart": "on-failure",
            "depends_on": {"init": {"condition": "service_completed_successfully"}, "db": {"condition": "service_healthy"}},
            "environment": {"LISTEN_PORT": "8080", "DB_TYPE": "mysql", "DB_HOST": "saud-limesurvey_db_1", "DB_PORT": "3306",
                            "DB_NAME": "limesurvey", "DB_USERNAME": "limesurvey", "DB_PASSWORD": "${APP_PASSWORD}",
                            "ADMIN_USER": "admin", "ADMIN_NAME": "Administrator", "ADMIN_EMAIL": "admin@example.com",
                            "ADMIN_PASSWORD": "${APP_PASSWORD}", "PUBLIC_URL": "http://${DEVICE_DOMAIN_NAME}:{PORT}",
                            "URL_FORMAT": "path"},
            "volumes": ["${APP_DATA_DIR}/data/surveys:/var/www/html/upload/surveys"]},
        "db": mariadb_service("limesurvey", "limesurvey")},
    no_proxy_auth=True, group="Education")

MOODLE_IMG = "erseco/alpine-moodle:v5.2.3"
app(slug="moodle", name="Moodle", category="social", version="5.2.3",
    tagline="Learning management system with built-in H5P",
    description="Moodle 5.2 on a lightweight Alpine image with PostgreSQL. H5P interactive content is built in (Site administration > H5P).\n\nThe first start installs the database and takes several minutes. Moodle must be opened at http://{DOMAIN}:{PORT}. Log in as admin with the password shown in umbrelOS.",
    developer="Moodle Pty Ltd / erseco", website="https://moodle.org", repo="https://github.com/erseco/alpine-moodle",
    support="https://github.com/erseco/alpine-moodle/issues", icon=di("moodle"),
    main="web", app_port=8080, data_dirs=["moodledata", "db"], default_username="admin", default_password=True,
    services={
        "init": chown_init("nobody:nobody", [("moodledata", "/var/www/moodledata")], image=MOODLE_IMG),
        "web": {"image": MOODLE_IMG, "restart": "on-failure",
            "depends_on": {"init": {"condition": "service_completed_successfully"}, "db": {"condition": "service_healthy"}},
            "environment": {"SITE_URL": "http://${DEVICE_DOMAIN_NAME}:{PORT}", "DB_TYPE": "pgsql", "DB_HOST": "saud-moodle_db_1",
                            "DB_PORT": "5432", "DB_NAME": "moodle", "DB_USER": "moodle", "DB_PASS": "${APP_PASSWORD}",
                            "MOODLE_USERNAME": "admin", "MOODLE_PASSWORD": "${APP_PASSWORD}", "MOODLE_EMAIL": "admin@example.com",
                            "MOODLE_SITENAME": "Umbrel Moodle", "MOODLE_LANGUAGE": "en", "REVERSEPROXY": "false",
                            "SSLPROXY": "false", "AUTO_UPDATE_MOODLE": "false"},
            "volumes": ["${APP_DATA_DIR}/data/moodledata:/var/www/moodledata"]},
        "db": pg_service("moodle", "moodle", "moodle")},
    no_proxy_auth=True, group="Education")

app(slug="h5p", name="H5P", category="social", version="1.0.0",
    tagline="Interactive content (use the H5P built into Moodle)",
    description="H5P has no maintained stand-alone server. It is built into Moodle 4 and later, so this entry is disabled. Install Moodle from this store and use Site administration > H5P.",
    developer="H5P Group", website="https://h5p.org", repo="https://github.com/h5p",
    support="https://h5p.org/forum", icon="https://avatars.githubusercontent.com/h5p?s=256",
    main="web", app_port=8080, disabled=True,
    services={"web": info_page_service("H5P is built into Moodle", "<p>Install Moodle from this store and use <b>Site administration &gt; H5P</b>.</p>")},
    group="Education")

# ---------------- Development ----------------
app(slug="baserow", name="Baserow", category="developer", version="2.3.4",
    tagline="No-code database and spreadsheet-style app builder",
    description="Baserow is a no-code database with a spreadsheet interface, forms and an application builder. This is the all-in-one image with its own PostgreSQL and Redis.\n\nBaserow must be opened at http://{DOMAIN}:{PORT}. Create the first account on launch; it becomes the admin.",
    developer="Baserow", website="https://baserow.io", repo="https://github.com/baserow/baserow",
    support="https://community.baserow.io", icon=di("baserow"),
    main="web", app_port=80, data_dirs=["baserow"],
    services={"web": {"image": "baserow/baserow:2.3.4", "restart": "on-failure", "stop_grace_period": "1m",
        "environment": {"BASEROW_PUBLIC_URL": "http://${DEVICE_DOMAIN_NAME}:{PORT}", "BASEROW_ENABLE_OTEL": "false"},
        "volumes": ["${APP_DATA_DIR}/data/baserow:/baserow/data"]}},
    no_proxy_auth=True, group="Development")

GT_IMG = "glitchtip/glitchtip:6.2.6"
app(slug="glitchtip", name="GlitchTip (Sentry-compatible)", category="developer", version="6.2.6",
    tagline="Error tracking that accepts Sentry SDKs",
    description="GlitchTip receives errors and performance events from any Sentry SDK. It replaces self-hosted Sentry, which needs 20+ containers and at least 16 GB of RAM on its own.\n\nRuns in all-in-one mode (web and worker in one container) with PostgreSQL. Register the first account on launch. Email is written to the container log.",
    developer="Burke Software and Consulting", website="https://glitchtip.com", repo="https://gitlab.com/glitchtip/glitchtip",
    support="https://gitlab.com/glitchtip/glitchtip/-/issues", icon=di("glitchtip"),
    main="web", app_port=8000, data_dirs=["uploads", "db"],
    services={
        "init": chown_init("app:app", [("uploads", "/code/uploads")], image=GT_IMG),
        "web": {"image": GT_IMG, "restart": "on-failure",
            "depends_on": {"init": {"condition": "service_completed_successfully"}, "db": {"condition": "service_healthy"}},
            "environment": {"DATABASE_URL": "postgres://glitchtip:${APP_PASSWORD}@saud-glitchtip_db_1:5432/glitchtip",
                            "SECRET_KEY": "${APP_SEED}", "PORT": "8000", "SERVER_ROLE": "all_in_one",
                            "GLITCHTIP_DOMAIN": "http://${DEVICE_DOMAIN_NAME}:{PORT}", "DEFAULT_FROM_EMAIL": "glitchtip@example.com",
                            "EMAIL_URL": "consolemail://", "ENABLE_USER_REGISTRATION": "true"},
            "volumes": ["${APP_DATA_DIR}/data/uploads:/code/uploads"]},
        "db": pg_service("glitchtip", "glitchtip", "glitchtip")},
    no_proxy_auth=True, group="Development")

app(slug="github-actions-runner", name="GitHub Actions Runner", category="developer", version="2.337.0",
    tagline="Self-hosted GitHub Actions runner (disabled until configured)",
    description="A self-hosted GitHub Actions runner. It has no web interface and needs a repository URL and a registration token, so it is disabled by default.\n\nTo use it: fork the store, fill in RUNNER_REPO_URL and RUNNER_TOKEN in exports.sh, remove disabled: true, and push. The runner can control Docker on your Umbrel, so only connect repositories you trust.",
    developer="myoung34", website="https://github.com/myoung34/docker-github-actions-runner", repo="https://github.com/myoung34/docker-github-actions-runner",
    support="https://github.com/myoung34/docker-github-actions-runner/issues", icon=di("github"),
    main="web", app_port=8080, disabled=True, data_dirs=["work"],
    services={
        "web": info_page_service("GitHub Actions Runner", "<p>The runner has no web interface. Check its logs with Dozzle.</p>"),
        "runner": {"image": "myoung34/github-runner:2.337.0-ubuntu-noble", "restart": "on-failure",
            "environment": {"REPO_URL": "${RUNNER_REPO_URL}", "RUNNER_TOKEN": "${RUNNER_TOKEN}", "RUNNER_NAME": "umbrel",
                            "RUNNER_WORKDIR": "/tmp/runner/work", "LABELS": "umbrel,x64,self-hosted", "RUNNER_SCOPE": "repo"},
            "volumes": ["/var/run/docker.sock:/var/run/docker.sock", "${APP_DATA_DIR}/data/work:/tmp/runner/work"]}},
    exports_extra='export RUNNER_REPO_URL="${RUNNER_REPO_URL:-}"\nexport RUNNER_TOKEN="${RUNNER_TOKEN:-}"\n',
    group="Development")

# Official duplicates (mirrored, disabled)
MIRRORS = ["portainer", "uptime-kuma", "langflow", "grafana", "jupyterlab", "nextcloud", "vikunja", "outline",
           "bookstack", "mattermost", "code-server", "gitea", "forgejo", "minio", "appsmith", "nocodb"]
MIRROR_GROUP = {"portainer": "Operations", "uptime-kuma": "Operations", "grafana": "Operations", "langflow": "AI",
                "jupyterlab": "Analytics", "nextcloud": "Documents", "outline": "Documents", "bookstack": "Documents",
                "vikunja": "Development", "mattermost": "Development", "code-server": "Development", "gitea": "Development",
                "forgejo": "Development", "minio": "Development", "appsmith": "Development", "nocodb": "Development"}
