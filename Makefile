SHELL:=/bin/bash

install:
	pip install -r requirements.txt

train:
	./scripts/train_local.sh

push:
	./scripts/push_to_hf.sh

eval:
	python scripts/eval_soc_json.py --gold data/val.jsonl
