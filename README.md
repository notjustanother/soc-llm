# SOC-LLM Budget Starter (QLoRA + RAG-ready)

A minimal, **budget-friendly** starter to fine-tune a small LLM (e.g., Qwen2.5/3-7B/8B Instruct or Llama 3.1 8B) as a **SOC copilot** using **QLoRA**.
Designed to work across **Colab** and **Kaggle** using **Hugging Face Hub** as a shared checkpoint store.

## Why this repo?
- Train in **short sessions** on free GPUs (Colab/Kaggle), resuming via HF Hub.
- Output **strict JSON** for SOC workflows (verdicts, TTPs, queries).
- Keep artifacts small via **LoRA adapters**.
- Evaluate quickly on held-out mini tasks.

---

## Quick Start (TL;DR)

1. **Create a new private or public repo on GitHub** and copy this project in.
2. **Create a Hugging Face token** (Write scope) and keep it handy.
3. Open `notebooks/colab_train.ipynb` in **Colab** (File → Open notebook → GitHub).
4. Run the setup cells, enter your `HF_TOKEN`, and start training.
5. After each session, **push LoRA** to HF Hub (`yourname/soc-llm-lora`).
6. Open `notebooks/kaggle_train.ipynb` in **Kaggle** → **Copy & Edit** → Resume training from the same HF repo.
7. Repeat across platforms until done. Use `scripts/eval_soc_json.py` to score held-out tasks.

---

## Project Structure

```
soc-llm-budget-starter/
├─ README.md
├─ requirements.txt
├─ .gitignore
├─ config/
│  ├─ axo.yaml
│  └─ env.example
├─ data/
│  ├─ train.jsonl
│  └─ val.jsonl
├─ notebooks/
│  ├─ colab_train.ipynb
│  └─ kaggle_train.ipynb
├─ scripts/
│  ├─ train_local.sh
│  ├─ push_to_hf.sh
│  └─ eval_soc_json.py
└─ Makefile
```

---

## Training Targets & JSON Schema

Your model should output responses like this (strict JSON):

```json
{
  "task": "analyze_alert",
  "hypothesis": "Possible credential dumping via LSASS memory access.",
  "evidence": ["Sysmon Event ID 10 from lsass.exe handle", "Sigma rule match XYZ"],
  "queries_to_run": [
    {"system":"Splunk","spl":"index=win EventCode=10 process=lsass.exe earliest=-1h"},
    {"system":"Sentinel","kql":"DeviceProcessEvents | where FileName == 'lsass.exe'"}
  ],
  "ttp_mapping": [{"technique_id":"T1003","confidence":0.82}],
  "verdict": "suspicious",
  "next_actions": ["Isolate host", "Dump running processes", "Acquire memory image"]
}
```

Edit `data/train.jsonl` and `data/val.jsonl` to add more examples. Keep them small locally; store larger data elsewhere.

---

## Axolotl Config (QLoRA)

We provide a ready `config/axo.yaml`. Tweak model ID, LoRA ranks, batch sizes, etc.  
**Save often** and **resume** between sessions.

---

## Evaluation

Run `scripts/eval_soc_json.py` to score JSON correctness on held-out examples:
- `verdict` accuracy
- TTP (ATT&CK technique_id) matching
- Schema presence/format

---

## Notes

- Recommended base model: `Qwen/Qwen2.5-7B-Instruct` (default), or swap for `meta-llama/Meta-Llama-3.1-8B-Instruct`.
- Keep context length modest (≤ 2k) on free GPUs.
- Always push checkpoints to HF Hub at the end of each session.
- For privacy-sensitive work, **avoid storing real logs** in public repos. Use private HF repos or mock/synthetic data.

---

## Commands

Local testing (CPU or single GPU):

```bash
pip install -r requirements.txt
# Train (small/local): requires GPU for realistic speed
axolotl train config/axo.yaml

# Push LoRA adapter to HF Hub
axolotl push-lora config/axo.yaml --repo YOUR_NAME/soc-llm-lora --token $HF_TOKEN

# Merge LoRA (optional)
axolotl merge-lora config/axo.yaml --save_safetensors true
```

Kaggle CLI helper (from your machine):

```bash
# Upload dataset / start run
kaggle datasets version -p data/ -m "update data"
kaggle kernels push -p notebooks/
```

---

## Next Steps

- Expand dataset with more incidents (use synthetic augmentation; keep PII out).
- Integrate lightweight RAG (ATT&CK + Sigma) for better reasoning.
- Add tool-calling stubs to generate KQL/SPL and enrichment steps.
