"""Persistencia en JSON local: un archivo por filamento en data/filaments/."""

from __future__ import annotations

import json
from pathlib import Path

from ..models import FilamentRecord
from .base import StorageBackend

DEFAULT_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "filaments"


class LocalJsonStorage(StorageBackend):
    def __init__(self, data_dir: Path | None = None):
        self.data_dir = data_dir or DEFAULT_DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, slug: str) -> Path:
        return self.data_dir / f"{slug}.json"

    def list_records(self) -> list[FilamentRecord]:
        records = []
        for path in sorted(self.data_dir.glob("*.json")):
            records.append(FilamentRecord.model_validate_json(path.read_text(encoding="utf-8")))
        return records

    def get(self, slug: str) -> FilamentRecord | None:
        path = self._path(slug)
        if not path.exists():
            return None
        return FilamentRecord.model_validate_json(path.read_text(encoding="utf-8"))

    def save(self, record: FilamentRecord) -> None:
        path = self._path(record.slug)
        path.write_text(
            json.dumps(record.model_dump(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def delete(self, slug: str) -> bool:
        path = self._path(slug)
        if path.exists():
            path.unlink()
            return True
        return False
