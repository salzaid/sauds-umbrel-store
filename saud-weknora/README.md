# saud-weknora (WeKnora v0.8.3 for umbrelOS)

## Add to the store
1. Copy the `saud-weknora` folder into the root of your store repo (next to `umbrel-app-store.yml`).
2. Commit and push:
   ```bash
   git add saud-weknora
   git commit -m "Add WeKnora 0.8.3"
   git push
   ```
3. In umbrelOS: App Store > ... > Community App Stores > your Saud store > refresh, then install WeKnora.

## First run
- First boot takes 2-4 minutes (database migrations, document reader warm-up). The app opens on port 5449.
- Register your account in WeKnora. Then, to stop anyone else registering, edit
  `DISABLE_REGISTRATION: "true"` in `docker-compose.yml`, bump `version` in `umbrel-app.yml` (e.g. `0.8.3-1`), push, and update the app.
- Settings > Models: add a chat model and an embedding model.
  - Umbrel Ollama: Base URL `http://ollama_ollama_1:11434` (pull e.g. `qwen2.5` and `bge-m3` in Ollama first).
  - Any OpenAI-compatible endpoint (Lemonade, OpenRouter, OpenAI) also works. If it is another container on the Umbrel, add its hostname to `SSRF_WHITELIST_EXTRA`.

## Troubleshooting (SSH into Umbrel)
```bash
sudo docker logs saud-weknora_app_1 --tail 100
sudo docker logs saud-weknora_docreader_1 --tail 100
sudo docker ps --filter name=saud-weknora
```

## Not included
Neo4j graph, Langfuse tracing, MinIO/S3, Qdrant/Milvus, and the Docker code sandbox for the agent.
