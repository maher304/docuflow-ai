"""Command-line tools for validating DocuFlow documents."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from docuflow_shared.schemas import Invoice


def _read_json(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"JSON invalide ligne {exc.lineno}, colonne {exc.colno}: {exc.msg}"
        ) from exc
    except OSError as exc:
        raise ValueError(f"Impossible de lire {path}: {exc}") from exc


def validate_invoice(path: Path) -> int:
    try:
        invoice = Invoice.model_validate(_read_json(path))
    except ValidationError as exc:
        print(
            json.dumps(
                {
                    "valid": False,
                    "errors": exc.errors(include_url=False, include_context=False),
                },
                ensure_ascii=False,
            )
        )
        return 1
    except ValueError as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False))
        return 1

    print(
        json.dumps({"valid": True, "invoice": invoice.model_dump(mode="json")}, ensure_ascii=False)
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="docuflow", description="Outils DocuFlow AI")
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser(
        "validate-invoice", help="valider et normaliser une facture JSON"
    )
    validate.add_argument("file", type=Path, help="chemin vers le fichier JSON")
    args = parser.parse_args()
    if args.command == "validate-invoice":
        return validate_invoice(args.file)
    return 2


if __name__ == "__main__":
    sys.exit(main())
