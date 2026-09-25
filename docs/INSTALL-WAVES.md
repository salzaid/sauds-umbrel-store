# Install waves for a 16 GB Umbrel

RAM figures are rough planning estimates, not measurements. Keep total steady-state use under about 10 GB so umbrelOS and the page cache have room. Stop apps you are not using.

## Wave 1: foundation

Install these first. Dozzle shows the logs of every later install, Netdata shows memory pressure, Backrest protects app data.

| App id | Name | Port | Approx. RAM |
|---|---|---|---|
| `saud-dozzle` | Dozzle | 5401 | 0.1 GB |
| `saud-netdata` | Netdata | 5402 | 0.3 GB |
| `saud-backrest` | Backrest | 5403 | 0.1 GB |
| `saud-postgresql` | PostgreSQL | 5409 | 0.3 GB |

Wave total about 0.8 GB.

## Wave 2: local AI

Load a small model in Lemonade first and confirm the GPU is used (Netdata > GPU) before adding the rest.

| App id | Name | Port | Approx. RAM |
|---|---|---|---|
| `saud-lemonade` | Lemonade Server | 5404 | 1.0 GB |
| `saud-qdrant` | Qdrant | 5407 | 0.3 GB |
| `saud-flowise` | Flowise | 5405 | 0.5 GB |
| `saud-litellm` | LiteLLM Proxy | 5408 | 0.8 GB |

Wave total about 2.6 GB.

## Wave 3: analytics

Metabase and Superset overlap; keep the one you prefer running and stop the other.

| App id | Name | Port | Approx. RAM |
|---|---|---|---|
| `saud-pgadmin` | pgAdmin | 5413 | 0.3 GB |
| `saud-metabase` | Metabase | 5410 | 1.5 GB |
| `saud-duckdb` | DuckDB Lab | 5412 | 0.5 GB |
| `saud-superset` | Apache Superset | 5411 | 1.0 GB |

Wave total about 3.3 GB.

## Wave 4: imaging lab

Each Orthanc app has its own DICOM port (14242 to 14246). Send studies to saud-dicom-deid first, then forward the de-identified copy.

| App id | Name | Port | Approx. RAM |
|---|---|---|---|
| `saud-orthanc-lab-basic` | Orthanc Lab | 5414 | 0.2 GB |
| `saud-orthanc-research-viewer` | Orthanc Research Viewer | 5415 | 0.3 GB |
| `saud-ohif-viewer` | OHIF Viewer | 5417 | 0.3 GB |
| `saud-dicom-deid` | DICOM De-identifier | 5418 | 0.2 GB |
| `saud-orthanc-research-archive` | Orthanc Research Archive | 5416 | 0.5 GB |

Wave total about 1.5 GB.

## Wave 5: interoperability

Generate synthetic patients with Synthea, load them into HAPI FHIR, validate with the FHIR Validator, route messages with OIE.

| App id | Name | Port | Approx. RAM |
|---|---|---|---|
| `saud-synthea` | Synthea | 5424 | 0.2 GB |
| `saud-hapi-fhir` | HAPI FHIR Server | 5422 | 1.5 GB |
| `saud-fhir-validator` | FHIR Validator | 5423 | 1.5 GB |
| `saud-oie` | Open Integration Engine | 5421 | 1.0 GB |

Wave total about 4.2 GB.

## Wave 6: documents and education

Moodle and LimeSurvey must be opened at the umbrel.local address shown in their description.

| App id | Name | Port | Approx. RAM |
|---|---|---|---|
| `saud-hedgedoc` | HedgeDoc | 5420 | 0.3 GB |
| `saud-onlyoffice` | ONLYOFFICE Docs | 5419 | 2.0 GB |
| `saud-limesurvey` | LimeSurvey | 5427 | 0.4 GB |
| `saud-moodle` | Moodle | 5428 | 0.6 GB |

Wave total about 3.3 GB.

## Wave 7: clinical sandboxes and development

OpenEMR and OpenMRS are heavy; run one at a time with synthetic data only.

| App id | Name | Port | Approx. RAM |
|---|---|---|---|
| `saud-openemr` | OpenEMR | 5425 | 0.8 GB |
| `saud-openmrs` | OpenMRS 3 | 5426 | 2.5 GB |
| `saud-baserow` | Baserow | 5430 | 1.5 GB |
| `saud-glitchtip` | GlitchTip (Sentry-compatible) | 5431 | 0.5 GB |

Wave total about 5.3 GB.

## Host ports published outside the Umbrel gateway

| App id | Host ports |
|---|---|
| `saud-orthanc-lab-basic` | 14242 |
| `saud-orthanc-research-viewer` | 14243 |
| `saud-orthanc-research-archive` | 14244 |
| `saud-ohif-viewer` | 14245 |
| `saud-dicom-deid` | 14246 |
| `saud-oie` | 18443, 6661 |

These are DICOM, HL7 MLLP and OIE Administrator ports. They bypass the umbrelOS login, so keep the Umbrel on a trusted network.
