#!/usr/bin/env bash
# Run on the Umbrel host:  sudo bash gpu-check.sh
C=saud-localai-rocm_api_1
echo "== Host devices";        ls -l /dev/kfd /dev/dri/render* 2>&1
echo "== Host group IDs";      getent group video render
echo "== Container sees GPU";  sudo docker exec $C sh -c 'ls -l /dev/kfd /dev/dri; id'
echo "== ROCm agents";         sudo docker exec $C sh -c 'rocminfo 2>/dev/null | grep -E "Marketing Name|gfx" | sort -u || echo "rocminfo not available"'
echo "== Capability";          sudo docker exec $C sh -c 'cat /run/localai/capability; echo; env | grep LOCALAI_FORCE'
echo "== Installed backends";  sudo docker exec $C sh -c 'ls /backends'
echo "== Recent GPU log lines"; sudo docker logs --tail 400 $C 2>&1 | grep -Ei 'rocm|hip|gfx|offload|vram|capabil|error' | tail -40
