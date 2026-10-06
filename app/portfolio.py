"""Loads our own data: the product portfolio (YAML) and regulatory updates (markdown)."""

from pathlib import Path

import yaml

from app.config import settings
from app.models import Product, Update


def load_products() -> list[Product]:
    """Read data/portfolio.yaml into Product models."""
    raw = yaml.safe_load(settings.portfolio_path.read_text(encoding="utf-8"))
    return [Product(**item) for item in raw["products"]]


def load_updates() -> list[Update]:
    """Read every data/updates/*.md file, newest first."""
    updates = [_read_update(path) for path in settings.updates_dir.glob("*.md")]
    return sorted(updates, key=lambda update: update.date, reverse=True)


def _read_update(path: Path) -> Update:
    """Split a markdown file into its YAML front matter (between --- lines) and body."""
    text = path.read_text(encoding="utf-8")
    _, front_matter, body = text.split("---", 2)
    metadata = yaml.safe_load(front_matter)
    return Update(**metadata, body=body.strip())
