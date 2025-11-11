#!/usr/bin/env bash
set -euo pipefail
export HF_TOKEN="${HF_TOKEN:-}"
axolotl train config/axo.yaml
