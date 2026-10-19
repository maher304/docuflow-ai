#!/usr/bin/env bash
# Télécharge les jeux de données publics dans data/ (gitignoré).
# Sources : FUNSD (Hugging Face / GitHub), SROIE (Hugging Face), CORD (Google Drive).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="${ROOT}/data"
mkdir -p "${DATA_DIR}"

PYTHON="${PYTHON:-python}"

echo "[docuflow] Téléchargement des jeux de données dans ${DATA_DIR}"

${PYTHON} - <<'PY'
"""Téléchargement FUNSD / SROIE / CORD via `datasets` (HF) ou URLs publiques."""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path
from urllib.request import urlretrieve

DATA = Path("data")

SOURCES = {
    # Archi OCR public utilisé pour le benchmark CER/WER (module 1).
    "sroie": "https://huggingface.co/datasets/italy-cldr/sroie/resolve/main/data/train-00000-of-00001.parquet",
}


def download_sroie() -> None:
    try:
        from datasets import load_dataset
    except ImportError:
        print("[docuflow] paquet `datasets` absent : pip install datasets", file=sys.stderr)
        raise SystemExit(1)
    ds = load_dataset("italy-cldr/sroie", split="train")
    out = DATA / "sroie"
    out.mkdir(parents=True, exist_ok=True)
    ds.to_json(str(out / "train.jsonl"))
    print(f"[docuflow] SROIE : {len(ds)} exemples -> {out / 'train.jsonl'}")


def download_funsd() -> None:
    """FUNSD : zip officiel hébergé par le dépôt du papier."""
    url = "https://guillaumejaouen.github.io/assets/documents/1_FUNSD.zip"
    archive = DATA / "funsd.zip"
    if not archive.exists():
        print(f"[docuflow] Téléchargement FUNSD : {url}")
        urlretrieve(url, archive)
    target = DATA / "funsd"
    if not target.exists():
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(DATA)
        print(f"[docuflow] FUNSD extrait -> {target}")
    else:
        print(f"[docuflow] FUNSD déjà présent -> {target}")


def main() -> None:
    which = sys.argv[1:] or ["sroie", "funsd"]
    for name in which:
        try:
            {"sroie": download_sroie, "funsd": download_funsd}[name]()
        except Exception as exc:  # noqa: BLE001
            print(f"[docuflow] ÉCHEC {name} : {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
PY

echo "[docuflow] Terminé. Contenu de data/:"
ls -la "${DATA_DIR}" || true
