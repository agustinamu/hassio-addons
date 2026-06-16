"""Interfaz de persistencia. v1 usa LocalJsonStorage; Spoolman se añade después."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import FilamentRecord


class StorageBackend(ABC):
    @abstractmethod
    def list_records(self) -> list[FilamentRecord]: ...

    @abstractmethod
    def get(self, slug: str) -> FilamentRecord | None: ...

    @abstractmethod
    def save(self, record: FilamentRecord) -> None: ...

    @abstractmethod
    def delete(self, slug: str) -> bool: ...
