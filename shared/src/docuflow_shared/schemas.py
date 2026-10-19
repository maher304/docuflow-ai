"""Schémas Pydantic partagés entre les modules docuflow-ai."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictModel(BaseModel):
    """Base model : interdit les champs inconnus (sorties VLM/OCR maîtrisées)."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class DocType(str, Enum):
    """Type de document détecté par le module 3."""

    INVOICE = "invoice"
    RECEIPT = "receipt"
    FORM = "form"
    OTHER = "other"


class ExtractionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    PARTIAL = "partial"


class PipelineStepName(str, Enum):
    """Étapes du pipeline d'ingestion (module 4)."""

    CLASSIFY = "classify"
    OCR = "ocr"
    EXTRACT = "extract"
    VALIDATE = "validate"
    STORE = "store"


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    RETRYING = "retrying"
    SKIPPED = "skipped"


class BoundingBox(StrictModel):
    """Boîte englobante normalisée : pixels ou unités relatives [0,1]."""

    x0: float
    y0: float
    x1: float
    y1: float

    @field_validator("x1")
    @classmethod
    def _x1_after_x0(cls, v: float, info) -> float:
        x0 = info.data.get("x0")
        if x0 is not None and v < x0:
            raise ValueError("x1 doit être >= x0")
        return v

    @field_validator("y1")
    @classmethod
    def _y1_after_y0(cls, v: float, info) -> float:
        y0 = info.data.get("y0")
        if y0 is not None and v < y0:
            raise ValueError("y1 doit être >= y0")
        return v


class OCRBlock(StrictModel):
    """Un bloc de texte reconnu par un moteur OCR."""

    text: str
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] = 1.0
    box: BoundingBox | None = None


class OCRResult(StrictModel):
    """Sortie normalisée d'un moteur OCR (interface commune)."""

    engine: str
    text: str
    blocks: list[OCRBlock] = Field(default_factory=list)
    preprocessed: bool = False
    image_width: int | None = None
    image_height: int | None = None

    @property
    def mean_confidence(self) -> float:
        if not self.blocks:
            return 0.0
        return sum(b.confidence for b in self.blocks) / len(self.blocks)


class InvoiceLine(StrictModel):
    """Ligne de facture extraite."""

    description: str
    quantity: float | None = None
    unit_price: Decimal | None = None
    amount: Decimal | None = None


class Invoice(StrictModel):
    """Schéma structuré d'une facture (sortie du module 2)."""

    vendor: str | None = None
    invoice_date: date | None = None
    invoice_number: str | None = None
    currency: str | None = None
    total: Decimal | None = None
    lines: list[InvoiceLine] = Field(default_factory=list)

    @field_validator("currency")
    @classmethod
    def _upper_currency(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.upper()
        if len(v) != 3 or not v.isalpha():
            raise ValueError("devise attendue au format ISO 4217 (3 lettres)")
        return v

    def lines_sum(self) -> Decimal:
        total = Decimal("0")
        for line in self.lines:
            if line.amount is not None:
                total += line.amount
        return total
