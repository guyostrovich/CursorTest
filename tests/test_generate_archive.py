"""Tests for the synthetic news archive generator."""

import json
import random
from pathlib import Path

import scripts.generate_archive as archive


def test_make_item_covers_eu_and_other_regulators():
    rng = random.Random(2024)
    seen = set()
    for index in range(80):
        item = archive.make_item(index, rng)
        seen.add(item["jurisdiction"])
        assert item["id"] == f"news-{index:06d}"
        assert item["headline"] in item["body"]
        assert item["source"] in archive.SOURCES
    assert "EU" in seen
    assert seen - {"EU"}


def test_main_stops_once_the_file_is_large_enough(tmp_path, monkeypatch, capsys):
    output = tmp_path / "nested" / "news.jsonl"
    monkeypatch.setattr(archive, "OUTPUT", output)
    monkeypatch.setattr(archive, "TARGET_BYTES", 1200)

    archive.main()

    raw = output.read_bytes()
    lines = raw.decode("utf-8").splitlines()
    assert len(raw) >= 1200
    assert json.loads(lines[0])["id"].startswith("news-")
    message = capsys.readouterr().out
    assert "Wrote" in message
    assert str(output) in message


def test_running_the_file_as_a_script(tmp_path):
    path = Path(archive.__file__)
    source = path.read_text(encoding="utf-8")
    destination = tmp_path / "scripted.jsonl"
    old_output = (
        'OUTPUT = Path(__file__).resolve().parent.parent / "data" / "archive" / "news_dump.jsonl"'
    )
    source = source.replace("TARGET_BYTES = 4_000_000", "TARGET_BYTES = 400", 1)
    source = source.replace(old_output, f"OUTPUT = Path({str(destination)!r})", 1)

    exec(compile(source, str(path), "exec"), {"__name__": "__main__", "__file__": str(path)})

    assert destination.is_file()
    assert destination.stat().st_size >= 400
