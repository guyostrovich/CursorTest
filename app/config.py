"""Settings for Regulatory Radar, read from environment variables and .env."""

import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_dotenv(path: Path = PROJECT_ROOT / ".env") -> None:
    """Copy KEY=VALUE lines from a .env file into the environment (existing values win)."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


@dataclass(frozen=True)
class Settings:
    """All runtime configuration in one place."""

    openfda_mode: str  # "fixture" (saved sample data) or "live" (api.fda.gov)
    openfda_api_key: str
    openfda_base_url: str
    openfda_timeout: float
    fixtures_dir: Path
    portfolio_path: Path
    updates_dir: Path


def get_settings() -> Settings:
    """Build Settings from the environment, after loading .env."""
    load_dotenv()
    return Settings(
        openfda_mode=os.getenv("OPENFDA_MODE", "fixture").strip().lower(),
        openfda_api_key=os.getenv("OPENFDA_API_KEY", ""),
        openfda_base_url=os.getenv("OPENFDA_BASE_URL", "https://api.fda.gov"),
        openfda_timeout=float(os.getenv("OPENFDA_TIMEOUT_SECONDS", "10")),
        fixtures_dir=PROJECT_ROOT / "data" / "fixtures",
        portfolio_path=PROJECT_ROOT / "data" / "portfolio.yaml",
        updates_dir=PROJECT_ROOT / "data" / "updates",
    )


settings = get_settings()
