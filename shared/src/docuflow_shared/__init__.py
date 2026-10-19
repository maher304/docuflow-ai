"""Schémas et utilitaires communs docuflow-ai."""

from docuflow_shared.logging import configure_logging, get_logger
from docuflow_shared.schemas import (
    BoundingBox,
    DocType,
    ExtractionStatus,
    Invoice,
    InvoiceLine,
    OCRBlock,
    OCRResult,
    PipelineStepName,
    StepStatus,
)

__all__ = [
    "BoundingBox",
    "DocType",
    "ExtractionStatus",
    "Invoice",
    "InvoiceLine",
    "OCRBlock",
    "OCRResult",
    "PipelineStepName",
    "StepStatus",
    "configure_logging",
    "get_logger",
]

__version__ = "0.1.0"
