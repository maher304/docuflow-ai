import json
from pathlib import Path

import numpy as np
import pytest
from docuflow_shared import BoundingBox, Invoice, InvoiceLine, OCRBlock, OCRResult
from docuflow_shared.cli import validate_invoice
from docuflow_shared.utils import env_flag, is_image_path, list_sample_images
from pydantic import ValidationError


def test_bounding_box_invalid_order():
    with pytest.raises(ValidationError):
        BoundingBox(x0=10, y0=10, x1=5, y1=20)
    with pytest.raises(ValidationError):
        BoundingBox(x0=10, y0=10, x1=20, y1=5)


def test_ocr_result_mean_confidence():
    result = OCRResult(
        engine="fake",
        text="hello",
        blocks=[
            OCRBlock(text="hello", confidence=0.5),
            OCRBlock(text="world", confidence=1.0),
        ],
    )
    assert result.mean_confidence == 0.75
    assert OCRResult(engine="fake", text="").mean_confidence == 0.0


def test_invoice_currency_normalized():
    inv = Invoice(currency="eur")
    assert inv.currency == "EUR"
    with pytest.raises(ValidationError):
        Invoice(currency="euro")


def test_invoice_lines_sum():
    inv = Invoice(
        total="10.00",
        lines=[
            InvoiceLine(description="a", amount="4.50"),
            InvoiceLine(description="b", amount="5.50"),
            InvoiceLine(description="c"),
        ],
    )
    assert str(inv.lines_sum()) == "10.00"


def test_env_flag_and_image_helpers(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("DOCUFLOW_TEST_FLAG", "true")
    assert env_flag("DOCUFLOW_TEST_FLAG") is True
    assert env_flag("DOCUFLOW_TEST_FLAG_MISSING", default=True) is True
    assert is_image_path("a/b/scan.PNG")
    assert not is_image_path("doc.pdf")


def test_list_sample_images(tmp_path: Path):
    (tmp_path / "b.png").write_bytes(b"x")
    (tmp_path / "a.jpg").write_bytes(b"x")
    (tmp_path / "c.txt").write_bytes(b"x")
    names = [p.name for p in list_sample_images(tmp_path)]
    assert names == ["a.jpg", "b.png"]


def test_load_image_gray_roundtrip():
    import cv2
    from docuflow_shared.utils import load_image_gray

    img = (np.random.default_rng(0).random((32, 48)) * 255).astype(np.uint8)
    ok, buf = cv2.imencode(".png", img)
    assert ok
    loaded = load_image_gray(buf.tobytes())
    assert loaded.shape == (32, 48)

    with pytest.raises(ValueError):
        load_image_gray(b"not-an-image")


def test_validate_invoice_cli_normalizes_output(monkeypatch, capsys):
    monkeypatch.setattr(
        "docuflow_shared.cli._read_json", lambda _: {"currency": "eur", "total": "1.20"}
    )

    assert validate_invoice(Path("invoice.json")) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["valid"] is True
    assert output["invoice"]["currency"] == "EUR"
    assert output["invoice"]["total"] == "1.20"


def test_validate_invoice_cli_reports_invalid_input(monkeypatch, capsys):
    monkeypatch.setattr("docuflow_shared.cli._read_json", lambda _: {"unexpected": True})

    assert validate_invoice(Path("invoice.json")) == 1
    assert json.loads(capsys.readouterr().out)["valid"] is False
