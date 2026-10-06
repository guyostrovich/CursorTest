"""Generate data/archive/news_dump.jsonl: a large file of synthetic regulatory news items.

Nothing in the app reads this file. It exists so course exercises have a big,
realistic-looking dataset to explore. Run from the project root:

    python scripts/generate_archive.py
"""

import json
import random
from datetime import date, timedelta
from pathlib import Path

OUTPUT = Path(__file__).resolve().parent.parent / "data" / "archive" / "news_dump.jsonl"
TARGET_BYTES = 4_000_000
SEED = 2024

REGULATORS = ["FDA", "European Commission", "MDCG", "MHRA", "Health Canada", "TGA", "PMDA"]
ACTIONS = [
    "publishes draft guidance on", "finalises guidance on", "opens consultation on",
    "issues safety communication about", "updates Q&A document on", "announces webinar on",
    "extends comment period for", "releases annual report covering",
]
TOPICS = [
    "cybersecurity for connected devices", "AI-enabled device software", "software as a medical device",
    "post-market surveillance", "unique device identification", "clinical evaluation of implants",
    "quality management systems", "labeling and instructions for use", "electronic submissions",
    "real-world evidence", "recall classification", "notified body capacity", "in vitro diagnostics",
    "cardiac rhythm devices", "robotic surgical systems", "surgical navigation software",
]
SOURCES = ["Regulatory Wire", "MedDevice Daily", "Compliance Brief", "Notified Body Watch", "RA Insider"]
SENTENCES = [
    "The document sets out expectations for manufacturers and explains how the regulator intends to apply them.",
    "Stakeholders have a limited period to submit comments before the text is finalised.",
    "Industry associations welcomed the clarification but asked for a longer transition period.",
    "The change is expected to affect both new submissions and devices already on the market.",
    "Observers note that the approach mirrors developments in other jurisdictions.",
    "Manufacturers are advised to review their technical documentation against the new expectations.",
    "The regulator emphasised that patient safety remains the primary objective.",
    "A summary of the key points is available on the official website.",
    "Further guidance on implementation details is expected later in the year.",
]


def make_item(index: int, rng: random.Random) -> dict:
    """Build one synthetic news item as a dict."""
    published = date(2019, 1, 1) + timedelta(days=rng.randint(0, 2800))
    regulator, topic = rng.choice(REGULATORS), rng.choice(TOPICS)
    headline = f"{regulator} {rng.choice(ACTIONS)} {topic}"
    body = " ".join(rng.sample(SENTENCES, rng.randint(3, 6)))
    return {
        "id": f"news-{index:06d}",
        "headline": headline,
        "date": published.isoformat(),
        "source": rng.choice(SOURCES),
        "jurisdiction": "EU" if regulator in ("European Commission", "MDCG") else regulator,
        "body": f"{headline}. {body}",
    }


def main() -> None:
    """Write JSONL until the file reaches TARGET_BYTES (about 4 MB)."""
    rng = random.Random(SEED)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    written, index = 0, 0
    with OUTPUT.open("w", encoding="utf-8") as handle:
        while written < TARGET_BYTES:
            line = json.dumps(make_item(index, rng)) + "\n"
            handle.write(line)
            written += len(line.encode("utf-8"))
            index += 1
    print(f"Wrote {index} news items ({written / 1_000_000:.1f} MB) to {OUTPUT}")


if __name__ == "__main__":
    main()
