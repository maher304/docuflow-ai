"""Utilitaires : chargement d'images, formats de fichiers, variables d'environnement."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import numpy as np

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".webp"}
PDF_SUFFIXES = {".pdf"}


def env_flag(name: str, default: bool = False) -> bool:
    """Lire un booléen depuis une variable d'environnement."""
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    return int(raw)


def is_image_path(path: str | Path) -> bool:
    return Path(path).suffix.lower() in IMAGE_SUFFIXES


def is_pdf_path(path: str | Path) -> bool:
    return Path(path).suffix.lower() in PDF_SUFFIXES


@lru_cache(maxsize=1)
def default_device() -> str:
    """Device par défaut : CPU sauf si DOCUFLOW_DEVICE=gpu et CUDA disponible."""
    requested = os.getenv("DOCUFLOW_DEVICE", "cpu").lower()
    if requested != "gpu":
        return "cpu"
    try:
        import torch

        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:  # noqa: BLE001 - torch optionnel
        return "cpu"


def load_image_gray(data: bytes) -> np.ndarray:
    """Charger des octets d'image en niveaux de gris numpy (via OpenCV)."""
    import cv2

    array = np.frombuffer(data, dtype=np.uint8)
    image = cv2.imdecode(array, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError("Image illisible : format non supporté ou fichier corrompu")
    return image


def list_sample_images(directory: str | Path) -> list[Path]:
    """Lister les images d'un dossier (triées, déterministe)."""
    root = Path(directory)
    if not root.exists():
        return []
    return sorted(p for p in root.rglob("*") if p.suffix.lower() in IMAGE_SUFFIXES)
