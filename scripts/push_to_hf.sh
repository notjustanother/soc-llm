#!/usr/bin/env bash
set -euo pipefail
: "${HF_TOKEN:?Set HF_TOKEN}"
: "${HF_REPO:?Set HF_REPO, e.g., yourname/soc-llm-lora}"
axolotl push-lora config/axo.yaml --repo "$HF_REPO" --token "$HF_TOKEN"
