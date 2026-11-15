PYTHON ?= python
PIP ?= pip
UV ?= uv

.PHONY: help install install-dev test test-all lint format clean

help:
	@echo "docuflow-ai — cibles disponibles :"
	@echo "  make install     Installer le paquet partagé"
	@echo "  make install-dev Installer aussi les dépendances de développement"
	@echo "  make test        Lancer les tests unitaires"
	@echo "  make test-all    Lancer tous les tests (y compris slow/integration)"
	@echo "  make lint        Ruff check + format --check"
	@echo "  make format      Ruff format + --fix"
	@echo "  make clean       Nettoyer artifacts, caches et .venv"

install:
	$(PIP) install -e ./shared

install-dev: install
	$(PIP) install -r requirements-dev.txt
	pre-commit install || true

test:
	$(PYTHON) -m pytest -m "not slow and not integration and not e2e"

test-all:
	$(PYTHON) -m pytest

lint:
	ruff check shared
	ruff format --check shared

format:
	ruff check --fix shared
	ruff format shared

clean:
	rm -rf .venv .pytest_cache .ruff_cache build dist *.egg-info
	rm -rf modules/*/*.egg-info shared/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
