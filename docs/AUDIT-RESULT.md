# umbrelOS store audit: `saud-umbrel-store`

Apps found: 48 · visible in store: 29 · errors: 0 · warnings: 5 · info: 181

| Severity | Area | Rule | Location | Finding |
|---|---|---|---|---|
| WARNING | install | `compose.restart` | `saud-appsmith/docker-compose.yml [app]` | No restart policy; use `restart: on-failure`. |
| WARNING | install | `compose.host-network` | `saud-portainer/docker-compose.yml [docker]` | network_mode: host bypasses the gateway and port checks. |
| WARNING | sync | `update.non-whitelisted-files` | `saud-code-server/` | ['data/'] are copied on first INSTALL only. On UPDATE, app-script copies just docker-compose.yml, *.template, exports.sh, torrc, hooks/ and umbrel-app.yml, so changes to these files never reach already-installed apps. Generate them from a *.template or a pre-start hook instead. |
| WARNING | sync | `update.non-whitelisted-files` | `saud-outline/` | ['data/', 'settings.env'] are copied on first INSTALL only. On UPDATE, app-script copies just docker-compose.yml, *.template, exports.sh, torrc, hooks/ and umbrel-app.yml, so changes to these files never reach already-installed apps. Generate them from a *.template or a pre-start hook instead. |
| WARNING | sync | `update.non-whitelisted-files` | `saud-portainer/` | ['entrypoint.sh', 'default-password'] are copied on first INSTALL only. On UPDATE, app-script copies just docker-compose.yml, *.template, exports.sh, torrc, hooks/ and umbrel-app.yml, so changes to these files never reach already-installed apps. Generate them from a *.template or a pre-start hook instead. |
| INFO | install | `compose.version-key` | `saud-appsmith/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-appsmith/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `hooks.errors-swallowed` | `saud-appsmith/hooks/` | Hook failures are swallowed (`\|\| true`); a failing hook will not fail the install - test hooks explicitly. |
| INFO | install | `app.disabled` | `saud-appsmith/umbrel-app.yml` | `disabled: true` - hidden from the store. |
| INFO | install | `compose.version-key` | `saud-backrest/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-backrest/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `compose.version-key` | `saud-baserow/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-baserow/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `compose.version-key` | `saud-bookstack/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-bookstack/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `app.disabled` | `saud-bookstack/umbrel-app.yml` | `disabled: true` - hidden from the store. |
| INFO | install | `compose.version-key` | `saud-code-server/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-code-server/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `app.disabled` | `saud-code-server/umbrel-app.yml` | `disabled: true` - hidden from the store. |
| INFO | install | `compose.version-key` | `saud-dicom-deid/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-dicom-deid/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `compose.version-key` | `saud-dify/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-dify/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `app.disabled` | `saud-dify/umbrel-app.yml` | `disabled: true` - hidden from the store. |
| INFO | install | `compose.version-key` | `saud-dozzle/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-dozzle/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `compose.volume.host-system` | `saud-dozzle/docker-compose.yml [web]` | Host system path `/var/run/docker.sock` mounted read-only; intentional for monitoring/Docker access, holds no app data. |
| INFO | install | `compose.version-key` | `saud-duckdb/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-duckdb/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `compose.user` | `saud-duckdb/docker-compose.yml [lab]` | Runs as 1000:100; repo files are chowned 1000:1000 at sync. |
| INFO | install | `compose.version-key` | `saud-fhir-validator/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-fhir-validator/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `compose.version-key` | `saud-flowise/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-flowise/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `compose.version-key` | `saud-forgejo/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-forgejo/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `app.disabled` | `saud-forgejo/umbrel-app.yml` | `disabled: true` - hidden from the store. |
| INFO | install | `compose.version-key` | `saud-gitea/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-gitea/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `app.disabled` | `saud-gitea/umbrel-app.yml` | `disabled: true` - hidden from the store. |
| INFO | install | `compose.version-key` | `saud-github-actions-runner/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-github-actions-runner/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `compose.volume.host-system` | `saud-github-actions-runner/docker-compose.yml [runner]` | Host system path `/var/run/docker.sock` mounted; intentional for monitoring/Docker access, holds no app data. |
| INFO | install | `app.disabled` | `saud-github-actions-runner/umbrel-app.yml` | `disabled: true` - hidden from the store. |
| INFO | install | `compose.version-key` | `saud-glitchtip/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-glitchtip/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `compose.user` | `saud-glitchtip/docker-compose.yml [init]` | Runs as 0:0; repo files are chowned 1000:1000 at sync. |
| INFO | install | `compose.version-key` | `saud-grafana/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-grafana/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `app.disabled` | `saud-grafana/umbrel-app.yml` | `disabled: true` - hidden from the store. |
| INFO | install | `compose.version-key` | `saud-h5p/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-h5p/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `app.disabled` | `saud-h5p/umbrel-app.yml` | `disabled: true` - hidden from the store. |
| INFO | install | `compose.version-key` | `saud-hapi-fhir/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-hapi-fhir/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `compose.version-key` | `saud-hedgedoc/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-hedgedoc/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `compose.config.ok` | `saud-jupyterlab/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `app.disabled` | `saud-jupyterlab/umbrel-app.yml` | `disabled: true` - hidden from the store. |
| INFO | install | `compose.version-key` | `saud-langflow/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-langflow/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `app.disabled` | `saud-langflow/umbrel-app.yml` | `disabled: true` - hidden from the store. |
| INFO | install | `compose.version-key` | `saud-lemonade/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-lemonade/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `compose.user` | `saud-lemonade/docker-compose.yml [init]` | Runs as 0:0; repo files are chowned 1000:1000 at sync. |
| INFO | install | `compose.version-key` | `saud-limesurvey/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-limesurvey/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `compose.user` | `saud-limesurvey/docker-compose.yml [init]` | Runs as 0:0; repo files are chowned 1000:1000 at sync. |
| INFO | install | `compose.version-key` | `saud-litellm/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-litellm/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `compose.version-key` | `saud-mattermost/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-mattermost/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `compose.volume.host-system` | `saud-mattermost/docker-compose.yml [app]` | Host system path `/etc/localtime` mounted read-only; intentional for monitoring/Docker access, holds no app data. |
| INFO | install | `compose.volume.host-system` | `saud-mattermost/docker-compose.yml [db]` | Host system path `/etc/localtime` mounted read-only; intentional for monitoring/Docker access, holds no app data. |
| INFO | install | `app.disabled` | `saud-mattermost/umbrel-app.yml` | `disabled: true` - hidden from the store. |
| INFO | install | `compose.version-key` | `saud-metabase/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-metabase/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `compose.version-key` | `saud-minio/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-minio/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `app.disabled` | `saud-minio/umbrel-app.yml` | `disabled: true` - hidden from the store. |
| INFO | install | `compose.version-key` | `saud-moodle/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-moodle/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `compose.user` | `saud-moodle/docker-compose.yml [init]` | Runs as 0:0; repo files are chowned 1000:1000 at sync. |
| INFO | install | `compose.version-key` | `saud-netdata/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-netdata/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `compose.volume.host-system` | `saud-netdata/docker-compose.yml [web]` | Host system path `/etc/passwd` mounted read-only; intentional for monitoring/Docker access, holds no app data. |
| INFO | install | `compose.volume.host-system` | `saud-netdata/docker-compose.yml [web]` | Host system path `/etc/group` mounted read-only; intentional for monitoring/Docker access, holds no app data. |
| INFO | install | `compose.volume.host-system` | `saud-netdata/docker-compose.yml [web]` | Host system path `/etc/localtime` mounted read-only; intentional for monitoring/Docker access, holds no app data. |
| INFO | install | `compose.volume.host-system` | `saud-netdata/docker-compose.yml [web]` | Host system path `/proc` mounted read-only; intentional for monitoring/Docker access, holds no app data. |
| INFO | install | `compose.volume.host-system` | `saud-netdata/docker-compose.yml [web]` | Host system path `/sys` mounted read-only; intentional for monitoring/Docker access, holds no app data. |
| INFO | install | `compose.volume.host-system` | `saud-netdata/docker-compose.yml [web]` | Host system path `/etc/os-release` mounted read-only; intentional for monitoring/Docker access, holds no app data. |
| INFO | install | `compose.version-key` | `saud-nextcloud/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-nextcloud/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `hooks.errors-swallowed` | `saud-nextcloud/hooks/` | Hook failures are swallowed (`\|\| true`); a failing hook will not fail the install - test hooks explicitly. |
| INFO | install | `app.disabled` | `saud-nextcloud/umbrel-app.yml` | `disabled: true` - hidden from the store. |
| INFO | install | `compose.version-key` | `saud-nocodb/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-nocodb/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `app.disabled` | `saud-nocodb/umbrel-app.yml` | `disabled: true` - hidden from the store. |
| INFO | install | `compose.version-key` | `saud-ohif-viewer/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-ohif-viewer/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `compose.version-key` | `saud-oie/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-oie/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `compose.user` | `saud-oie/docker-compose.yml [init]` | Runs as 0:0; repo files are chowned 1000:1000 at sync. |
| INFO | install | `compose.version-key` | `saud-onlyoffice/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-onlyoffice/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `compose.version-key` | `saud-openemr/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-openemr/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `compose.version-key` | `saud-openmrs/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-openmrs/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `compose.user` | `saud-openmrs/docker-compose.yml [perms]` | Runs as 0:0; repo files are chowned 1000:1000 at sync. |
| INFO | install | `compose.version-key` | `saud-orthanc-lab-basic/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-orthanc-lab-basic/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `compose.version-key` | `saud-orthanc-research-archive/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-orthanc-research-archive/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `compose.version-key` | `saud-orthanc-research-viewer/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-orthanc-research-viewer/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `compose.version-key` | `saud-outline/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-outline/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `hooks.errors-swallowed` | `saud-outline/hooks/` | Hook failures are swallowed (`\|\| true`); a failing hook will not fail the install - test hooks explicitly. |
| INFO | install | `app.disabled` | `saud-outline/umbrel-app.yml` | `disabled: true` - hidden from the store. |
| INFO | install | `compose.version-key` | `saud-pgadmin/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-pgadmin/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `compose.user` | `saud-pgadmin/docker-compose.yml [init]` | Runs as 0:0; repo files are chowned 1000:1000 at sync. |
| INFO | install | `compose.version-key` | `saud-portainer/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-portainer/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `hooks.errors-swallowed` | `saud-portainer/hooks/` | Hook failures are swallowed (`\|\| true`); a failing hook will not fail the install - test hooks explicitly. |
| INFO | install | `app.disabled` | `saud-portainer/umbrel-app.yml` | `disabled: true` - hidden from the store. |
| INFO | install | `compose.version-key` | `saud-postgresql/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-postgresql/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `compose.version-key` | `saud-qdrant/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-qdrant/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `compose.version-key` | `saud-superset/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-superset/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `compose.user` | `saud-superset/docker-compose.yml [perms]` | Runs as 0:0; repo files are chowned 1000:1000 at sync. |
| INFO | install | `compose.version-key` | `saud-synthea/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-synthea/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `compose.version-key` | `saud-uptime-kuma/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-uptime-kuma/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `app.disabled` | `saud-uptime-kuma/umbrel-app.yml` | `disabled: true` - hidden from the store. |
| INFO | install | `compose.version-key` | `saud-vikunja/docker-compose.yml` | Top-level `version:` is obsolete in Compose v2 (harmless). |
| INFO | install | `compose.config.ok` | `saud-vikunja/docker-compose.yml` | `docker compose config` passed with umbrelOS common fragment. |
| INFO | install | `app.disabled` | `saud-vikunja/umbrel-app.yml` | `disabled: true` - hidden from the store. |
| INFO | sync | `sync.model` | `(umbreld)` | umbreld checks every 5 min: compares local HEAD with the remote's default-branch HEAD and, if different, does a fresh shallow clone (depth 1, single default branch) swapped in atomically. Only the DEFAULT branch is ever used. |
| INFO | sync | `sync.gitkeep` | `saud-appsmith/data/app/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-backrest/data/config/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-baserow/data/baserow/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-bookstack/data/config/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-dicom-deid/data/db/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-duckdb/data/home/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-flowise/data/flowise/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-forgejo/data/db/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-gitea/data/db/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-github-actions-runner/data/work/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-glitchtip/data/uploads/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-grafana/data/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-hapi-fhir/data/db/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-hedgedoc/data/uploads/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-jupyterlab/data/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-langflow/data/app/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-lemonade/data/config/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-limesurvey/data/db/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-litellm/data/db/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-mattermost/data/db/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-metabase/data/db/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-minio/data/minio/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-moodle/data/moodledata/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-netdata/data/config/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-nextcloud/data/migration/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-nocodb/data/app/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-ohif-viewer/data/db/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-oie/data/appdata/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-onlyoffice/data/lib/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-openemr/data/logs/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-openmrs/data/db/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-orthanc-lab-basic/data/db/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-orthanc-research-archive/data/pg/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-orthanc-research-viewer/data/db/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-outline/data/app/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-pgadmin/data/pgadmin/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-portainer/data/portainer/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-postgresql/data/db/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-qdrant/data/storage/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-superset/data/home/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-synthea/data/output/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-uptime-kuma/data/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
| INFO | sync | `sync.gitkeep` | `saud-vikunja/data/files/.gitkeep` | umbreld deletes every .gitkeep after cloning; the directory will exist but be empty (that is intended). |
