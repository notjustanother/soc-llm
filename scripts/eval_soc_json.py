#!/usr/bin/env python3
import json, argparse, os, sys

def load_jsonl(path):
    rows = []
    with open(path) as f:
        for line in f:
            line=line.strip()
            if not line: continue
            rows.append(json.loads(line))
    return rows

def score(gold, pred):
    total = len(gold)
    correct_verdict = 0
    ttp_hits = 0
    for g, p in zip(gold, pred):
        try:
            gjs = json.loads(g["output"])
            pjs = json.loads(p["output"]) if isinstance(p, dict) and "output" in p else p
        except Exception as e:
            continue
        if gjs.get("verdict")==pjs.get("verdict"):
            correct_verdict += 1
        g_ttps = {t.get("technique_id") for t in gjs.get("ttp_mapping",[]) if t.get("technique_id")}
        p_ttps = {t.get("technique_id") for t in pjs.get("ttp_mapping",[]) if t.get("technique_id")}
        if g_ttps & p_ttps:
            ttp_hits += 1
    return {
        "n": total,
        "verdict_acc": round(correct_verdict/total,3) if total else 0.0,
        "ttp_overlap_rate": round(ttp_hits/total,3) if total else 0.0
    }

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", default="data/val.jsonl")
    ap.add_argument("--pred", required=False, help="JSONL with model outputs (one strict JSON per line)")
    args = ap.parse_args()
    gold = load_jsonl(args.gold)
    if args.pred and os.path.exists(args.pred):
        pred = load_jsonl(args.pred)
    else:
        # Placeholder: echo gold as pred to show format
        pred = [json.loads(r["output"]) for r in gold]
    print(json.dumps(score(gold, pred), indent=2))
