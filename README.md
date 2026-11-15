# docuflow-ai

# DocuFlow AI

Socle Python open source pour les flux documentaires : schémas Pydantic partagés, utilitaires et outils de validation. Le dépôt contient actuellement le paquet `docuflow-shared` ; les services OCR, VLM, classification, ingestion, API et benchmarks annoncés dans d'anciennes versions de la documentation ne sont pas encore implémentés.

## Prérequis

- Python 3.11 ou plus récent
- `make` facultatif (les commandes Python fonctionnent aussi directement sous Windows)

## Installation

```bash
python -m venv .venv
# Linux/macOS : source .venv/bin/activate
# Windows PowerShell : .venv\Scripts\Activate.ps1
python -m pip install -e ./shared
python -m pip install -r requirements-dev.txt
```

## Valider une facture JSON

Le CLI valide les champs avec le schéma `Invoice`, normalise la devise et les dates, puis émet le document normalisé en JSON. Il retourne le code 0 en cas de succès et 1 si le document est invalide ou illisible.

```bash
docuflow validate-invoice invoice.json
# Sans installation du CLI :
python -m docuflow_shared.cli validate-invoice invoice.json
```

Exemple de `invoice.json` :

```json
{
  "vendor": "Acme",
  "invoice_date": "2026-05-12",
  "invoice_number": "INV-42",
  "currency": "eur",
  "total": "12.50",
  "lines": [{"description": "Service", "quantity": 1, "amount": "12.50"}]
}
```

Les champs inconnus sont refusés. Pour contrôler une facture :

```python
from docuflow_shared import Invoice

invoice = Invoice.model_validate_json(open("invoice.json", encoding="utf-8").read())
print(invoice.lines_sum())
```

## Développement

```bash
make install-dev  # paquet partagé et outils de développement
make test         # tests unitaires
make lint         # Ruff : lint et format
```

Ou utilisez `python -m pytest` et `ruff check shared` directement. La suite de tests ne requiert pas de téléchargement de modèles ni de services externes.

## État du projet

Les schémas disponibles comprennent les types de documents, statuts de pipeline, boîtes, résultats OCR et factures. Les dépendances de modèles lourds restent optionnelles et ne sont pas nécessaires pour les fonctions présentes. Les anciennes commandes `bench`, `data`, `up` et `down` ont été retirées tant que les modules et configurations correspondants ne sont pas dans le dépôt.

## Licence

MIT — voir [LICENSE](LICENSE).
