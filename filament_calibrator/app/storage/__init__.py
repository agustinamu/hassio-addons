"""Backends de persistencia para los registros de filamento."""

from .base import StorageBackend
from .local import LocalJsonStorage

__all__ = ["StorageBackend", "LocalJsonStorage"]
