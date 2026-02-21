from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
	from kiwipiepy import Kiwi

	KIWI_AVAILABLE = True
except Exception:
	KIWI_AVAILABLE = False
	Kiwi = None  # type: ignore


POS_MAPPING = {
	"NNG": "Noun",
	"NNP": "Noun",
	"NNB": "Noun",
	"NP": "Pronoun",
	"NR": "Numeral",
	"VV": "Verb",
	"VA": "Adjective",
	"VX": "AuxVerb",
	"VCP": "Copula",
	"VCN": "NegCopula",
	"MAG": "Adverb",
	"MAJ": "Adverb",
	"MM": "Determiner",
	"IC": "Interjection",
	"JKS": "Particle",
	"JKC": "Particle",
	"JKG": "Particle",
	"JKO": "Particle",
	"JKB": "Particle",
	"JKV": "Particle",
	"JKQ": "Particle",
	"JX": "Particle",
	"JC": "Conjunction",
}


@dataclass
class VocabRow:
	id: str
	ko: str
	ja: str


@dataclass
class TaggedRow:
	id: str
	ko: str
	ja: str
	pos: str
	pos_tag: str
	lemma: str


def parse_vocab_tsv(path: Path) -> list[VocabRow]:
	rows: list[VocabRow] = []
	with path.open("r", encoding="utf-8") as f:
		reader = csv.reader(f, delimiter="\t")
		for raw in reader:
			if not raw:
				continue
			if len(raw) < 3:
				continue
			first = (raw[0] or "").strip()
			ko = (raw[1] or "").strip()
			ja = (raw[2] or "").strip()
			if not ko or not ja:
				continue

			if first.lower() in {"no", "no.", "id"}:
				continue

			rows.append(VocabRow(id=first, ko=ko, ja=ja))
	return rows


def heuristic_pos(word: str) -> tuple[str, str, str]:
	w = word.strip()
	if not w:
		return "Unknown", "UNK", w
	if w.endswith("다"):
		return "Predicate", "PRED", w
	if w.endswith("히") or w.endswith("게"):
		return "Adverb", "HEUR", w
	return "Noun", "HEUR", w


def kiwi_pos(word: str, kiwi: Kiwi) -> tuple[str, str, str]:  # type: ignore[name-defined]
	tokens = kiwi.tokenize(word)
	if not tokens:
		return "Unknown", "UNK", word

	token = tokens[0]
	tag = token.tag
	lemma = getattr(token, "lemma", token.form)
	if not lemma:
		lemma = word
	pos = POS_MAPPING.get(tag, tag) or "Unknown"
	return pos, tag, lemma


def tag_rows(rows: Iterable[VocabRow], kiwi: Kiwi | None) -> list[TaggedRow]:  # type: ignore[name-defined]
	tagged: list[TaggedRow] = []
	for r in rows:
		if kiwi is not None:
			pos, tag, lemma = kiwi_pos(r.ko, kiwi)
		else:
			pos, tag, lemma = heuristic_pos(r.ko)
		tagged.append(TaggedRow(id=r.id, ko=r.ko, ja=r.ja, pos=pos, pos_tag=tag, lemma=lemma))
	return tagged


def write_tagged_tsv(path: Path, rows: Iterable[TaggedRow]) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	with path.open("w", encoding="utf-8", newline="") as f:
		writer = csv.writer(f, delimiter="\t")
		writer.writerow(["id", "ko", "ja", "pos", "pos_tag", "lemma"])
		for r in rows:
			writer.writerow([r.id, r.ko, r.ja, r.pos, r.pos_tag, r.lemma])


def build_one_file(input_path: Path, output_path: Path, kiwi: Kiwi | None) -> tuple[int, int]:  # type: ignore[name-defined]
	rows = parse_vocab_tsv(input_path)
	tagged = tag_rows(rows, kiwi)
	write_tagged_tsv(output_path, tagged)
	unknown_count = sum(1 for r in tagged if r.pos == "Unknown")
	return len(tagged), unknown_count


def resolve_project_root() -> Path:
	return Path(__file__).resolve().parents[1]


def main() -> None:
	project_root = resolve_project_root()
	default_vocab_dir = project_root / "data" / "vocab"

	parser = argparse.ArgumentParser(description="Create POS-tagged DB TSV from vocab TSV files.")
	parser.add_argument("--input", type=Path, help="Input vocab TSV path")
	parser.add_argument("--output", type=Path, help="Output DB TSV path")
	parser.add_argument("--all", action="store_true", help="Process all TSV files in data/vocab")
	args = parser.parse_args()

	kiwi = Kiwi() if KIWI_AVAILABLE else None  # type: ignore[operator]
	if kiwi is None:
		print("[WARN] kiwipiepy が見つからないため、簡易ヒューリスティックで品詞を付与します。")

	targets: list[tuple[Path, Path]] = []

	if args.all:
		for p in sorted(default_vocab_dir.glob("*.tsv")):
			if p.name.endswith("_db.tsv"):
				continue
			out = p.with_name(p.stem + "_db.tsv")
			targets.append((p, out))
	else:
		input_path = args.input or (default_vocab_dir / "syokyuu_hanguk.tsv")
		output_path = args.output or input_path.with_name(input_path.stem + "_db.tsv")
		targets.append((input_path, output_path))

	for input_path, output_path in targets:
		if not input_path.exists():
			print(f"[SKIP] 入力ファイルがありません: {input_path}")
			continue
		total, unknown = build_one_file(input_path, output_path, kiwi)
		print(f"[OK] {input_path.name} -> {output_path.name} | rows={total}, unknown={unknown}")


if __name__ == "__main__":
	main()
