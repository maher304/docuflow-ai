PYTHON ?= python
PIP ?= pip
UV ?= uv

.PHONY: help install install-dev test test-all lint format bench data clean up down

help:
	@echo "docuflow-ai — cibles disponibles :"
	@echo "  make install     Installer shared + tous les modules (base)"
	@echo "  make install-dev Installer aussi les dépendances de développement"
	@echo "  make test        Lancer les tests unitaires"
	@echo "  make test-all    Lancer tous les tests (y compris slow/integration)"
	@echo "  make lint        Ruff check + format --check"
	@echo "  make format      Ruff format + --fix"
	@echo "  make bench       Exécuter tous les benchmarks -> docs/results.md"
	@echo "  make data        Télécharger les jeux de données publics dans data/"
	@echo "  make up          Démarrer la plateforme complète (docker compose)"
	@echo "  make down        Arrêter la plateforme"
	@echo "  make clean       Nettoyer artifacts, caches et .venv"

install:
	$(PIP) install -e ./shared
	$(PIP) install -e ./modules/01-ocr-pipeline
	$(PIP) install -e ./modules/02-vlm-extraction
	$(PIP) install -e ./modules/03-layout-classification
	$(PIP) install -e ./modules/04-ingestion-platform

install-dev: install
	$(PIP) install -r requirements-dev.txt
	pre-commit install || true

test:
	$(PYTHON) -m pytest -m "not slow and not integration and not e2e"

test-all:
	$(PYTHON) -m pytest

lint:
	ruff check shared modules scripts
	ruff format --check shared modules scripts

format:
	ruff check --fix shared modules scripts
	ruff format shared modules scripts

bench:
	bash scripts/run_all_benchmarks.sh

data:
	bash scripts/download_datasets.sh

up:
	docker compose up --build -d

down:
	docker compose down -v

clean:
	rm -rf .venv .pytest_cache .ruff_cache build dist *.egg-info
	rm -rf modules/*/*.egg-info shared/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
