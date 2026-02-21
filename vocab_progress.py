import json
import os
import random
import re


def parse_vocab_line(line: str):
    line = line.strip()
    if not line:
        return None
    parts = line.split("\t")
    if len(parts) >= 3:
        idx, ko, ja = parts[0].strip(), parts[1].strip(), parts[2].strip()
    else:
        parts = re.split(r"\s+", line, maxsplit=2)
        if len(parts) < 3:
            return None
        idx, ko, ja = parts[0].strip(), parts[1].strip(), parts[2].strip()

    if idx.isdigit():
        return int(idx), ko, ja
    return None, ko, ja


def load_vocab(path: str):
    vocab = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            parsed = parse_vocab_line(raw)
            if not parsed:
                continue
            idx, ko, ja = parsed
            if not ko or not ja:
                continue
            vocab.append({"id": idx, "ko": ko, "ja": ja})
    if not vocab:
        raise ValueError("語彙が読み込めませんでした（区切りがタブ/スペースで '番号 韓国語 日本語' になってるか確認）")
    return vocab


def progress_path_for(vocab_path: str) -> str:
    base = os.path.splitext(os.path.basename(vocab_path))[0]
    return f"progress_{base}.json"


def load_progress(p_path: str, vocab):
    default = {v["ko"]: {"seen": 0, "correct": 0, "wrong": 0} for v in vocab}
    if not os.path.exists(p_path):
        return default
    try:
        with open(p_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k in default.keys():
            if k in data and isinstance(data[k], dict):
                for fld in ["seen", "correct", "wrong"]:
                    if fld in data[k] and isinstance(data[k][fld], int):
                        default[k][fld] = data[k][fld]
        return default
    except Exception:
        return default


def save_progress(p_path: str, prog: dict):
    with open(p_path, "w", encoding="utf-8") as f:
        json.dump(prog, f, ensure_ascii=False, indent=2)


def difficulty_score(entry_prog):
    seen = entry_prog["seen"]
    wrong = entry_prog["wrong"]
    correct = entry_prog["correct"]
    return (1 + wrong * 3) + (0 if seen == 0 else max(0, (wrong - correct)))


def weighted_choice(vocab, prog):
    weights = []
    for v in vocab:
        p = prog[v["ko"]]
        w = difficulty_score(p)
        weights.append(max(1, w))
    return random.choices(vocab, weights=weights, k=1)[0]