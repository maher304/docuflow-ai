# docuflow-ai

Plateforme open source d'**IA documentaire** : OCR multi-moteurs, extraction structurée
par modèles vision-langage (VLM), analyse de mise en page et ingestion documentaire à
grande échelle.

> **Statut des métriques** : aucun benchmark n'a encore été exécuté dans ce dépôt.
> Tous les chiffres sont marqués **« À exécuter »** jusqu'à l'exécution de
> `make bench` (voir [docs/results.md](docs/results.md)).

## Modules

| Module | Rôle | API |
|---|---|---|
| [`modules/01-ocr-pipeline`](modules/01-ocr-pipeline/) | OCR multi-moteurs (Tesseract, PaddleOCR, docTR) + prétraitement OpenCV | `POST /ocr`, `POST /ocr/batch`, `GET /jobs/{id}` |
| [`modules/02-vlm-extraction`](modules/02-vlm-extraction/) | Extraction structurée de factures par VLM (Qwen2-VL / Florence-2) | `POST /extract/invoice` |
| [`modules/03-layout-classification`](modules/03-layout-classification/) | LayoutLMv3 (labelling) + classification de type de document | `POST /classify`, `POST /layout/label` |
| [`modules/04-ingestion-platform`](modules/04-ingestion-platform/) | Pipeline d'ingestion (Celery), stockage PostgreSQL + pgvector, recherche sémantique | `POST /documents`, `GET /search`, … |

Le schéma d'architecture détaillé est dans [docs/architecture.md](docs/architecture.md).

## Installation

Prérequis : Python 3.11+, Docker (pour la plateforme complète).

```bash
git clone https://github.com/<org>/docuflow-ai.git
cd docuflow-ai
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
make install-dev
```

Configuration : copier `.env.example` vers `.env` et ajuster (moteurs OCR, modèles VLM,
URLs de services). Les dépendances lourdes (Tesseract, PaddleOCR, docTR, torch) sont
optionnelles et activables par extras — voir les README de chaque module.

## Commandes make

```bash
make install     # installer shared + les 4 modules
make install-dev # + pytest, ruff, pre-commit
make test        # tests unitaires (sans dépendances lourdes)
make test-all    # tous les tests
make lint        # ruff check + format
make bench       # benchmarks -> docs/results.md
make data        # télécharger FUNSD / SROIE dans data/
make up          # docker compose up (plateforme complète)
make down        # arrêter la plateforme
```

## Démarrage rapide (API)

```bash
# Module 1 — OCR
uvicorn docuflow_ocr.api.app:app --port 8001 &
curl -X POST "http://localhost:8001/ocr?engine=tesseract&preprocess=true" \
     -F "file=@scan.png"

# Module 2 — Extraction de facture
curl -X POST "http://localhost:8002/extract/invoice" \
     -F "file=@invoice.jpg"

# Module 4 — Plateforme complète
docker compose up --build -d
curl -X POST "http://localhost:8000/documents" -F "file=@invoice.jpg"
curl "http://localhost:8000/search?q=total%20facture"
```

## Benchmarks

```bash
make bench   # CER/WER OCR (SROIE), F1 extraction (CORD/SROIE) -> docs/results.md
```

Les résultats sont écrits automatiquement dans
[docs/results.md](docs/results.md) ; le README n'affiche que des chiffres issus
de ces exécutions (sinon « À exécuter »).

## Licence

MIT — voir [LICENSE](LICENSE).
