# saud-localai-rocm — LocalAI with AMD ROCm on umbrelOS

Target: RX 7900 XTX (gfx1100). Image: `localai/localai:v4.12.1-gpu-hipblas` (ROCm 7.2.1), digest-pinned.

## Install
1. Copy this whole `saud-localai-rocm` folder into the root of your store repo (next to `umbrel-app-store.yml`).
2. Commit and push to GitHub.
3. In umbrelOS: App Store → your community store → refresh → install **LocalAI (AMD ROCm)**.
4. First start downloads ~4.3 GB plus the ROCm llama.cpp backend. Wait until the web UI opens on port 8794.

This app can sit alongside the official LocalAI app (different ID and port), but do not run both
with models loaded at the same time — they share the same 24 GB of VRAM.

## Load a model on the GPU
In the LocalAI web UI → Models → install a GGUF model (e.g. a 7–14B Q4/Q5 model). In the model's YAML make sure:

```yaml
backend: llama-cpp     # resolves to rocm-llama-cpp
gpu_layers: 999        # offload all layers that fit
f16: true
```

## Prove it is using the GPU
```bash
sudo bash gpu-check.sh
```
Then send a prompt and watch VRAM on the host:
```bash
watch -n1 cat /sys/class/drm/card*/device/mem_info_vram_used
```
VRAM should jump by roughly the model size, and the logs should show layers offloaded to ROCm/HIP.

## Using it from other Umbrel apps
OpenAI base URL: `http://saud-localai-rocm_api_1:8080/v1` (any API key string works unless you set `LOCALAI_API_KEY`).
From your LAN: `http://umbrel.local:8794/v1`.

## Troubleshooting
| Symptom | Fix |
|---|---|
| Container won't start, "no such file /dev/kfd" | amdgpu driver not loaded on host: `ls /dev/kfd`, `lsmod \| grep amdgpu` |
| Permission denied on /dev/kfd or renderD128 | Run `getent group render` and replace `991` in `docker-compose.yml` with that GID, bump the version, reinstall |
| Model runs but VRAM unchanged | Check model YAML has `gpu_layers: 999` and backend is not `cpu-llama-cpp` |
| "invalid device function" / HIP errors | Only for non-7900 cards: uncomment `HSA_OVERRIDE_GFX_VERSION` with your card's value |
| Port 8794 already used by another store app | Change `port:` in `umbrel-app.yml` |

## Notes
- `/v1/*` is whitelisted past the Umbrel login (same as the official app). Set `LOCALAI_API_KEY` if you want a key on the API.
- `seccomp=unconfined` follows AMD's ROCm container guidance; remove it if you prefer tighter isolation and the GPU still works.
- Models and backends are excluded from Umbrel backups (they are large and re-downloadable).
